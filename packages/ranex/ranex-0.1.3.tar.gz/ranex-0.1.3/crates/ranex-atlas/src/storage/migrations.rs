//! Database schema migrations.
//!
//! Handles upgrading the database schema between versions.
//!
//! ## Migration Policy
//!
//! - **Backwards compatible**: Schema changes should be additive where possible.
//! - **Minimum version**: Databases older than `MIN_SUPPORTED_VERSION` require rebuild.
//! - **Forward compatible**: Unknown future versions trigger warnings but don't fail.
//! - **Atomic**: Each migration runs in a transaction; failures roll back cleanly.

use crate::storage::schema::{MIN_SUPPORTED_VERSION, SCHEMA_VERSION};
use ranex_core::AtlasError;
use rusqlite::{Connection, OptionalExtension};
use tracing::{debug, error, info, warn};

/// Result of checking schema compatibility.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SchemaCompatibility {
    /// Schema is compatible and up to date.
    UpToDate,
    /// Schema needs migration from old_version to new_version.
    NeedsMigration { from: u32, to: u32 },
    /// Schema is too old and must be rebuilt (run `ranex clean && ranex scan`).
    TooOld { version: u32, min_supported: u32 },
    /// Schema is from a newer version (user should upgrade ranex).
    TooNew { version: u32, current: u32 },
    /// Schema is corrupted or missing version info.
    Corrupted,
}

/// Check schema compatibility without making changes.
pub fn check_compatibility(conn: &Connection) -> SchemaCompatibility {
    let current = match get_schema_version(conn) {
        Ok(v) => v,
        Err(_) => return SchemaCompatibility::Corrupted,
    };

    if current == 0 {
        // Fresh database, will be created at current version
        return SchemaCompatibility::UpToDate;
    }

    if current < MIN_SUPPORTED_VERSION {
        return SchemaCompatibility::TooOld {
            version: current,
            min_supported: MIN_SUPPORTED_VERSION,
        };
    }

    if current > SCHEMA_VERSION {
        return SchemaCompatibility::TooNew {
            version: current,
            current: SCHEMA_VERSION,
        };
    }

    if current < SCHEMA_VERSION {
        return SchemaCompatibility::NeedsMigration {
            from: current,
            to: SCHEMA_VERSION,
        };
    }

    SchemaCompatibility::UpToDate
}

/// Run all pending migrations.
///
/// Returns an error if:
/// - Schema is too old (requires rebuild)
/// - Schema is from a future version (requires upgrade)
/// - Migration fails
pub fn run_migrations(conn: &Connection) -> Result<(), AtlasError> {
    match check_compatibility(conn) {
        SchemaCompatibility::UpToDate => {
            debug!(version = SCHEMA_VERSION, "Schema is up to date");
            return Ok(());
        }
        SchemaCompatibility::TooOld {
            version,
            min_supported,
        } => {
            error!(
                version = version,
                min_supported = min_supported,
                "Database schema is too old. Run `ranex clean && ranex scan` to rebuild."
            );
            return Err(AtlasError::Migration {
                from_version: version,
                to_version: SCHEMA_VERSION,
                message: format!(
                    "Schema version {} is below minimum supported version {}. \
                     Please run `ranex clean && ranex scan` to rebuild the index.",
                    version, min_supported
                ),
            });
        }
        SchemaCompatibility::TooNew { version, current } => {
            warn!(
                db_version = version,
                lib_version = current,
                "Database was created by a newer version of Ranex. \
                 Some features may not work correctly. Consider upgrading."
            );
            // Allow reading but warn - don't fail
            return Ok(());
        }
        SchemaCompatibility::Corrupted => {
            error!("Database schema is corrupted. Run `ranex clean && ranex scan` to rebuild.");
            return Err(AtlasError::Database {
                operation: "check_schema".to_string(),
                message: "Schema version table is corrupted or missing".to_string(),
            });
        }
        SchemaCompatibility::NeedsMigration { from, to } => {
            info!(from = from, to = to, "Running schema migrations");
        }
    }

    let current_version = get_schema_version(conn)?;

    // Run migrations in order
    for version in (current_version + 1)..=SCHEMA_VERSION {
        run_migration(conn, version)?;
        set_schema_version(conn, version)?;
    }

    info!(version = SCHEMA_VERSION, "Migrations complete");
    Ok(())
}

