//! Database repository for CRUD operations.
//!
//! Provides type-safe access to the Atlas SQLite database.

use crate::analysis::{CallEdge, CallType, DetectedPattern, PatternConfidence, PatternType};
use crate::storage::schema::Schema;
use crate::storage::run_migrations;
use ranex_core::{Artifact, ArtifactKind, AtlasError, ImportEdge, ImportType};
use rusqlite::{params, Connection, OptionalExtension};
use std::path::Path;
use tracing::{debug, info};

/// Repository for Atlas database operations.
pub struct AtlasRepository {
    conn: Connection,
}

impl AtlasRepository {
    /// Create or open an Atlas database.
    ///
    /// The database file is created with secure permissions (600 on Unix)
    /// to prevent unauthorized access to code metadata.
    pub fn new(db_path: &Path) -> Result<Self, AtlasError> {
        let conn = Connection::open(db_path).map_err(|e| AtlasError::Database {
            operation: "open".to_string(),
            message: e.to_string(),
        })?;

        // Set secure file permissions (owner read/write only)
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            if let Err(e) =
                std::fs::set_permissions(db_path, std::fs::Permissions::from_mode(0o600))
            {
                tracing::warn!(
                    path = %db_path.display(),
                    error = %e,
                    "Failed to set secure permissions on database file"
                );
            } else {
                tracing::debug!(
                    path = %db_path.display(),
                    "Set secure permissions (600) on database file"
                );
            }
        }

        // Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON", [])
            .map_err(|e| AtlasError::Database {
                operation: "pragma".to_string(),
                message: e.to_string(),
            })?;

        // Initialize schema
        conn.execute_batch(Schema::create_tables())
            .map_err(|e| AtlasError::Database {
                operation: "schema".to_string(),
                message: e.to_string(),
            })?;

        run_migrations(&conn)?;

        info!(path = %db_path.display(), "Database initialized");

