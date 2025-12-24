//! Database schema definitions.
//!
//! SQL CREATE TABLE statements for Atlas storage.
//!
//! ## Version History
//!
//! - **v1**: Initial schema (artifacts, files, scan_runs, metadata)
//! - **v2**: Added git_commit tracking for staleness detection
//! - **v3**: Added imports table with 100% edge accuracy (ADR: ATLAS-ADR-DATABASE.md)
//! - **v4**: Added text_blob for semantic search (per Engg Tech Spec)
//! - **v5**: Added staleness metadata for zero-config auto-scan (Engg Tech Spec §3.4)
//! - **v6**: Added analysis tables (calls, patterns, domains, embeddings) per ROADMAP
//! - **v7**: Added HTTP metadata (http_method, route_path, router_prefix) to artifacts
//!
//! ## Design Decisions
//!
//! ### Imports Table (v3)
//!
//! The imports table uses `(source_file, target_file, import_name, line_number)` as
//! PRIMARY KEY per ADR recommendation (Option A). This ensures:
//! - 100% accuracy: All import occurrences are preserved (vs 58% with deduplication)
//! - 1:1 mapping with in-memory Petgraph representation
//! - Line numbers preserved for navigation and debugging
//!
//! ### Text Blob (v4)
//!
//! The `text_blob` field stores a combined searchable text representation of the artifact
//! including symbol name, docstring, signature, and tags for future semantic search.
//!
//! ### Staleness Metadata (v5)
//!
//! Added `last_known_latest_mtime` to metadata table for the mtime-based staleness probe.
//! This enables zero-config auto-scan by detecting uncommitted file changes.
//!
//! ### Analysis Tables (v6)
//!
//! Added tables for advanced analysis per ROADMAP.md:
//! - `calls`: Call graph edges (function-to-function relationships)
//! - `patterns`: Detected architectural patterns (CRUD, Repository, etc.)
//! - `domains`: Business domain clusters
//! - `embeddings`: Vector embeddings for semantic search (future)

/// Current schema version.
/// Increment this when making breaking schema changes.
pub const SCHEMA_VERSION: u32 = 9;

/// Minimum supported schema version for backwards compatibility.
/// Databases older than this MUST be rebuilt.
pub const MIN_SUPPORTED_VERSION: u32 = 1;

/// Schema creation SQL
pub struct Schema;

impl Schema {
    /// Get the complete schema SQL
    pub fn create_tables() -> &'static str {
        r#"
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

-- Insert current version only if table is empty (prevents version table pollution)
INSERT INTO schema_version (version)
SELECT 9
WHERE NOT EXISTS (SELECT 1 FROM schema_version);

-- Core artifacts table (functions, classes, endpoints, etc.)
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol_name TEXT NOT NULL,
    qualified_name TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    file_path TEXT NOT NULL,
    module_path TEXT NOT NULL,
    signature TEXT,
    docstring TEXT,
    feature TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    text_blob TEXT,                    -- Combined text for semantic search (v4)
    hash TEXT,
    http_method TEXT,                  -- HTTP verb for FastAPI endpoints (v7)
    route_path TEXT,                   -- HTTP route path for endpoints (v7)
    router_prefix TEXT,                -- Router prefix if known (v7)
    direct_dependencies TEXT NOT NULL DEFAULT '[]',
    dependency_chain TEXT NOT NULL DEFAULT '[]',
    security_dependencies TEXT NOT NULL DEFAULT '[]',
    request_models TEXT NOT NULL DEFAULT '[]',
    response_models TEXT NOT NULL DEFAULT '[]',
    pydantic_fields_summary TEXT,
    pydantic_validators_summary TEXT,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_artifacts_symbol_name ON artifacts(symbol_name);
CREATE INDEX IF NOT EXISTS idx_artifacts_qualified_name ON artifacts(qualified_name);
CREATE INDEX IF NOT EXISTS idx_artifacts_feature ON artifacts(feature);
CREATE INDEX IF NOT EXISTS idx_artifacts_kind ON artifacts(kind);
CREATE INDEX IF NOT EXISTS idx_artifacts_file_path ON artifacts(file_path);

-- File tracking for incremental scans
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    last_modified INTEGER NOT NULL,
    parse_status TEXT NOT NULL DEFAULT 'success',
    error_message TEXT,
    line_count INTEGER NOT NULL DEFAULT 0,
    artifact_count INTEGER NOT NULL DEFAULT 0,
    last_scanned DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash);

-- Scan runs for audit trail
CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status TEXT NOT NULL DEFAULT 'running',
    artifacts_found INTEGER DEFAULT 0,
    files_scanned INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    duration_ms INTEGER,
    git_commit TEXT,           -- Git HEAD commit hash at scan time (v2)
    git_branch TEXT            -- Git branch at scan time (v2)
);

-- Import edges table (v3) - ADR: ATLAS-ADR-DATABASE.md
-- Uses Option A: line_number in PRIMARY KEY for 100% edge accuracy
-- This preserves all import occurrences (multiple imports of same module on different lines)
CREATE TABLE IF NOT EXISTS imports (
    source_file TEXT NOT NULL,      -- File that contains the import statement
    target_file TEXT NOT NULL,      -- File being imported (resolved path)
    import_name TEXT NOT NULL,      -- Full import name (e.g., "app.commons.database")
    import_type TEXT NOT NULL,      -- Type: "module", "from", "symbol", "relative"
    line_number INTEGER NOT NULL,   -- Line number of import statement
    alias TEXT,                     -- Import alias if any (e.g., "import x as y")
    is_wildcard INTEGER DEFAULT 0,  -- 1 if "from x import *"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- PRIMARY KEY includes line_number per ADR Option A
    -- This allows multiple edges between same source/target with different line numbers
    PRIMARY KEY (source_file, target_file, import_name, line_number)
);