fn column_exists(conn: &Connection, table: &str, column: &str) -> Result<bool, AtlasError> {
    let pragma = format!("PRAGMA table_info({})", table);
    let mut stmt = conn.prepare(&pragma).map_err(|e| AtlasError::Database {
        operation: "pragma_table_info".to_string(),
        message: e.to_string(),
    })?;

    let mut rows = stmt.query([]).map_err(|e| AtlasError::Database {
        operation: "pragma_table_info_query".to_string(),
        message: e.to_string(),
    })?;

    while let Some(row) = rows.next().map_err(|e| AtlasError::Database {
        operation: "pragma_table_info_next".to_string(),
        message: e.to_string(),
    })? {
        let name: String = row.get(1).map_err(|e| AtlasError::Database {
            operation: "pragma_table_info_get".to_string(),
            message: e.to_string(),
        })?;

        if name == column {
            return Ok(true);
        }
    }

    Ok(false)
}

/// Get current schema version from database.
fn get_schema_version(conn: &Connection) -> Result<u32, AtlasError> {
    // Check if schema_version table exists
    let exists: bool = conn
        .query_row(
            "SELECT COUNT(*) > 0 FROM sqlite_master WHERE type='table' AND name='schema_version'",
            [],
            |row| row.get(0),
        )
        .unwrap_or(false);

    if !exists {
        return Ok(0);
    }

    // Baseline: schema_version table can contain multiple rows.
    // Use MAX(version) as the best estimate from this table alone.
    let table_version: u32 = conn
        .query_row(
        "SELECT COALESCE(MAX(version), 0) FROM schema_version",
        [],
        |row| row.get::<_, u32>(0),
    )
    .map_err(|e| AtlasError::Database {
        operation: "get_version".to_string(),
        message: e.to_string(),
    })
    .unwrap_or(0);

    // Prefer metadata.schema_version if present, but never return a version higher than
    // what schema_version claims. This prevents false "up to date" reports when
    // schema_version was polluted with a higher version row.
    let metadata_exists: bool = conn
        .query_row(
            "SELECT COUNT(*) > 0 FROM sqlite_master WHERE type='table' AND name='metadata'",
            [],
            |row| row.get(0),
        )
        .unwrap_or(false);

    if metadata_exists {
        let schema_version_str: Option<String> = conn
            .query_row(
                "SELECT value FROM metadata WHERE key = 'schema_version'",
                [],
                |row| row.get(0),
            )
            .optional()
            .map_err(|e: rusqlite::Error| AtlasError::Database {
                operation: "get_version_metadata".to_string(),
                message: e.to_string(),
            })?;

        if let Some(v) = schema_version_str
            && let Ok(metadata_version) = v.parse::<u32>()
            && metadata_version > 0
        {
            if metadata_version != table_version {
                warn!(
                    metadata_version,
                    table_version,
                    "Schema version mismatch between metadata and schema_version table"
                );
            }
            return Ok(std::cmp::min(metadata_version, table_version));
        }
    }

    Ok(table_version)
}

/// Set schema version in database.
fn set_schema_version(conn: &Connection, version: u32) -> Result<(), AtlasError> {
    conn.execute("DELETE FROM schema_version", [])
        .map_err(|e| AtlasError::Database {
            operation: "set_version".to_string(),
            message: e.to_string(),
        })?;

    conn.execute(
        "INSERT INTO schema_version (version) VALUES (?1)",
        [version],
    )
    .map_err(|e| AtlasError::Database {
        operation: "set_version".to_string(),
        message: e.to_string(),
    })?;

    // Also update metadata table
    conn.execute(
        "INSERT OR REPLACE INTO metadata (key, value, updated_at) VALUES ('schema_version', ?1, datetime('now'))",
        [version.to_string()],
    )
    .map_err(|e| AtlasError::Database {
        operation: "set_metadata".to_string(),
        message: e.to_string(),
    })?;

    Ok(())
}