        Ok(Self { conn })
    }

    /// Create an in-memory database (for testing).
    pub fn in_memory() -> Result<Self, AtlasError> {
        let conn = Connection::open_in_memory().map_err(|e| AtlasError::Database {
            operation: "open_memory".to_string(),
            message: e.to_string(),
        })?;

        conn.execute_batch(Schema::create_tables())
            .map_err(|e| AtlasError::Database {
                operation: "schema".to_string(),
                message: e.to_string(),
            })?;

        run_migrations(&conn)?;

        Ok(Self { conn })
    }

    /// Store multiple artifacts (replaces existing).
    pub fn store_artifacts(&self, artifacts: &[Artifact]) -> Result<(), AtlasError> {
        let tx = self
            .conn
            .unchecked_transaction()
            .map_err(|e| AtlasError::Database {
                operation: "transaction".to_string(),
                message: e.to_string(),
            })?;

        for artifact in artifacts {
            self.upsert_artifact(&tx, artifact)?;
        }

        tx.commit().map_err(|e| AtlasError::Database {
            operation: "commit".to_string(),
            message: e.to_string(),
        })?;

        debug!(count = artifacts.len(), "Stored artifacts");
        Ok(())
    }

    /// Insert or update a single artifact.
    fn upsert_artifact(&self, conn: &Connection, artifact: &Artifact) -> Result<(), AtlasError> {
        let tags_json = serde_json::to_string(&artifact.tags).unwrap_or_else(|_| "[]".to_string());
        let direct_deps_json =
            serde_json::to_string(&artifact.direct_dependencies).unwrap_or_else(|_| "[]".to_string());
        let dependency_chain_json =
            serde_json::to_string(&artifact.dependency_chain).unwrap_or_else(|_| "[]".to_string());
        let security_deps_json = serde_json::to_string(&artifact.security_dependencies)
            .unwrap_or_else(|_| "[]".to_string());
        let request_models_json =
            serde_json::to_string(&artifact.request_models).unwrap_or_else(|_| "[]".to_string());
        let response_models_json =
            serde_json::to_string(&artifact.response_models).unwrap_or_else(|_| "[]".to_string());

        // Build text_blob for semantic search (combines symbol, signature, docstring, tags)
        let text_blob = Self::build_text_blob(artifact);

        conn.execute(
            r#"
            INSERT INTO artifacts (
                symbol_name, qualified_name, kind, file_path, module_path,
                signature, docstring, feature, tags, text_blob, hash,
                http_method, route_path, router_prefix,
                direct_dependencies, dependency_chain, security_dependencies,
                request_models, response_models, pydantic_fields_summary, pydantic_validators_summary,
                line_start, line_end,
                updated_at
            ) VALUES (
                ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11,
                ?12, ?13, ?14,
                ?15, ?16, ?17,
                ?18, ?19, ?20, ?21,
                ?22, ?23,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(qualified_name) DO UPDATE SET
                symbol_name = excluded.symbol_name,
                kind = excluded.kind,
                file_path = excluded.file_path,
                module_path = excluded.module_path,
                signature = excluded.signature,
                docstring = excluded.docstring,
                feature = excluded.feature,
                tags = excluded.tags,
                text_blob = excluded.text_blob,
                hash = excluded.hash,
                http_method = excluded.http_method,
                route_path = excluded.route_path,
                router_prefix = excluded.router_prefix,
                direct_dependencies = excluded.direct_dependencies,
                dependency_chain = excluded.dependency_chain,
                security_dependencies = excluded.security_dependencies,
                request_models = excluded.request_models,
                response_models = excluded.response_models,
                pydantic_fields_summary = excluded.pydantic_fields_summary,
                pydantic_validators_summary = excluded.pydantic_validators_summary,
                line_start = excluded.line_start,
                line_end = excluded.line_end,
                updated_at = CURRENT_TIMESTAMP
            "#,
            params![
                artifact.symbol_name,
                artifact.qualified_name,
                artifact.kind.as_str(),
                artifact.file_path.to_string_lossy(),
                artifact.module_path,
                artifact.signature,
                artifact.docstring,
                artifact.feature,
                tags_json,
                text_blob,
                artifact.hash,
                artifact.http_method,
                artifact.route_path,
                artifact.router_prefix,
                direct_deps_json,
                dependency_chain_json,
                security_deps_json,
                request_models_json,
                response_models_json,
                artifact.pydantic_fields_summary,
                artifact.pydantic_validators_summary,
                artifact.line_start as i64,
                artifact.line_end as i64,
            ],
        )
        .map_err(|e| AtlasError::Database {
            operation: "upsert_artifact".to_string(),
            message: e.to_string(),
        })?;

        Ok(())
    }

    /// Build combined text blob for semantic search.
    fn build_text_blob(artifact: &Artifact) -> String {
        let mut parts = vec![
            artifact.symbol_name.clone(),
            artifact.qualified_name.clone(),
            artifact.kind.as_str().to_string(),
        ];

        if let Some(ref sig) = artifact.signature {
            parts.push(sig.clone());
        }

        if let Some(ref doc) = artifact.docstring {
            parts.push(doc.clone());
        }

        if let Some(ref feature) = artifact.feature {
            parts.push(feature.clone());
        }

        parts.extend(artifact.tags.iter().cloned());

        parts.join(" ")
    }

    /// Search artifacts by symbol name, qualified name, module path, or file path (partial match).
    pub fn search_by_symbol(&self, query: &str, limit: usize) -> Result<Vec<Artifact>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT symbol_name, qualified_name, kind, file_path, module_path,
                       signature, docstring, feature, tags, hash,
                       line_start, line_end,
                       http_method, route_path, router_prefix,
                       direct_dependencies, dependency_chain, security_dependencies,
                       request_models, response_models, pydantic_fields_summary, pydantic_validators_summary
                FROM artifacts
                WHERE symbol_name LIKE ?1
                   OR qualified_name LIKE ?1
                   OR module_path LIKE ?1
                   OR file_path LIKE ?1
                ORDER BY 
                    CASE 
                        WHEN symbol_name = ?3 THEN 1
                        WHEN qualified_name = ?3 THEN 2
                        WHEN symbol_name LIKE ?3 || '%' THEN 3
                        WHEN qualified_name LIKE ?3 || '%' THEN 4
                        ELSE 5
                    END,
                    symbol_name
                LIMIT ?2
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let pattern = format!("%{}%", query);
        let rows = stmt
            .query_map(params![pattern, limit as i64, query], |row| {
                self.row_to_artifact(row)
            })
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut artifacts = Vec::new();
        for row in rows {
            artifacts.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        debug!(query = query, count = artifacts.len(), "Search results");
        Ok(artifacts)
    }

    /// Get a single artifact by exact qualified name.
    pub fn get_by_qualified_name(
        &self,
        qualified_name: &str,
    ) -> Result<Option<Artifact>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT symbol_name, qualified_name, kind, file_path, module_path,
                       signature, docstring, feature, tags, hash,
                       line_start, line_end,
                       http_method, route_path, router_prefix,
                       direct_dependencies, dependency_chain, security_dependencies,
                       request_models, response_models, pydantic_fields_summary, pydantic_validators_summary
                FROM artifacts
                WHERE qualified_name = ?1
                LIMIT 1
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let mut rows = stmt
            .query_map(params![qualified_name], |row| self.row_to_artifact(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        if let Some(row) = rows.next() {
            Ok(Some(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?))
        } else {
            Ok(None)
        }
    }

    /// Search artifacts by feature name.
    pub fn search_by_feature(&self, feature: &str) -> Result<Vec<Artifact>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT symbol_name, qualified_name, kind, file_path, module_path,
                       signature, docstring, feature, tags, hash,
                       line_start, line_end,
                       http_method, route_path, router_prefix,
                       direct_dependencies, dependency_chain, security_dependencies,
                       request_models, response_models, pydantic_fields_summary, pydantic_validators_summary
                FROM artifacts
                WHERE feature = ?1 OR kind = ?1
                ORDER BY file_path, line_start
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![feature], |row| self.row_to_artifact(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut artifacts = Vec::new();
        for row in rows {
            artifacts.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(artifacts)
    }

    /// Count total artifacts.
    pub fn count_artifacts(&self) -> Result<i64, AtlasError> {
        self.conn
            .query_row("SELECT COUNT(*) FROM artifacts", [], |row| row.get(0))
            .map_err(|e| AtlasError::Database {
                operation: "count".to_string(),
                message: e.to_string(),
            })
    }

    /// Get last scan timestamp.
    pub fn last_scan_time(&self) -> Result<Option<i64>, AtlasError> {
        // strftime returns TEXT in SQLite, so we need to get it as String and parse
        let result: Option<String> = self.conn
            .query_row(
                "SELECT strftime('%s', completed_at) FROM scan_runs WHERE completed_at IS NOT NULL ORDER BY id DESC LIMIT 1",
                [],
                |row| row.get(0),
            )
            .optional()
            .map_err(|e| AtlasError::Database {
                operation: "last_scan".to_string(),
                message: e.to_string(),
            })?;

        // Parse the string timestamp to i64
        Ok(result.and_then(|s| s.parse::<i64>().ok()))
    }

    /// Record a completed scan run in the audit table.
    ///
    /// This is called after a successful scan to:
    /// 1. Record the scan for audit purposes
    /// 2. Enable `last_scan_time()` to return a valid timestamp
    /// 3. Track git state for staleness detection
    pub fn record_scan_run(
        &self,
        artifacts_found: usize,
        files_scanned: usize,
        files_failed: usize,
        duration_ms: u64,
        git_commit: Option<&str>,
        git_branch: Option<&str>,
    ) -> Result<i64, AtlasError> {
        self.conn
            .execute(
                r#"
                INSERT INTO scan_runs (
                    started_at, completed_at, status,
                    artifacts_found, files_scanned, files_failed,
                    duration_ms, git_commit, git_branch
                ) VALUES (
                    datetime('now', '-' || ?1 || ' seconds'),
                    CURRENT_TIMESTAMP,
                    'completed',
                    ?2, ?3, ?4, ?5, ?6, ?7
                )
                "#,
                params![
                    duration_ms / 1000, // Approximate start time
                    artifacts_found as i64,
                    files_scanned as i64,
                    files_failed as i64,
                    duration_ms as i64,
                    git_commit,
                    git_branch,
                ],
            )
            .map_err(|e| AtlasError::Database {
                operation: "record_scan_run".to_string(),
                message: e.to_string(),
            })?;

        let id = self.conn.last_insert_rowid();
        debug!(scan_id = id, "Recorded scan run");
        Ok(id)
    }

    /// Delete all artifacts for a file.
    pub fn delete_file_artifacts(&self, file_path: &str) -> Result<usize, AtlasError> {
        let count = self
            .conn
            .execute(
                "DELETE FROM artifacts WHERE file_path = ?1",
                params![file_path],
            )
            .map_err(|e| AtlasError::Database {
                operation: "delete".to_string(),
                message: e.to_string(),
            })?;

        Ok(count)
    }

    // ========================================================================
    // Import Operations (ADR: ATLAS-ADR-DATABASE.md)
    // ========================================================================

    /// Store multiple import edges.
    pub fn store_imports(&self, imports: &[ImportEdge]) -> Result<(), AtlasError> {
        let tx = self
            .conn
            .unchecked_transaction()
            .map_err(|e| AtlasError::Database {
                operation: "transaction".to_string(),
                message: e.to_string(),
            })?;

        for import in imports {
            self.insert_import(&tx, import)?;
        }

        tx.commit().map_err(|e| AtlasError::Database {
            operation: "commit".to_string(),
            message: e.to_string(),
        })?;

        debug!(count = imports.len(), "Stored imports");
        Ok(())
    }

    /// Insert a single import edge.
    fn insert_import(&self, conn: &Connection, import: &ImportEdge) -> Result<(), AtlasError> {
        conn.execute(
            r#"
            INSERT OR REPLACE INTO imports (
                source_file, target_file, import_name, import_type,
                line_number, alias, is_wildcard
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
            "#,
            params![
                import.source_file,
                import.target_file,
                import.import_name,
                import.import_type.as_str(),
                import.line_number as i64,
                import.alias,
                import.is_wildcard as i32,
            ],
        )
        .map_err(|e| AtlasError::Database {
            operation: "insert_import".to_string(),
            message: e.to_string(),
        })?;

        Ok(())
    }

    /// Get all imports from a source file.
    pub fn get_imports_from_file(&self, source_file: &str) -> Result<Vec<ImportEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT source_file, target_file, import_name, import_type,
                       line_number, alias, is_wildcard
                FROM imports
                WHERE source_file = ?1
                ORDER BY line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![source_file], |row| self.row_to_import(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut imports = Vec::new();
        for row in rows {
            imports.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(imports)
    }

    /// Get all files that import a target file.
    pub fn get_importers_of_file(&self, target_file: &str) -> Result<Vec<ImportEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT source_file, target_file, import_name, import_type,
                       line_number, alias, is_wildcard
                FROM imports
                WHERE target_file = ?1
                ORDER BY source_file, line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![target_file], |row| self.row_to_import(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut imports = Vec::new();
        for row in rows {
            imports.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(imports)
    }

    /// Delete all imports from a source file.
    pub fn delete_file_imports(&self, source_file: &str) -> Result<usize, AtlasError> {
        let count = self
            .conn
            .execute(
                "DELETE FROM imports WHERE source_file = ?1",
                params![source_file],
            )
            .map_err(|e| AtlasError::Database {
                operation: "delete_imports".to_string(),
                message: e.to_string(),
            })?;

        Ok(count)
    }

    /// Count total imports.
    pub fn count_imports(&self) -> Result<i64, AtlasError> {
        self.conn
            .query_row("SELECT COUNT(*) FROM imports", [], |row| row.get(0))
            .map_err(|e| AtlasError::Database {
                operation: "count_imports".to_string(),
                message: e.to_string(),
            })
    }

    // ========================================================================
    // Metadata Operations (for staleness tracking)
    // ========================================================================

    /// Get a metadata value by key.
    pub fn get_metadata(&self, key: &str) -> Result<Option<String>, AtlasError> {
        self.conn
            .query_row(
                "SELECT value FROM metadata WHERE key = ?1",
                params![key],
                |row| row.get(0),
            )
            .optional()
            .map_err(|e| AtlasError::Database {
                operation: "get_metadata".to_string(),
                message: e.to_string(),
            })
    }

    /// Set a metadata value.
    pub fn set_metadata(&self, key: &str, value: &str) -> Result<(), AtlasError> {
        self.conn
            .execute(
                "INSERT OR REPLACE INTO metadata (key, value, updated_at) VALUES (?1, ?2, CURRENT_TIMESTAMP)",
                params![key, value],
            )
            .map_err(|e| AtlasError::Database {
                operation: "set_metadata".to_string(),
                message: e.to_string(),
            })?;
        Ok(())
    }

    /// Convert a database row to an ImportEdge.
    fn row_to_import(&self, row: &rusqlite::Row) -> rusqlite::Result<ImportEdge> {
        let import_type_str: String = row.get(3)?;
        let import_type = ImportType::parse(&import_type_str).unwrap_or(ImportType::Module);
        let is_wildcard: i32 = row.get(6)?;

        Ok(ImportEdge {
            source_file: row.get(0)?,
            target_file: row.get(1)?,
            import_name: row.get(2)?,
            import_type,
            line_number: row.get::<_, i64>(4)? as usize,
            alias: row.get(5)?,
            is_wildcard: is_wildcard != 0,
        })
    }

    /// Convert a database row to an Artifact.
    fn row_to_artifact(&self, row: &rusqlite::Row) -> rusqlite::Result<Artifact> {
        let kind_str: String = row.get(2)?;
        let kind = ArtifactKind::parse(&kind_str).unwrap_or(ArtifactKind::Function);

        let tags_json: String = row.get(8)?;
        let tags: Vec<String> = serde_json::from_str(&tags_json).unwrap_or_default();

        let file_path_str: String = row.get(3)?;

        let direct_deps_json: String = row.get(15)?;
        let dependency_chain_json: String = row.get(16)?;
        let security_deps_json: String = row.get(17)?;
        let request_models_json: String = row.get(18)?;
        let response_models_json: String = row.get(19)?;

        let request_models: Vec<String> =
            serde_json::from_str(&request_models_json).unwrap_or_default();
        let response_models: Vec<String> =
            serde_json::from_str(&response_models_json).unwrap_or_default();

        let direct_dependencies: Vec<String> =
            serde_json::from_str(&direct_deps_json).unwrap_or_default();
        let dependency_chain: Vec<String> =
            serde_json::from_str(&dependency_chain_json).unwrap_or_default();
        let security_dependencies: Vec<String> =
            serde_json::from_str(&security_deps_json).unwrap_or_default();

        Ok(Artifact {
            symbol_name: row.get(0)?,
            qualified_name: row.get(1)?,
            kind,
            file_path: std::path::PathBuf::from(file_path_str),
            module_path: row.get(4)?,
            signature: row.get(5)?,
            docstring: row.get(6)?,
            feature: row.get(7)?,
            tags,
            direct_dependencies,
            dependency_chain,
            security_dependencies,
            request_models,
            response_models,
            pydantic_fields_summary: row.get(20)?,
            pydantic_validators_summary: row.get(21)?,
            hash: row.get(9)?,
            line_start: row.get::<_, i64>(10)? as usize,
            line_end: row.get::<_, i64>(11)? as usize,
            http_method: row.get(12)?,
            route_path: row.get(13)?,
            router_prefix: row.get(14)?,
        })
    }

    // ========================================================================
    // Call Graph Operations (Phase 1.3)
    // ========================================================================

    /// Store multiple call graph edges.
    pub fn store_call_edges(&self, edges: &[CallEdge]) -> Result<(), AtlasError> {
        let tx = self
            .conn
            .unchecked_transaction()
            .map_err(|e| AtlasError::Database {
                operation: "transaction".to_string(),
                message: e.to_string(),
            })?;

        for edge in edges {
            self.insert_call_edge(&tx, edge)?;
        }

        tx.commit().map_err(|e| AtlasError::Database {
            operation: "commit".to_string(),
            message: e.to_string(),
        })?;

        debug!(count = edges.len(), "Stored call edges");
        Ok(())
    }

    /// Insert a single call edge.
    fn insert_call_edge(&self, conn: &Connection, edge: &CallEdge) -> Result<(), AtlasError> {
        conn.execute(
            r#"
            INSERT OR REPLACE INTO calls (
                caller_qualified_name, callee_qualified_name, caller_file,
                line_number, call_type
            ) VALUES (?1, ?2, ?3, ?4, ?5)
            "#,
            params![
                edge.caller,
                edge.callee,
                edge.file_path,
                edge.line_number as i64,
                edge.call_type.as_str(),
            ],
        )
        .map_err(|e| AtlasError::Database {
            operation: "insert_call_edge".to_string(),
            message: e.to_string(),
        })?;

        Ok(())
    }

    /// Get all call edges where the given function is the caller.
    pub fn get_calls_from(&self, caller: &str) -> Result<Vec<CallEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT caller_qualified_name, callee_qualified_name, caller_file,
                       line_number, call_type
                FROM calls
                WHERE caller_qualified_name = ?1
                ORDER BY line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![caller], |row| self.row_to_call_edge(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut edges = Vec::new();
        for row in rows {
            edges.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(edges)
    }

    /// Get all call edges where the given function is the callee.
    pub fn get_calls_to(&self, callee: &str) -> Result<Vec<CallEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT caller_qualified_name, callee_qualified_name, caller_file,
                       line_number, call_type
                FROM calls
                WHERE callee_qualified_name = ?1
                ORDER BY caller_qualified_name, line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![callee], |row| self.row_to_call_edge(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut edges = Vec::new();
        for row in rows {
            edges.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(edges)
    }

    /// Get all call edges.
    pub fn get_all_call_edges(&self) -> Result<Vec<CallEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT caller_qualified_name, callee_qualified_name, caller_file,
                       line_number, call_type
                FROM calls
                ORDER BY caller_qualified_name, line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map([], |row| self.row_to_call_edge(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut edges = Vec::new();
        for row in rows {
            edges.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(edges)
    }

    /// Clear all call edges.
    pub fn clear_call_edges(&self) -> Result<usize, AtlasError> {
        let count =
            self.conn
                .execute("DELETE FROM calls", [])
                .map_err(|e| AtlasError::Database {
                    operation: "clear_calls".to_string(),
                    message: e.to_string(),
                })?;
        Ok(count)
    }

    /// Convert a database row to a CallEdge.
    fn row_to_call_edge(&self, row: &rusqlite::Row) -> rusqlite::Result<CallEdge> {
        let call_type_str: String = row.get(4)?;
        let call_type = CallType::parse(&call_type_str).unwrap_or(CallType::Direct);

        Ok(CallEdge {
            caller: row.get(0)?,
            callee: row.get(1)?,
            file_path: row.get(2)?,
            line_number: row.get::<_, i64>(3)? as usize,
            call_type,
        })
    }

    // ========================================================================
    // Pattern Operations (Phase 2.1)
    // ========================================================================

    /// Store detected patterns.
    pub fn store_patterns(&self, patterns: &[DetectedPattern]) -> Result<(), AtlasError> {
        let tx = self
            .conn
            .unchecked_transaction()
            .map_err(|e| AtlasError::Database {
                operation: "transaction".to_string(),
                message: e.to_string(),
            })?;

        for pattern in patterns {
            self.insert_pattern(&tx, pattern)?;
        }

        tx.commit().map_err(|e| AtlasError::Database {
            operation: "commit".to_string(),
            message: e.to_string(),
        })?;

        debug!(count = patterns.len(), "Stored patterns");
        Ok(())
    }

    /// Insert a single pattern.
    fn insert_pattern(
        &self,
        conn: &Connection,
        pattern: &DetectedPattern,
    ) -> Result<(), AtlasError> {
        let artifacts_json =
            serde_json::to_string(&pattern.artifacts).unwrap_or_else(|_| "[]".to_string());
        let indicators_json =
            serde_json::to_string(&pattern.indicators).unwrap_or_else(|_| "[]".to_string());

        conn.execute(
            r#"
            INSERT INTO patterns (
                pattern_type, name, file_path, confidence,
                artifacts, indicators, explanation
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
            "#,
            params![
                pattern.pattern_type.as_str(),
                pattern.name,
                pattern.file_path,
                pattern.confidence.value(),
                artifacts_json,
                indicators_json,
                pattern.explanation,
            ],
        )
        .map_err(|e| AtlasError::Database {
            operation: "insert_pattern".to_string(),
            message: e.to_string(),
        })?;

        Ok(())
    }

    /// Get all detected patterns.
    pub fn get_all_patterns(&self) -> Result<Vec<DetectedPattern>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT pattern_type, name, file_path, confidence,
                       artifacts, indicators, explanation
                FROM patterns
                ORDER BY confidence DESC, name
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map([], |row| self.row_to_pattern(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut patterns = Vec::new();
        for row in rows {
            patterns.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(patterns)
    }

    /// Get patterns of a specific type.
    pub fn get_patterns_by_type(
        &self,
        pattern_type: PatternType,
    ) -> Result<Vec<DetectedPattern>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT pattern_type, name, file_path, confidence,
                       artifacts, indicators, explanation
                FROM patterns
                WHERE pattern_type = ?1
                ORDER BY confidence DESC, name
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![pattern_type.as_str()], |row| {
                self.row_to_pattern(row)
            })
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut patterns = Vec::new();
        for row in rows {
            patterns.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(patterns)
    }

    /// Clear all patterns.
    pub fn clear_patterns(&self) -> Result<usize, AtlasError> {
        let count =
            self.conn
                .execute("DELETE FROM patterns", [])
                .map_err(|e| AtlasError::Database {
                    operation: "clear_patterns".to_string(),
                    message: e.to_string(),
                })?;
        Ok(count)
    }

    /// Convert a database row to a DetectedPattern.
    fn row_to_pattern(&self, row: &rusqlite::Row) -> rusqlite::Result<DetectedPattern> {
        let pattern_type_str: String = row.get(0)?;
        let pattern_type = PatternType::parse(&pattern_type_str).unwrap_or(PatternType::Crud);

        let confidence_val: f64 = row.get(3)?;
        let artifacts_json: String = row.get(4)?;
        let indicators_json: String = row.get(5)?;
        let explanation: Option<String> = row.get(6)?;

        let artifacts: Vec<String> = serde_json::from_str(&artifacts_json).unwrap_or_default();
        let indicators: Vec<String> = serde_json::from_str(&indicators_json).unwrap_or_default();

        Ok(DetectedPattern {
            pattern_type,
            name: row.get(1)?,
            file_path: row.get(2)?,
            confidence: PatternConfidence::new(confidence_val),
            artifacts,
            indicators,
            explanation: explanation.unwrap_or_default(),
        })
    }

    // ========================================================================
    // Bulk Query Operations (for analysis)
    // ========================================================================

    /// Get all artifacts (for pattern detection).
    pub fn get_all_artifacts(&self) -> Result<Vec<Artifact>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT symbol_name, qualified_name, kind, file_path, module_path,
                       signature, docstring, feature, tags, hash,
                       line_start, line_end,
                       http_method, route_path, router_prefix,
                       direct_dependencies, dependency_chain, security_dependencies,
                       request_models, response_models, pydantic_fields_summary, pydantic_validators_summary
                FROM artifacts
                ORDER BY file_path, line_start
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map([], |row| self.row_to_artifact(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut artifacts = Vec::new();
        for row in rows {
            artifacts.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(artifacts)
    }

    /// Get all import edges (for building DependencyGraph).
    pub fn get_all_imports(&self) -> Result<Vec<ImportEdge>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT source_file, target_file, import_name, import_type,
                       line_number, alias, is_wildcard
                FROM imports
                ORDER BY source_file, line_number
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map([], |row| self.row_to_import(row))
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut imports = Vec::new();
        for row in rows {
            imports.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(imports)
    }

    /// Get artifacts in batches for memory-efficient processing.
    ///
    /// Returns an iterator that yields batches of artifacts.
    /// This is useful for processing large codebases without loading
    /// all artifacts into memory at once.
    pub fn get_artifacts_batched(
        &self,
        batch_size: usize,
    ) -> Result<ArtifactBatchIterator<'_>, AtlasError> {
        let total = self.count_artifacts()? as usize;
        Ok(ArtifactBatchIterator {
            repo: self,
            batch_size,
            offset: 0,
            total,
        })
    }

    /// Get a batch of artifacts with pagination.
    pub fn get_artifacts_page(
        &self,
        offset: usize,
        limit: usize,
    ) -> Result<Vec<Artifact>, AtlasError> {
        let mut stmt = self
            .conn
            .prepare(
                r#"
                SELECT symbol_name, qualified_name, kind, file_path, module_path,
                       signature, docstring, feature, tags, hash,
                       line_start, line_end,
                       http_method, route_path, router_prefix,
                       direct_dependencies, dependency_chain, security_dependencies,
                       request_models, response_models, pydantic_fields_summary, pydantic_validators_summary
                FROM artifacts
                ORDER BY file_path, line_start
                LIMIT ?1 OFFSET ?2
                "#,
            )
            .map_err(|e| AtlasError::Database {
                operation: "prepare".to_string(),
                message: e.to_string(),
            })?;

        let rows = stmt
            .query_map(params![limit as i64, offset as i64], |row| {
                self.row_to_artifact(row)
            })
            .map_err(|e| AtlasError::Database {
                operation: "query".to_string(),
                message: e.to_string(),
            })?;

        let mut artifacts = Vec::new();
        for row in rows {
            artifacts.push(row.map_err(|e| AtlasError::Database {
                operation: "read_row".to_string(),
                message: e.to_string(),
            })?);
        }

        Ok(artifacts)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ranex_core::{ArtifactKind, Artifact};
    use std::error::Error;

    #[test]
    fn test_store_and_search_preserves_http_metadata() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let artifact = Artifact::new(
            "read_item",
            "app.api.read_item",
            ArtifactKind::Endpoint,
            "app/api.py",
            "app.api",
            10,
            20,
        )
        .with_tag("fastapi_route")
        .with_tag("http_get")
        .with_http_method("get")
        .with_route_path("/items/{item_id}")
        .with_router_prefix("/api/v1")
        .with_direct_dependencies(vec!["get_db".to_string(), "get_current_user".to_string()])
        .with_dependency_chain(vec![
            "get_db".to_string(),
            "get_current_user".to_string(),
            "oauth2_scheme".to_string(),
        ])
        .with_security_dependencies(vec!["get_current_user".to_string()]);

        repo.store_artifacts(std::slice::from_ref(&artifact))?;

        let results = repo.search_by_symbol("read_item", 5)?;

        let found = results.iter().find(|a| a.qualified_name == "app.api.read_item").ok_or_else(
            || std::io::Error::new(std::io::ErrorKind::NotFound, "artifact missing"),
        )?;

        assert_eq!(found.http_method.as_deref(), Some("get"));
        assert_eq!(found.route_path.as_deref(), Some("/items/{item_id}"));
        assert_eq!(found.router_prefix.as_deref(), Some("/api/v1"));
        assert!(found.tags.contains(&"fastapi_route".to_string()));
        assert!(found.tags.contains(&"http_get".to_string()));

        assert_eq!(
            found.direct_dependencies,
            vec!["get_db".to_string(), "get_current_user".to_string()]
        );
        assert_eq!(
            found.dependency_chain,
            vec![
                "get_db".to_string(),
                "get_current_user".to_string(),
                "oauth2_scheme".to_string()
            ]
        );
        assert_eq!(found.security_dependencies, vec!["get_current_user".to_string()]);
        Ok(())
    }

    #[test]
    fn test_search_by_feature_matches_kind() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let endpoint = Artifact::new(
            "read_item",
            "app.api.read_item",
            ArtifactKind::Endpoint,
            "app/api.py",
            "app.api",
            10,
            20,
        );

        repo.store_artifacts(std::slice::from_ref(&endpoint))?;

        let results = repo.search_by_feature("endpoint")?;
        assert_eq!(results.len(), 1);
        let found = results.first().ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint missing")
        })?;
        assert_eq!(found.qualified_name, "app.api.read_item");
        assert_eq!(found.kind, ArtifactKind::Endpoint);
        Ok(())
    }
}

/// Iterator for batched artifact retrieval.
pub struct ArtifactBatchIterator<'a> {
    repo: &'a AtlasRepository,
    batch_size: usize,
    offset: usize,
    total: usize,
}

impl<'a> Iterator for ArtifactBatchIterator<'a> {
    type Item = Result<Vec<Artifact>, AtlasError>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.offset >= self.total {
            return None;
        }

        let batch = self.repo.get_artifacts_page(self.offset, self.batch_size);
        self.offset += self.batch_size;

        match batch {
            Ok(artifacts) if artifacts.is_empty() => None,
            other => Some(other),
        }
    }
}

impl<'a> ArtifactBatchIterator<'a> {
    /// Get the total number of artifacts.
    pub fn total(&self) -> usize {
        self.total
    }

    /// Get the batch size.
    pub fn batch_size(&self) -> usize {
        self.batch_size
    }
}

#[cfg(test)]
mod tests_basic {
    use super::*;
    use std::error::Error;

    fn create_test_artifact() -> Artifact {
        Artifact::new(
            "test_func",
            "app.test.test_func",
            ArtifactKind::Function,
            "app/test.py",
            "app.test",
            10,
            20,
        )
        .with_signature("test_func()")
        .with_feature("testing")
    }

    #[test]
    fn test_store_and_search() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;
        let artifact = create_test_artifact();

        repo.store_artifacts(&[artifact])?;

        let results = repo.search_by_symbol("test", 10)?;
        assert_eq!(results.len(), 1);
        let first = results
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
        assert_eq!(first.symbol_name, "test_func");
        Ok(())
    }

    #[test]
    fn test_search_by_feature() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;
        let artifact = create_test_artifact();

        repo.store_artifacts(&[artifact])?;

        let results = repo.search_by_feature("testing")?;
        assert_eq!(results.len(), 1);
        Ok(())
    }

    #[test]
    fn test_count() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;
        let artifact = create_test_artifact();

        repo.store_artifacts(&[artifact])?;

        let count = repo.count_artifacts()?;
        assert_eq!(count, 1);
        Ok(())
    }

    #[test]
    fn test_store_and_query_imports() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let imports = vec![
            ImportEdge::new(
                "app/main.py",
                "app/utils.py",
                "app.utils",
                ImportType::Module,
                5,
            ),
            ImportEdge::new("app/main.py", "app/db.py", "app.db", ImportType::From, 10),
        ];

        repo.store_imports(&imports)?;

        let count = repo.count_imports()?;
        assert_eq!(count, 2);

        let from_main = repo.get_imports_from_file("app/main.py")?;
        assert_eq!(from_main.len(), 2);
        let mut line_numbers: Vec<usize> = from_main.iter().map(|e| e.line_number).collect();
        line_numbers.sort_unstable();
        assert_eq!(line_numbers, vec![5, 10]);
        Ok(())
    }

    #[test]
    fn test_import_multiple_lines_option_a() -> Result<(), Box<dyn Error>> {
        // ADR Option A: line_number in PK allows multiple edges between same files
        let repo = AtlasRepository::in_memory()?;

        let imports = vec![
            ImportEdge::new(
                "app/main.py",
                "app/utils.py",
                "app.utils",
                ImportType::Module,
                5,
            ),
            ImportEdge::new(
                "app/main.py",
                "app/utils.py",
                "app.utils",
                ImportType::Module,
                15, // Same module, different line
            ),
        ];

        repo.store_imports(&imports)?;

        // Both should be stored (Option A behavior)
        let count = repo.count_imports()?;
        assert_eq!(
            count, 2,
            "Option A: Both import occurrences should be stored"
        );
        Ok(())
    }

    #[test]
    fn test_get_importers_of_file() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let imports = vec![
            ImportEdge::new(
                "app/main.py",
                "app/utils.py",
                "app.utils",
                ImportType::Module,
                5,
            ),
            ImportEdge::new(
                "app/service.py",
                "app/utils.py",
                "app.utils",
                ImportType::Module,
                3,
            ),
        ];

        repo.store_imports(&imports)?;

        let importers = repo.get_importers_of_file("app/utils.py")?;
        assert_eq!(importers.len(), 2);
        Ok(())
    }

    // ========================================================================
    // Call Graph Tests
    // ========================================================================

    #[test]
    fn test_store_and_query_call_edges() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let edges = vec![
            CallEdge::new(
                "app.service.get_order",
                "app.repo.find_by_id",
                CallType::Direct,
                10,
                "app/service.py",
            ),
            CallEdge::new(
                "app.service.get_order",
                "app.utils.validate",
                CallType::Direct,
                15,
                "app/service.py",
            ),
        ];

        repo.store_call_edges(&edges)?;

        // Query calls from a function
        let from_service = repo.get_calls_from("app.service.get_order")?;
        assert_eq!(from_service.len(), 2);

        // Query calls to a function
        let to_repo = repo.get_calls_to("app.repo.find_by_id")?;
        assert_eq!(to_repo.len(), 1);
        let first = to_repo
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
        assert_eq!(first.caller, "app.service.get_order");
        Ok(())
    }

    #[test]
    fn test_get_all_call_edges() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let edges = vec![
            CallEdge::new("A", "B", CallType::Direct, 1, "a.py"),
            CallEdge::new("B", "C", CallType::Async, 2, "b.py"),
        ];

        repo.store_call_edges(&edges)?;

        let all = repo.get_all_call_edges()?;
        assert_eq!(all.len(), 2);
        Ok(())
    }

    #[test]
    fn test_clear_call_edges() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let edges = vec![CallEdge::new("A", "B", CallType::Direct, 1, "a.py")];
        repo.store_call_edges(&edges)?;

        let cleared = repo.clear_call_edges()?;
        assert_eq!(cleared, 1);

        let all = repo.get_all_call_edges()?;
        assert!(all.is_empty());
        Ok(())
    }

    // ========================================================================
    // Pattern Tests
    // ========================================================================

    #[test]
    fn test_store_and_query_patterns() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let patterns = vec![DetectedPattern::new(
            PatternType::Crud,
            "OrderService",
            "app/services/orders.py",
            PatternConfidence::new(0.85),
        )
        .with_indicator("create")
        .with_indicator("get")
        .with_indicator("update")
        .with_indicator("delete")
        .with_explanation("OrderService implements CRUD operations")];

        repo.store_patterns(&patterns)?;

        let all = repo.get_all_patterns()?;
        assert_eq!(all.len(), 1);
        let first = all
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
        assert_eq!(first.name, "OrderService");
        assert_eq!(first.pattern_type, PatternType::Crud);
        assert!(first.confidence.value() > 0.8);
        Ok(())
    }

    #[test]
    fn test_get_patterns_by_type() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let patterns = vec![
            DetectedPattern::new(
                PatternType::Crud,
                "OrderService",
                "orders.py",
                PatternConfidence::new(0.8),
            ),
            DetectedPattern::new(
                PatternType::Repository,
                "OrderRepository",
                "orders.py",
                PatternConfidence::new(0.9),
            ),
            DetectedPattern::new(
                PatternType::Crud,
                "UserService",
                "users.py",
                PatternConfidence::new(0.7),
            ),
        ];

        repo.store_patterns(&patterns)?;

        let crud_patterns = repo.get_patterns_by_type(PatternType::Crud)?;
        assert_eq!(crud_patterns.len(), 2);

        let repo_patterns = repo.get_patterns_by_type(PatternType::Repository)?;
        assert_eq!(repo_patterns.len(), 1);
        let first = repo_patterns
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
        assert_eq!(first.name, "OrderRepository");
        Ok(())
    }

    #[test]
    fn test_clear_patterns() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let patterns = vec![DetectedPattern::new(
            PatternType::Crud,
            "Test",
            "test.py",
            PatternConfidence::new(0.5),
        )];
        repo.store_patterns(&patterns)?;

        let cleared = repo.clear_patterns()?;
        assert_eq!(cleared, 1);

        let all = repo.get_all_patterns()?;
        assert!(all.is_empty());
        Ok(())
    }

    // ========================================================================
    // Bulk Query Tests
    // ========================================================================

    #[test]
    fn test_get_all_artifacts() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let artifacts = vec![
            Artifact::new(
                "func1",
                "app.func1",
                ArtifactKind::Function,
                "app.py",
                "app",
                1,
                10,
            ),
            Artifact::new(
                "func2",
                "app.func2",
                ArtifactKind::Function,
                "app.py",
                "app",
                11,
                20,
            ),
        ];

        repo.store_artifacts(&artifacts)?;

        let all = repo.get_all_artifacts()?;
        assert_eq!(all.len(), 2);
        Ok(())
    }

    #[test]
    fn test_get_all_imports() -> Result<(), Box<dyn Error>> {
        let repo = AtlasRepository::in_memory()?;

        let imports = vec![
            ImportEdge::new("a.py", "b.py", "b", ImportType::Module, 1),
            ImportEdge::new("a.py", "c.py", "c", ImportType::Module, 2),
            ImportEdge::new("b.py", "c.py", "c", ImportType::Module, 1),
        ];

        repo.store_imports(&imports)?;

        let all = repo.get_all_imports()?;
        assert_eq!(all.len(), 3);
        Ok(())
    }
}