-- Indexes for fast import queries
CREATE INDEX IF NOT EXISTS idx_imports_source ON imports(source_file);
CREATE INDEX IF NOT EXISTS idx_imports_target ON imports(target_file);
CREATE INDEX IF NOT EXISTS idx_imports_name ON imports(import_name);

-- Metadata table for configuration
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Initialize metadata
INSERT OR IGNORE INTO metadata (key, value) VALUES ('schema_version', '9');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('created_at', datetime('now'));
INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_git_commit', '');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('imports_count', '0');
INSERT OR IGNORE INTO metadata (key, value) VALUES ('last_known_latest_mtime', '0');

-- ============================================================================
-- Analysis Tables (v6) - per ROADMAP.md
-- ============================================================================

-- Call graph edges (function-to-function relationships)
-- Used for: Impact analysis, call chain tracing
CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_qualified_name TEXT NOT NULL,    -- Qualified name of calling function
    callee_qualified_name TEXT NOT NULL,    -- Qualified name of called function
    caller_file TEXT NOT NULL,              -- File containing the call
    line_number INTEGER NOT NULL,           -- Line number of the call site
    call_type TEXT NOT NULL,                -- 'direct', 'async', 'callback', 'method', 'super', 'static'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- PRIMARY KEY includes line_number to track multiple call sites
    UNIQUE (caller_qualified_name, callee_qualified_name, line_number)
);

CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_qualified_name);
CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_qualified_name);
CREATE INDEX IF NOT EXISTS idx_calls_file ON calls(caller_file);

-- Detected architectural patterns
-- Used for: Pattern-based code generation, architecture analysis
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,             -- 'crud', 'repository', 'factory', 'service_layer', etc.
    name TEXT NOT NULL,                     -- Name of the class/module implementing pattern
    file_path TEXT NOT NULL,                -- File where pattern is found
    confidence REAL NOT NULL,               -- Detection confidence (0.0-1.0)
    artifacts TEXT NOT NULL DEFAULT '[]',   -- JSON array of artifact qualified names
    indicators TEXT NOT NULL DEFAULT '[]',  -- JSON array of pattern indicators
    explanation TEXT,                       -- Human-readable explanation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_name ON patterns(name);
CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);

-- Business domain clusters
-- Used for: Domain mapping, feature-based organization
CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,              -- Domain name (e.g., 'payment', 'orders', 'users')
    files TEXT NOT NULL DEFAULT '[]',       -- JSON array of file paths in this domain
    keywords TEXT NOT NULL DEFAULT '[]',    -- JSON array of domain keywords
    artifact_count INTEGER DEFAULT 0,       -- Number of artifacts in domain
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_domains_name ON domains(name);

-- Code embeddings for semantic search (Phase 1.1)
-- Uses SQLite BLOB for vector storage; future: use sqlite-vec extension
CREATE TABLE IF NOT EXISTS embeddings (
    artifact_id INTEGER PRIMARY KEY,        -- Foreign key to artifacts.id
    embedding BLOB,                         -- Vector embedding (e.g., 384-dim float32)
    embedding_model TEXT,                   -- Model used (e.g., 'all-MiniLM-L6-v2')
    embedding_dim INTEGER,                  -- Dimension of the embedding
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(embedding_model);
"#
    }

    /// Get the DROP statements for testing
    pub fn drop_tables() -> &'static str {
        r#"
DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS domains;
DROP TABLE IF EXISTS patterns;
DROP TABLE IF EXISTS calls;
DROP TABLE IF EXISTS artifacts;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS scan_runs;
DROP TABLE IF EXISTS imports;
DROP TABLE IF EXISTS metadata;
DROP TABLE IF EXISTS schema_version;
"#
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;
    use std::error::Error;

    #[test]
    fn test_schema_creation() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;

        // Verify tables exist
        let count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
                [],
                |row| row.get(0),
            )?;

        // v6 tables: artifacts, files, scan_runs, imports, metadata, schema_version,
        //            calls, patterns, domains, embeddings = 10 tables
        assert!(
            count >= 9,
            "Expected at least 9 tables (core + analysis tables)"
        );
        Ok(())
    }

    #[test]
    fn test_analysis_tables_exist() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;

        // Verify analysis tables exist
        let analysis_tables = ["calls", "patterns", "domains", "embeddings"];

        for table in &analysis_tables {
            let exists: i64 = conn
                .query_row(
                    &format!(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{}'",
                        table
                    ),
                    [],
                    |row| row.get(0),
                )?;
            assert_eq!(exists, 1, "Table '{}' should exist", table);
        }
        Ok(())
    }

    #[test]
    fn test_schema_version() -> Result<(), Box<dyn Error>> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch(Schema::create_tables())?;

        let version: i64 = conn
            .query_row("SELECT version FROM schema_version LIMIT 1", [], |row| {
                row.get(0)
            })?;

        assert_eq!(version, SCHEMA_VERSION as i64);
        Ok(())
    }
}