/// Run a specific migration.
fn run_migration(conn: &Connection, version: u32) -> Result<(), AtlasError> {
    debug!(version = version, "Running migration");

    match version {
        1 => migration_v1(conn),
        2 => migration_v2(conn),
        3 => migration_v3(conn),
        4 => migration_v4(conn),
        5 => migration_v5(conn),
        6 => migration_v6(conn),
        7 => migration_v7(conn),
        8 => migration_v8(conn),
        9 => migration_v9(conn),
        _ => {
            warn!(version = version, "Unknown migration version - skipping");
            Ok(())
        }
    }
}

/// Migration to version 1 (initial schema).
///
/// This is a no-op since version 1 is created by Schema::create_tables().
fn migration_v1(_conn: &Connection) -> Result<(), AtlasError> {
    // Initial schema is created by Schema::create_tables()
    // This migration exists for future incremental updates
    Ok(())
}

/// Migration to version 2: Add git commit tracking for staleness detection.
///
/// Adds columns:
/// - `scan_runs.git_commit`: Git HEAD hash at scan time
/// - `scan_runs.git_branch`: Git branch name at scan time
fn migration_v2(conn: &Connection) -> Result<(), AtlasError> {
    // Add git_commit column to scan_runs
    // Note: SQLite allows adding columns but they'll be NULL for existing rows
    conn.execute("ALTER TABLE scan_runs ADD COLUMN git_commit TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 1,
            to_version: 2,
            message: format!("Failed to add git_commit column: {}", e),
        })?;

    conn.execute("ALTER TABLE scan_runs ADD COLUMN git_branch TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 1,
            to_version: 2,
            message: format!("Failed to add git_branch column: {}", e),
        })?;

    // Add metadata entries for tracking
    conn.execute(
        "INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_git_commit', '')",
        [],
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 1,
        to_version: 2,
        message: format!("Failed to add metadata: {}", e),
    })?;

    info!("Migration v2 complete: Added git commit tracking");
    Ok(())
}

/// Migration to version 3: Add imports table for dependency graph edges.
///
/// Per ADR (ATLAS-ADR-DATABASE.md), uses Option A: line_number in PRIMARY KEY
/// to ensure 100% edge accuracy (vs 58% with deduplication).
///
/// Creates:
/// - `imports` table with composite PRIMARY KEY (source_file, target_file, import_name, line_number)
/// - Indexes on source_file, target_file, import_name for fast queries
fn migration_v3(conn: &Connection) -> Result<(), AtlasError> {
    // Create imports table with Option A schema (line_number in PK)
    conn.execute_batch(
        r#"
        -- Import edges table per ADR ATLAS-ADR-DATABASE.md Option A
        CREATE TABLE IF NOT EXISTS imports (
            source_file TEXT NOT NULL,
            target_file TEXT NOT NULL,
            import_name TEXT NOT NULL,
            import_type TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            alias TEXT,
            is_wildcard INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source_file, target_file, import_name, line_number)
        );
        
        -- Indexes for fast queries
        CREATE INDEX IF NOT EXISTS idx_imports_source ON imports(source_file);
        CREATE INDEX IF NOT EXISTS idx_imports_target ON imports(target_file);
        CREATE INDEX IF NOT EXISTS idx_imports_name ON imports(import_name);
        "#,
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 2,
        to_version: 3,
        message: format!("Failed to create imports table: {}", e),
    })?;

    // Add metadata entry for tracking
    conn.execute(
        "INSERT OR IGNORE INTO metadata (key, value) VALUES ('imports_count', '0')",
        [],
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 2,
        to_version: 3,
        message: format!("Failed to add metadata: {}", e),
    })?;

    info!("Migration v3 complete: Added imports table (ADR Option A)");
    Ok(())
}

/// Migration to version 4: Add text_blob for semantic search.
///
/// Per Engg Tech Spec, adds text_blob column to artifacts table
/// for combined searchable text (symbol name + docstring + signature + tags).
fn migration_v4(conn: &Connection) -> Result<(), AtlasError> {
    // Add text_blob column to artifacts
    conn.execute("ALTER TABLE artifacts ADD COLUMN text_blob TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 3,
            to_version: 4,
            message: format!("Failed to add text_blob column: {}", e),
        })?;

    info!("Migration v4 complete: Added text_blob for semantic search");
    Ok(())
}

/// Migration to version 7: Add HTTP metadata columns for endpoints.
///
/// Adds columns:
/// - `artifacts.http_method`
/// - `artifacts.route_path`
/// - `artifacts.router_prefix`
fn migration_v7(conn: &Connection) -> Result<(), AtlasError> {
    conn.execute("ALTER TABLE artifacts ADD COLUMN http_method TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 6,
            to_version: 7,
            message: format!("Failed to add http_method column: {}", e),
        })?;

    conn.execute("ALTER TABLE artifacts ADD COLUMN route_path TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 6,
            to_version: 7,
            message: format!("Failed to add route_path column: {}", e),
        })?;

    conn.execute("ALTER TABLE artifacts ADD COLUMN router_prefix TEXT", [])
        .map_err(|e| AtlasError::Migration {
            from_version: 6,
            to_version: 7,
            message: format!("Failed to add router_prefix column: {}", e),
        })?;

    info!("Migration v7 complete: Added HTTP metadata columns to artifacts");
    Ok(())
}

/// Migration to version 8: Add FastAPI dependency columns for endpoints.
///
/// Adds columns:
/// - `artifacts.direct_dependencies` (JSON string)
/// - `artifacts.dependency_chain` (JSON string)
/// - `artifacts.security_dependencies` (JSON string)
fn migration_v8(conn: &Connection) -> Result<(), AtlasError> {
    if !column_exists(conn, "artifacts", "direct_dependencies")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN direct_dependencies TEXT NOT NULL DEFAULT '[]'",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 7,
            to_version: 8,
            message: format!("Failed to add direct_dependencies column: {}", e),
        })?;
    }

    if !column_exists(conn, "artifacts", "dependency_chain")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN dependency_chain TEXT NOT NULL DEFAULT '[]'",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 7,
            to_version: 8,
            message: format!("Failed to add dependency_chain column: {}", e),
        })?;
    }

    if !column_exists(conn, "artifacts", "security_dependencies")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN security_dependencies TEXT NOT NULL DEFAULT '[]'",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 7,
            to_version: 8,
            message: format!("Failed to add security_dependencies column: {}", e),
        })?;
    }

    info!("Migration v8 complete: Added dependency columns to artifacts");
    Ok(())
}

fn migration_v9(conn: &Connection) -> Result<(), AtlasError> {
    if !column_exists(conn, "artifacts", "request_models")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN request_models TEXT NOT NULL DEFAULT '[]'",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 8,
            to_version: 9,
            message: format!("Failed to add request_models column: {}", e),
        })?;
    }

    if !column_exists(conn, "artifacts", "response_models")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN response_models TEXT NOT NULL DEFAULT '[]'",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 8,
            to_version: 9,
            message: format!("Failed to add response_models column: {}", e),
        })?;
    }

    if !column_exists(conn, "artifacts", "pydantic_fields_summary")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN pydantic_fields_summary TEXT",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 8,
            to_version: 9,
            message: format!("Failed to add pydantic_fields_summary column: {}", e),
        })?;
    }

    if !column_exists(conn, "artifacts", "pydantic_validators_summary")? {
        conn.execute(
            "ALTER TABLE artifacts ADD COLUMN pydantic_validators_summary TEXT",
            [],
        )
        .map_err(|e| AtlasError::Migration {
            from_version: 8,
            to_version: 9,
            message: format!("Failed to add pydantic_validators_summary column: {}", e),
        })?;
    }

    info!("Migration v9 complete: Added request/response schema columns to artifacts");
    Ok(())
}

/// Migration to version 5: Add staleness metadata for zero-config auto-scan.
///
/// Per Engg Tech Spec §3.4, adds `last_known_latest_mtime` to metadata table
/// for the mtime-based staleness probe that detects uncommitted file changes.
fn migration_v5(conn: &Connection) -> Result<(), AtlasError> {
    // Add last_known_latest_mtime to metadata
    conn.execute(
        "INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_known_latest_mtime', '0')",
        [],
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 4,
        to_version: 5,
        message: format!("Failed to add last_known_latest_mtime: {}", e),
    })?;

    info!("Migration v5 complete: Added staleness metadata for zero-config auto-scan");
    Ok(())
}

/// Migration to version 6: Add analysis tables per ROADMAP.md.
///
/// Creates tables for:
/// - `calls`: Call graph edges (function-to-function relationships)
/// - `patterns`: Detected architectural patterns
/// - `domains`: Business domain clusters
/// - `embeddings`: Vector embeddings for semantic search
fn migration_v6(conn: &Connection) -> Result<(), AtlasError> {
    // Create calls table
    conn.execute_batch(
        r#"
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caller_qualified_name TEXT NOT NULL,
            callee_qualified_name TEXT NOT NULL,
            caller_file TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            call_type TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (caller_qualified_name, callee_qualified_name, line_number)
        );
        
        CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_qualified_name);
        CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_qualified_name);
        CREATE INDEX IF NOT EXISTS idx_calls_file ON calls(caller_file);
        "#,
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 5,
        to_version: 6,
        message: format!("Failed to create calls table: {}", e),
    })?;

    // Create patterns table
    conn.execute_batch(
        r#"
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            confidence REAL NOT NULL,
            artifacts TEXT NOT NULL DEFAULT '[]',
            indicators TEXT NOT NULL DEFAULT '[]',
            explanation TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
        CREATE INDEX IF NOT EXISTS idx_patterns_name ON patterns(name);
        CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);
        "#,
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 5,
        to_version: 6,
        message: format!("Failed to create patterns table: {}", e),
    })?;

    // Create domains table
    conn.execute_batch(
        r#"
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            files TEXT NOT NULL DEFAULT '[]',
            keywords TEXT NOT NULL DEFAULT '[]',
            artifact_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_domains_name ON domains(name);
        "#,
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 5,
        to_version: 6,
        message: format!("Failed to create domains table: {}", e),
    })?;

    // Create embeddings table
    conn.execute_batch(
        r#"
        CREATE TABLE IF NOT EXISTS embeddings (
            artifact_id INTEGER PRIMARY KEY,
            embedding BLOB,
            embedding_model TEXT,
            embedding_dim INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(embedding_model);
        "#,
    )
    .map_err(|e| AtlasError::Migration {
        from_version: 5,
        to_version: 6,
        message: format!("Failed to create embeddings table: {}", e),
    })?;

    info!("Migration v6 complete: Added analysis tables (calls, patterns, domains, embeddings)");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::schema::Schema;
    use std::error::Error;

    #[test]
    fn test_get_schema_version_empty() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        let version = get_schema_version(&conn)?;
        assert_eq!(version, 0);
        Ok(())
    }

    #[test]
    fn test_run_migrations() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;

        run_migrations(&conn)?;

        let version = get_schema_version(&conn)?;
        assert_eq!(version, SCHEMA_VERSION);
        Ok(())
    }

    #[test]
    fn test_check_compatibility_fresh_db() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        assert_eq!(check_compatibility(&conn), SchemaCompatibility::UpToDate);
        Ok(())
    }

    #[test]
    fn test_check_compatibility_up_to_date() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;
        run_migrations(&conn)?;

        assert_eq!(check_compatibility(&conn), SchemaCompatibility::UpToDate);
        Ok(())
    }

    #[test]
    fn test_check_compatibility_needs_migration() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        // Create v1 schema manually
        conn.execute_batch(
            r#"
            CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
            INSERT INTO schema_version (version) VALUES (1);
        "#,
        )?;

        let compat = check_compatibility(&conn);
        // v1 needs migration to current version
        assert!(matches!(
            compat,
            SchemaCompatibility::NeedsMigration {
                from: 1,
                to: SCHEMA_VERSION
            }
        ));
        Ok(())
    }

    #[test]
    fn test_migration_v2_adds_git_columns() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;

        // Create base schema without git columns
        conn.execute_batch(
            r#"
            CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
            INSERT INTO schema_version (version) VALUES (1);
            CREATE TABLE scan_runs (
                id INTEGER PRIMARY KEY,
                started_at DATETIME,
                completed_at DATETIME,
                status TEXT,
                artifacts_found INTEGER,
                files_scanned INTEGER,
                files_failed INTEGER,
                duration_ms INTEGER
            );
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME
            );
        "#,
        )?;

        // Run v2 migration
        migration_v2(&conn)?;

        // Verify columns exist by inserting a row with them
        conn.execute(
            "INSERT INTO scan_runs (status, git_commit, git_branch) VALUES ('test', 'abc123', 'main')",
            [],
        )?;

        let (commit, branch): (String, String) = conn
            .query_row(
                "SELECT git_commit, git_branch FROM scan_runs WHERE status = 'test'",
                [],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )?;

        assert_eq!(commit, "abc123");
        assert_eq!(branch, "main");
        Ok(())
    }

    #[test]
    fn test_migration_v3_creates_imports_table() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;

        // Create v2 schema (without imports table)
        conn.execute_batch(
            r#"
            CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
            INSERT INTO schema_version (version) VALUES (2);
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME
            );
        "#,
        )?;

        // Run v3 migration
        migration_v3(&conn)?;

        // Verify imports table was created by inserting a row
        conn.execute(
            r#"INSERT INTO imports (source_file, target_file, import_name, import_type, line_number) 
               VALUES ('app/main.py', 'app/utils.py', 'app.utils', 'module', 5)"#,
            [],
        )?;

        // Query the row back
        let (source, target, name, line): (String, String, String, i32) = conn
            .query_row(
                "SELECT source_file, target_file, import_name, line_number FROM imports",
                [],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?)),
            )?;

        assert_eq!(source, "app/main.py");
        assert_eq!(target, "app/utils.py");
        assert_eq!(name, "app.utils");
        assert_eq!(line, 5);
        Ok(())
    }

    #[test]
    fn test_imports_primary_key_allows_multiple_lines() -> Result<(), Box<dyn Error>> {
        // This test verifies Option A from ADR: line_number in PK allows
        // multiple edges between same source/target
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;

        // Insert same import on two different lines
        conn.execute(
            r#"INSERT INTO imports (source_file, target_file, import_name, import_type, line_number) 
               VALUES ('app/main.py', 'app/utils.py', 'app.utils', 'module', 5)"#,
            [],
        )?;

        conn.execute(
            r#"INSERT INTO imports (source_file, target_file, import_name, import_type, line_number) 
               VALUES ('app/main.py', 'app/utils.py', 'app.utils', 'module', 10)"#,
            [],
        )?;

        // Both should exist (this is the key behavior from ADR Option A)
        let count: i64 = conn.query_row(
            "SELECT COUNT(*) FROM imports WHERE source_file = 'app/main.py' AND target_file = 'app/utils.py'",
            [],
            |row| row.get(0),
        )?;

        assert_eq!(
            count, 2,
            "Option A: Both import occurrences should be stored"
        );
        Ok(())
    }

    #[test]
    fn test_get_schema_version_prefers_metadata_when_schema_version_polluted(
    ) -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;

        // Simulate a DB where schema_version was accidentally appended to.
        // metadata still reflects the real version.
        conn.execute_batch(
            r#"
            CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
            INSERT INTO schema_version (version) VALUES (7);
            INSERT INTO schema_version (version) VALUES (8);
            INSERT INTO schema_version (version) VALUES (9);

            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at DATETIME);
            INSERT INTO metadata (key, value) VALUES ('schema_version', '8');
            "#,
        )?;

        let version = get_schema_version(&conn)?;
        assert_eq!(version, 8);
        Ok(())
    }
}
