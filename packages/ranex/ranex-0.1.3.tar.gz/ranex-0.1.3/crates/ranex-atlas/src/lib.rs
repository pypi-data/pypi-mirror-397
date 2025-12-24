//! # ranex-atlas
//!
//! Atlas codebase indexing system for Ranex.
//!
//! Atlas scans Python projects, extracts symbols (functions, classes, endpoints),
//! and stores them in SQLite for fast retrieval. This enables AI coding tools
//! to find existing code instead of hallucinating or duplicating.
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
//! │   Scanner   │───▶│   Parser    │───▶│   Storage   │
//! │  (walker)   │    │ (python_ast)│    │  (sqlite)   │
//! └─────────────┘    └─────────────┘    └─────────────┘
//!       │                   │                  │
//!       ▼                   ▼                  ▼
//!   Find .py files    Parse AST &        Store artifacts
//!   Respect ignore    Extract symbols    in atlas.sqlite
//! ```
//!
//! ## Usage
//!
//! ```rust,no_run
//! use ranex_atlas::Atlas;
//! use std::path::Path;
//!
//! fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     // Initialize Atlas for a project
//!     let mut atlas = Atlas::new(Path::new("/path/to/project"))?;
//!
//!     // Scan the project
//!     let result = atlas.scan()?;
//!     println!("Found {} artifacts", result.stats.artifacts_found);
//!
//!     // Search for symbols
//!     let matches = atlas.search("calculate_tax", 10)?;
//!     for artifact in matches {
//!         println!("{}: {}", artifact.symbol_name, artifact.file_path.display());
//!     }
//!     Ok(())
//! }
//! ```
//!
//! Note: This example uses `no_run` because it requires a valid project directory
//! with Python files. The code is compiled to verify correctness.

pub mod analysis;
pub mod artifact;
pub mod parser;
pub mod query;
pub mod scanner;
pub mod staleness;
pub mod storage;

// Re-export main types
pub use artifact::ArtifactProcessor;
pub use parser::{ParseResult, PythonParser};
pub use query::QueryBuilder;
pub use scanner::{FileWalker, ScanOptions};
pub use storage::{AtlasRepository, Schema};

use crate::analysis::fastapi_dependencies;
use crate::analysis::{analyze_router_topology, RouterTopologyReport};
use crate::analysis::{CallEdge, CallGraph, CallType};
use glob::Pattern;
use ranex_core::{Artifact, ArtifactKind, AtlasError, ImportEdge, ImportType, RanexConfig, ScanResult, ScanStats};
use serde::Serialize;
use staleness::{check_staleness, get_git_branch, get_git_head, ScanMetadata, StalenessReason};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use tracing::{debug, info, instrument, warn};

/// Main Atlas indexing system.
///
/// Orchestrates scanning, parsing, and storage of Python codebase artifacts.
pub struct Atlas {
    /// Project root directory
    pub project_root: PathBuf,

    /// Configuration
    config: RanexConfig,

    /// Database repository
    repository: AtlasRepository,
}

impl Atlas {
    /// Create a new Atlas instance for a project.
    ///
    /// # Arguments
    /// * `project_root` - Path to the Python project root
    ///
    /// # Errors
    /// Returns error if database initialization fails.
    #[instrument(skip_all, fields(project = %project_root.display()))]
    pub fn new(project_root: &Path) -> Result<Self, AtlasError> {
        let project_root = project_root.canonicalize().map_err(|e| AtlasError::Walk {
            path: project_root.to_path_buf(),
            message: format!("Failed to resolve project root: {}", e),
        })?;

        let config = RanexConfig::load(&project_root).unwrap_or_default();
        let db_path = config.db_path(&project_root);

        // Ensure .ranex directory exists
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| AtlasError::Database {
                operation: "create_dir".to_string(),
                message: format!("Failed to create .ranex directory: {}", e),
            })?;
        }

        let repository = AtlasRepository::new(&db_path)?;

        info!(
            db_path = %db_path.display(),
            "Atlas initialized"
        );

        Ok(Self {
            project_root,
            config,
            repository,
        })
    }

    /// Scan the project and index all Python files.
    ///
    /// # Returns
    /// Scan statistics including artifact counts and any errors.
    #[instrument(skip(self))]
    pub fn scan(&mut self) -> Result<ScanResult, AtlasError> {
        let start = std::time::Instant::now();
        let mut stats = ScanStats::new();
        let mut failed_files = Vec::new();

        // 1. Walk directory and find Python files
        let walker = FileWalker::new(&self.project_root, &self.config.atlas)?;
        let python_files = walker.find_python_files()?;

        // Enforce SecurityConfig at scan time: only index files that are
        // permitted by security rules. This prevents denied files from ever
        // entering the Atlas index.
        let mut allowed_files = Vec::new();
        for path in python_files {
            if self.is_path_allowed_by_security(&path) {
                allowed_files.push(path);
            } else {
                debug!(
                    file = %path.display(),
                    "Skipping file denied by security configuration during scan"
                );
            }
        }

        info!(file_count = allowed_files.len(), "Found security-allowed Python files");
        stats.files_scanned = allowed_files.len();

        // Track newest mtime from actual scanned files (for staleness detection)
        let mut newest_mtime: u64 = 0;
        for file_path in &allowed_files {
            if let Ok(metadata) = std::fs::metadata(file_path)
                && let Ok(modified) = metadata.modified()
                && let Ok(duration) = modified.duration_since(std::time::UNIX_EPOCH)
            {
                newest_mtime = newest_mtime.max(duration.as_secs());
            }
        }

        // 2. Parse each file and collect artifacts + imports + calls
        let mut parser = PythonParser::new()?;
        let mut all_artifacts = Vec::new();
        let mut all_imports = Vec::new();
        let mut all_calls = Vec::new();

        // Build module-to-file mapping for import resolution
        let mut module_to_file: HashMap<String, String> = HashMap::new();
        for file_path in &allowed_files {
            let relative = file_path
                .strip_prefix(&self.project_root)
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|_| file_path.to_string_lossy().to_string());
            let module = relative.trim_end_matches(".py").replace(['/', '\\'], ".");
            module_to_file.insert(module, relative);
        }

        for file_path in allowed_files {
            match parser.parse_file(&file_path) {
                Ok(parse_result) => {
                    stats.files_parsed += 1;

                    // Get relative path for source file
                    let relative_path = file_path
                        .strip_prefix(&self.project_root)
                        .map(|p| p.to_string_lossy().to_string())
                        .unwrap_or_else(|_| file_path.to_string_lossy().to_string());

                    // Extract imports BEFORE processing (since process consumes parse_result)
                    let imports = parse_result.imports.clone();

                    // Convert ImportInfo to ImportEdge
                    // For "from x import y, z" we create edges for x.y and x.z
                    for import_info in imports {
                        let base_module = if import_info.is_relative {
                            self.resolve_relative_import(&relative_path, &import_info)
                        } else {
                            import_info.module_name.clone()
                        };

                        let import_type = if import_info.is_wildcard {
                            ImportType::Wildcard
                        } else if import_info.is_relative {
                            ImportType::Relative
                        } else if import_info.imported_names.is_empty() {
                            ImportType::Module
                        } else {
                            ImportType::From
                        };

                        // For "from x import y, z" create edges for each imported name
                        if import_info.imported_names.is_empty() {
                            // Simple import: "import x" or "from . import x"
                            let target_file = module_to_file
                                .get(&base_module)
                                .cloned()
                                .unwrap_or_else(|| format!("{}.py", base_module.replace('.', "/")));

                            all_imports.push(ImportEdge {
                                source_file: relative_path.clone(),
                                target_file,
                                import_name: base_module,
                                import_type,
                                line_number: import_info.line_number,
                                alias: import_info.alias.clone(),
                                is_wildcard: import_info.is_wildcard,
                            });
                        } else {
                            // "from x import y, z" - create edge for each imported name
                            for imported_name in &import_info.imported_names {
                                // Full path: base_module.imported_name (e.g., app.crud)
                                let full_import = if base_module.is_empty() {
                                    imported_name.clone()
                                } else {
                                    format!("{}.{}", base_module, imported_name)
                                };

                                // Try to resolve to file: first try full path, then base module
                                let target_file = module_to_file
                                    .get(&full_import)
                                    .or_else(|| module_to_file.get(&base_module))
                                    .cloned()
                                    .unwrap_or_else(|| {
                                        format!("{}.py", full_import.replace('.', "/"))
                                    });

                                all_imports.push(ImportEdge {
                                    source_file: relative_path.clone(),
                                    target_file,
                                    import_name: full_import,
                                    import_type,
                                    line_number: import_info.line_number,
                                    alias: import_info.alias.clone(),
                                    is_wildcard: import_info.is_wildcard,
                                });
                            }
                        }
                    }

                    // Extract calls and convert to CallEdge
                    let module_path = relative_path
                        .trim_end_matches(".py")
                        .replace(['/', '\\'], ".");
                    for call_info in &parse_result.calls {
                        // Build fully qualified caller name
                        let caller_qualified = if call_info.caller_name.is_empty() {
                            module_path.clone()
                        } else {
                            format!("{}.{}", module_path, call_info.caller_name)
                        };

                        // Determine call type
                        let call_type = if call_info.is_async {
                            CallType::Async
                        } else if call_info.is_method {
                            CallType::Method
                        } else {
                            CallType::Direct
                        };

                        all_calls.push(CallEdge::new(
                            caller_qualified,
                            &call_info.callee_name,
                            call_type,
                            call_info.line_number,
                            &relative_path,
                        ));
                    }

                    // Process artifacts
                    let processor = ArtifactProcessor::new(&self.project_root);
                    let artifacts = processor.process(parse_result, &file_path)?;

                    for artifact in &artifacts {
                        stats.add_artifact(artifact.kind);
                    }

                    all_artifacts.extend(artifacts);
                }
                Err(e) => {
                    warn!(
                        file = %file_path.display(),
                        error = %e,
                        "Failed to parse file"
                    );
                    stats.files_failed += 1;
                    failed_files.push(ranex_core::FileInfo {
                        path: file_path,
                        hash: String::new(),
                        last_modified: 0,
                        status: ranex_core::FileStatus::Failed,
                        error: Some(e.to_string()),
                        line_count: 0,
                        artifact_count: 0,
                    });
                }
            }
        }

        fastapi_dependencies::expand_dependency_chains(&mut all_artifacts);
        fastapi_dependencies::highlight_auth_enforcement(&mut all_artifacts, &all_calls);

        // 3. Store artifacts in database (UPSERT deduplicates by qualified_name)
        self.repository.store_artifacts(&all_artifacts)?;

        // 3b. Store imports in database
        self.repository.store_imports(&all_imports)?;

        // 3c. Store call edges in database
        self.repository.store_call_edges(&all_calls)?;

        info!(
            import_count = all_imports.len(),
            call_count = all_calls.len(),
            "Stored imports and calls"
        );

        // 4. Get actual stored count (may differ from processed count due to UPSERT deduplication)
        let actual_stored = self.repository.count_artifacts()?;

        // Log if there's a significant difference (indicates duplicate qualified_names)
        let duplicates = stats.artifacts_found.saturating_sub(actual_stored as usize);
        if duplicates > 0 {
            debug!(
                processed = stats.artifacts_found,
                stored = actual_stored,
                duplicates = duplicates,
                "Some artifacts had duplicate qualified_names and were merged"
            );
        }

        // Update stats to reflect actual stored count
        stats.artifacts_found = actual_stored as usize;

        // 5. Save scan metadata for staleness detection (using mtime computed from actual scanned files)
        self.save_scan_metadata(newest_mtime)?;

        let duration = start.elapsed();
        let duration_ms = duration.as_millis() as u64;

        // 6. Record scan run for audit trail and last_scan_time()
        let git_head = get_git_head(&self.project_root);
        let git_branch = get_git_branch(&self.project_root);
        self.repository.record_scan_run(
            stats.artifacts_found,
            stats.files_scanned,
            stats.files_failed,
            duration_ms,
            git_head.as_deref(),
            git_branch.as_deref(),
        )?;

        info!(
            artifacts = stats.artifacts_found,
            files_parsed = stats.files_parsed,
            files_failed = stats.files_failed,
            duration_ms = duration_ms,
            "Scan complete"
        );

        Ok(ScanResult {
            stats,
            failed_files,
            duration_ms,
        })
    }

    /// Search for artifacts by symbol name.
    ///
    /// **Zero-config behavior**: If the index is empty AND `auto_scan_on_first_search`
    /// is enabled (default: true), automatically triggers a scan before searching.
    ///
    /// # Arguments
    /// * `query` - Search query (partial match on symbol name)
    /// * `limit` - Maximum number of results
    #[instrument(skip(self))]
    pub fn search(&mut self, query: &str, limit: usize) -> Result<Vec<Artifact>, AtlasError> {
        // Zero-config: auto-scan if index is empty
        self.ensure_indexed()?;

        debug!(query = query, limit = limit, "Searching artifacts");
        let artifacts = self.repository.search_by_symbol(query, limit)?;

        // Enforce SecurityConfig at retrieval time as a second line of defense
        // (Option A should already prevent denied files from being indexed).
        let filtered: Vec<Artifact> = artifacts
            .into_iter()
            .filter(|a| {
                let full_path = self.project_root.join(&a.file_path);
                self.is_path_allowed_by_security(&full_path)
            })
            .collect();

        Ok(filtered)
    }

    /// Search for artifacts by feature name.
    ///
    /// **Zero-config behavior**: Auto-scans if index is empty.
    #[instrument(skip(self))]
    pub fn search_by_feature(&mut self, feature: &str) -> Result<Vec<Artifact>, AtlasError> {
        // Zero-config: auto-scan if index is empty
        self.ensure_indexed()?;

        debug!(feature = feature, "Searching by feature");
        let artifacts = self.repository.search_by_feature(feature)?;

        let filtered: Vec<Artifact> = artifacts
            .into_iter()
            .filter(|a| {
                let full_path = self.project_root.join(&a.file_path);
                self.is_path_allowed_by_security(&full_path)
            })
            .collect();

        Ok(filtered)
    }

    /// Get a single artifact by exact qualified name.
    ///
    /// **Zero-config behavior**: Auto-scans if index is empty.
    #[instrument(skip(self))]
    pub fn get_by_qualified_name(
        &mut self,
        qualified_name: &str,
    ) -> Result<Option<Artifact>, AtlasError> {
        // Zero-config: auto-scan if index is empty
        self.ensure_indexed()?;

        debug!(
            qualified_name = qualified_name,
            "Getting artifact by qualified name"
        );
        let artifact = self.repository.get_by_qualified_name(qualified_name)?;

        // If, for any reason, an artifact from a denied file is still present
        // (e.g., stale database from older versions), treat it as not
        // accessible instead of leaking it.
        if let Some(a) = artifact {
            let full_path = self.project_root.join(&a.file_path);
            if self.is_path_allowed_by_security(&full_path) {
                Ok(Some(a))
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }

    /// Ensure the index is valid and fresh (zero-config auto-scan).
    ///
    /// Implements the ensure_index() contract from Engg Tech Spec §3.4:
    /// 1. If DB is empty → full scan
    /// 2. If index is stale → incremental scan (currently full scan)
    /// 3. If fresh → return immediately
    ///
    /// **Fail-closed semantics**: If the index cannot be guaranteed valid,
    /// this returns `AtlasError::Unavailable` instead of empty results.
    #[instrument(skip(self))]
    fn ensure_indexed(&mut self) -> Result<(), AtlasError> {
        // Check if auto-scan is enabled
        if !self.config.atlas.auto_scan_on_first_search {
            debug!("auto_scan_on_first_search disabled, skipping staleness check");
            return Ok(());
        }

        // Load scan metadata
        let metadata = self.load_scan_metadata()?;

        // Check for empty index (first run)
        let count = self.repository.count_artifacts()?;
        if count == 0 && metadata.last_scan_at == 0 {
            info!("Index is empty, performing initial scan (zero-config mode)");
            return self.scan().map(|_| ());
        }

        // Check staleness using three-strategy approach
        let staleness = check_staleness(
            &self.project_root,
            &metadata,
            staleness::DEFAULT_MAX_AGE_SECS,
            staleness::DEFAULT_MTIME_PROBE_BUDGET_MS,
        );

        match staleness {
            StalenessReason::Fresh => {
                debug!("Index is fresh, no scan needed");
                Ok(())
            }
            StalenessReason::NoPreviousScan => {
                info!("No previous scan found, performing full scan");
                self.scan().map(|_| ())
            }
            StalenessReason::GitHeadChanged { ref old, ref new } => {
                info!(
                    old_head = %old,
                    new_head = %new,
                    "Git HEAD changed, rescanning"
                );
                self.scan().map(|_| ())
            }
            StalenessReason::FileModified => {
                info!("File modifications detected, rescanning");
                self.scan().map(|_| ())
            }
            StalenessReason::MaxAgeExceeded { age_secs, max_secs } => {
                info!(
                    age_secs = age_secs,
                    max_secs = max_secs,
                    "Index exceeded max age, rescanning"
                );
                self.scan().map(|_| ())
            }
        }
    }

    /// Load scan metadata from the database.
    fn load_scan_metadata(&self) -> Result<ScanMetadata, AtlasError> {
        let mut metadata = ScanMetadata::default();

        // Load from metadata table
        if let Ok(Some(value)) = self.repository.get_metadata("last_known_latest_mtime") {
            metadata.last_known_latest_mtime = value.parse().unwrap_or(0);
        }

        if let Ok(Some(value)) = self.repository.get_metadata("last_git_commit")
            && !value.is_empty()
        {
            metadata.git_head = Some(value);
        }

        // Get last scan time from scan_runs
        if let Ok(Some(timestamp)) = self.repository.last_scan_time() {
            metadata.last_scan_at = timestamp as u64;
        }

        Ok(metadata)
    }

    /// Save scan metadata after a successful scan.
    fn save_scan_metadata(&self, newest_mtime: u64) -> Result<(), AtlasError> {
        // Save mtime
        self.repository
            .set_metadata("last_known_latest_mtime", &newest_mtime.to_string())?;

        // Save git info
        if let Some(head) = get_git_head(&self.project_root) {
            self.repository.set_metadata("last_git_commit", &head)?;
        }

        Ok(())
    }

    /// Resolve a relative import to an absolute module path.
    ///
    /// Example: In `app/api/routes.py`, `from .. import crud` -> `app.crud`
    fn resolve_relative_import(
        &self,
        source_file: &str,
        import_info: &parser::ImportInfo,
    ) -> String {
        // Get the directory of the source file
        let source_module = source_file
            .trim_end_matches(".py")
            .replace(['/', '\\'], ".");

        // Split into parts
        let parts: Vec<&str> = source_module.split('.').collect();

        // Calculate how many levels to go up
        let level = import_info.relative_level;

        // Go up `level` directories (but at least 1 for the file itself is already a module)
        let base_len = if parts.len() > level {
            parts.len() - level
        } else {
            0
        };

        let base: Vec<&str> = parts
            .get(..base_len)
            .map_or_else(Vec::new, |slice| slice.to_vec());

        // Append the import module name if any
        if import_info.module_name.is_empty() {
            base.join(".")
        } else if base.is_empty() {
            import_info.module_name.clone()
        } else {
            format!("{}.{}", base.join("."), import_info.module_name)
        }
    }

    /// Get count of indexed artifacts.
    pub fn count(&self) -> Result<i64, AtlasError> {
        self.repository.count_artifacts()
    }

    /// Get health status of the Atlas index.
    pub fn health(&self) -> Result<AtlasHealth, AtlasError> {
        let artifact_count = self.repository.count_artifacts()?;
        let last_scan = self.repository.last_scan_time()?;

        Ok(AtlasHealth {
            artifact_count,
            last_scan,
            db_path: self.config.db_path(&self.project_root),
        })
    }

    /// Get the project root path.
    pub fn project_root(&self) -> &Path {
        &self.project_root
    }

    // ========================================================================
    // Analysis Methods (Phase 1-4)
    // ========================================================================

    /// Run pattern detection on the indexed artifacts.
    ///
    /// Detects common architectural patterns like CRUD, Repository, Factory, etc.
    /// Results are persisted to the database for future queries.
    #[instrument(skip(self))]
    pub fn detect_patterns(&self) -> Result<Vec<analysis::DetectedPattern>, AtlasError> {
        let artifacts = self.repository.get_all_artifacts()?;

        if artifacts.is_empty() {
            info!("No artifacts found, skipping pattern detection");
            return Ok(Vec::new());
        }

        debug!(
            artifact_count = artifacts.len(),
            "Retrieved artifacts for pattern detection"
        );

        let detector = analysis::PatternDetector::new(&artifacts).with_min_confidence(0.5);

        let patterns = detector.detect_all();

        // Clear old patterns and store new ones
        self.repository.clear_patterns()?;
        self.repository.store_patterns(&patterns)?;

        info!(pattern_count = patterns.len(), "Detected patterns");
        Ok(patterns)
    }

    /// Get all detected patterns from the database.
    pub fn get_patterns(&self) -> Result<Vec<analysis::DetectedPattern>, AtlasError> {
        self.repository.get_all_patterns()
    }

    /// Get patterns of a specific type.
    pub fn get_patterns_by_type(
        &self,
        pattern_type: analysis::PatternType,
    ) -> Result<Vec<analysis::DetectedPattern>, AtlasError> {
        self.repository.get_patterns_by_type(pattern_type)
    }

    /// Build an in-memory dependency graph from stored imports.
    ///
    /// Use this for impact analysis and dependency queries.
    pub fn build_dependency_graph(&self) -> Result<analysis::DependencyGraph, AtlasError> {
        let imports = self.repository.get_all_imports()?;
        Ok(analysis::DependencyGraph::from_edges(imports))
    }

    /// Build an in-memory call graph from stored call edges.
    pub fn build_call_graph(&self) -> Result<analysis::CallGraph, AtlasError> {
        let edges = self.repository.get_all_call_edges()?;
        Ok(analysis::CallGraph::from_edges(edges))
    }

    /// Analyze the impact of changing a specific function.
    ///
    /// Returns a report showing:
    /// - Direct callers (functions that call this one)
    /// - Transitive callers (functions that indirectly depend on it)
    /// - API endpoints affected
    /// - Test files that cover the function
    /// - Overall risk level
    #[instrument(skip(self))]
    pub fn analyze_function_impact(
        &self,
        qualified_name: &str,
    ) -> Result<analysis::ImpactReport, AtlasError> {
        let call_graph = self.build_call_graph()?;
        let dep_graph = self.build_dependency_graph()?;
        let artifacts = self.repository.get_all_artifacts()?;

        let analyzer = analysis::ImpactAnalyzer::new(&call_graph, &dep_graph)
            .with_artifacts(&artifacts)
            .with_max_depth(10);

        Ok(analyzer.analyze_function(qualified_name))
    }

    /// Analyze the impact of changing a file.
    ///
    /// Returns a report showing:
    /// - Direct importers (files that import this one)
    /// - Transitive importers (files that indirectly depend on it)
    /// - Test files affected
    /// - Overall risk level
    #[instrument(skip(self))]
    pub fn analyze_file_impact(
        &self,
        file_path: &str,
    ) -> Result<analysis::ImpactReport, AtlasError> {
        let call_graph = self.build_call_graph()?;
        let dep_graph = self.build_dependency_graph()?;

        let analyzer = analysis::ImpactAnalyzer::new(&call_graph, &dep_graph).with_max_depth(10);

        Ok(analyzer.analyze_file(file_path))
    }

    /// Build a FastAPI Truth Capsule for a specific endpoint.
    ///
    /// This is a Phase 1 implementation that relies on existing Atlas artifacts
    /// and call graph data. It does not yet use the dedicated FastAPI tables
    /// described in TO-ADD.md.
    #[instrument(err, skip(self, request))]
    pub fn fastapi_truth_capsule(
        &mut self,
        request: analysis::FastapiTruthCapsuleRequest,
    ) -> Result<analysis::TruthCapsule, AtlasError> {
        self.ensure_indexed()?;

        let artifacts = self.repository.get_all_artifacts()?;
        let call_graph = self.build_call_graph()?;

        let start = std::time::Instant::now();
        let mut capsule = analysis::fastapi_truth_capsule::build_truth_capsule(
            &artifacts,
            &call_graph,
            &request,
        )?;
        let elapsed_ms = start.elapsed().as_millis() as u64;

        if capsule.stats.elapsed_ms == 0 {
            capsule.stats.elapsed_ms = elapsed_ms;
        }

        Ok(capsule)
    }

    /// Analyze FastAPI scalability using the configured policy.
    #[instrument(err, skip(self))]
    pub fn analyze_fastapi_scaling(&mut self) -> Result<analysis::FastapiScalingReport, AtlasError> {
        self.ensure_indexed()?;

        let policy = analysis::FastapiScalingPolicy::load(&self.project_root)?;
        let mut parser = PythonParser::new()?;
        let walker = FileWalker::new(&self.project_root, &self.config.atlas)?;
        let python_files = walker.find_python_files()?;

        // Enforce SecurityConfig: do not analyze denied files.
        let mut allowed_files = Vec::new();
        for path in python_files {
            if self.is_path_allowed_by_security(&path) {
                allowed_files.push(path);
            } else {
                debug!(
                    file = %path.display(),
                    "Skipping file denied by security configuration during FastAPI scaling analysis"
                );
            }
        }

        let mut definitions = Vec::new();

        for file_path in allowed_files {
            match parser.parse_file(&file_path) {
                Ok(parse_result) => {
                    let relative_path = file_path
                        .strip_prefix(&self.project_root)
                        .map(|p| p.to_string_lossy().to_string())
                        .unwrap_or_else(|_| file_path.to_string_lossy().to_string());

                    let module_path = relative_path
                        .trim_end_matches(".py")
                        .replace(['/', '\\'], ".");

                    for definition in parse_result.definitions {
                        definitions.push(analysis::ParsedDefinition {
                            definition,
                            file_path: relative_path.clone(),
                            module_path: module_path.clone(),
                        });
                    }
                }
                Err(e) => {
                    warn!(
                        file = %file_path.display(),
                        error = %e,
                        "Failed to parse file during FastAPI scaling analysis"
                    );
                }
            }
        }

        let call_graph = self.build_call_graph()?;

        Ok(analysis::analyze_definitions(
            &policy,
            &definitions,
            &call_graph,
        ))
    }

    /// Analyze FastAPI router topology: routers, prefixes, includes, and direct app routes.
    #[instrument(err, skip(self))]
    pub fn analyze_fastapi_router_topology(&mut self) -> Result<RouterTopologyReport, AtlasError> {
        self.ensure_indexed()?;

        let mut parser = PythonParser::new()?;
        let walker = FileWalker::new(&self.project_root, &self.config.atlas)?;
        let python_files = walker.find_python_files()?;

        // Enforce SecurityConfig: do not analyze denied files.
        let mut allowed_files = Vec::new();
        for path in python_files {
            if self.is_path_allowed_by_security(&path) {
                allowed_files.push(path);
            } else {
                debug!(
                    file = %path.display(),
                    "Skipping file denied by security configuration during router topology analysis"
                );
            }
        }

        let mut definitions = Vec::new();

        for file_path in allowed_files {
            match parser.parse_file(&file_path) {
                Ok(parse_result) => {
                    let relative_path = file_path
                        .strip_prefix(&self.project_root)
                        .map(|p| p.to_string_lossy().to_string())
                        .unwrap_or_else(|_| file_path.to_string_lossy().to_string());

                    let module_path = relative_path
                        .trim_end_matches(".py")
                        .replace(['/', '\\'], ".");

                    for definition in parse_result.definitions {
                        definitions.push(analysis::ParsedDefinition {
                            definition,
                            file_path: relative_path.clone(),
                            module_path: module_path.clone(),
                        });
                    }
                }
                Err(e) => {
                    warn!(
                        file = %file_path.display(),
                        error = %e,
                        "Failed to parse file during FastAPI router topology analysis"
                    );
                }
            }
        }

        Ok(analyze_router_topology(&definitions))
    }

    // ========================================================================
    // Span-First Retrieval & Safe File Utilities
    // ========================================================================

    /// Read a span of lines from a file, enforcing Atlas security configuration.
    ///
    /// Line numbers are 1-indexed and inclusive. The `file_path` is interpreted
    /// relative to the Atlas `project_root`.
    #[instrument(err, skip(self, max_bytes), fields(file_path = file_path))]
    pub fn read_span(
        &self,
        file_path: &str,
        line_start: usize,
        line_end: usize,
        max_bytes: usize,
    ) -> Result<String, AtlasError> {
        if line_start == 0 || line_end < line_start {
            return Err(AtlasError::parse(
                self.project_root.join(file_path),
                format!("Invalid span range: {}-{}", line_start, line_end),
            ));
        }

        let full_path = self.project_root.join(file_path);

        if !self.is_path_allowed_by_security(&full_path) {
            return Err(AtlasError::unavailable(
                format!(
                    "Access to '{}' is denied by security configuration",
                    full_path.display()
                ),
                false,
            ));
        }

        let file = File::open(&full_path)?;
        let reader = BufReader::new(file);

        let mut snippet = String::new();
        let mut bytes_written: usize = 0;

        for (idx, line_res) in reader.lines().enumerate() {
            let line_no = idx + 1;

            if line_no < line_start {
                continue;
            }
            if line_no > line_end {
                break;
            }

            let line = line_res.map_err(|e| AtlasError::Parse {
                path: full_path.clone(),
                message: format!("Failed to read line {}: {}", line_no, e),
            })?;

            let projected = bytes_written
                .saturating_add(line.len())
                .saturating_add(1); // account for newline

            if projected > max_bytes {
                break;
            }

            snippet.push_str(&line);
            snippet.push('\n');
            bytes_written = projected;
        }

        if snippet.is_empty() {
            return Err(AtlasError::parse(
                full_path,
                format!(
                    "Requested span {}-{} produced no content (file may be shorter)",
                    line_start, line_end
                ),
            ));
        }

        Ok(snippet)
    }

    /// Glob for Python files under the project root, respecting Atlas ignore and
    /// security configuration.
    #[instrument(err, skip(self), fields(pattern = pattern, limit = limit))]
    pub fn glob_python_files(
        &self,
        pattern: &str,
        limit: usize,
    ) -> Result<Vec<PathBuf>, AtlasError> {
        if limit == 0 {
            return Ok(Vec::new());
        }

        let glob_pattern = Pattern::new(pattern).map_err(|e| {
            AtlasError::walk(
                &self.project_root,
                format!("Invalid glob pattern '{}': {}", pattern, e),
            )
        })?;

        let walker = FileWalker::new(&self.project_root, &self.config.atlas)?;
        let python_files = walker.find_python_files()?;

        let mut results = Vec::new();

        for path in python_files {
            if !self.is_path_allowed_by_security(&path) {
                continue;
            }

            let relative = path
                .strip_prefix(&self.project_root)
                .unwrap_or(&path)
                .to_path_buf();
            let rel_str = relative.to_string_lossy();

            if glob_pattern.matches(&rel_str) {
                results.push(relative);
                if results.len() >= limit {
                    break;
                }
            }
        }

        Ok(results)
    }

    /// Grep-style text search over Python files, returning span-level matches.
    ///
    /// This uses a simple substring search (no regular expressions) and respects
    /// Atlas ignore + security configuration.
    #[instrument(err, skip(self), fields(query = query, limit = limit))]
    pub fn grep_spans(
        &self,
        query: &str,
        limit: usize,
        path_glob: Option<&str>,
    ) -> Result<Vec<SpanResult>, AtlasError> {
        if query.trim().is_empty() || limit == 0 {
            return Ok(Vec::new());
        }

        let glob_pattern = if let Some(glob) = path_glob {
            Some(
                Pattern::new(glob).map_err(|e| {
                    AtlasError::walk(
                        &self.project_root,
                        format!("Invalid glob pattern '{}': {}", glob, e),
                    )
                })?,
            )
        } else {
            None
        };

        let walker = FileWalker::new(&self.project_root, &self.config.atlas)?;
        let python_files = walker.find_python_files()?;

        let mut results = Vec::new();

        for path in python_files {
            if !self.is_path_allowed_by_security(&path) {
                continue;
            }

            let relative = path
                .strip_prefix(&self.project_root)
                .unwrap_or(&path)
                .to_path_buf();
            let rel_str = relative.to_string_lossy();

            if let Some(ref pat) = glob_pattern
                && !pat.matches(&rel_str)
            {
                continue;
            }

            let file = File::open(&path)?;
            let reader = BufReader::new(file);

            for (idx, line_res) in reader.lines().enumerate() {
                let line_no = idx + 1;
                let line = line_res.map_err(|e| AtlasError::Parse {
                    path: path.clone(),
                    message: format!("Failed to read line {}: {}", line_no, e),
                })?;

                if line.contains(query) {
                    results.push(SpanResult {
                        file_path: relative.clone(),
                        line_start: line_no,
                        line_end: line_no,
                        kind: None,
                        score: 0.0,
                        evidence_type: SpanEvidenceType::Grep,
                        snippet: None,
                    });

                    if results.len() >= limit {
                        return Ok(results);
                    }
                }
            }
        }

        Ok(results)
    }

    /// Hybrid span-first search that fuses structured Atlas artifacts with
    /// text-based grep evidence.
    ///
    /// This is a deterministic, multi-source retrieval path designed so that
    /// higher layers (e.g., MCP tools) can expose SWE-grep-style `(file, span)`
    /// results without needing to implement their own query planner.
    #[instrument(err, skip(self), fields(query = query, limit = limit))]
    pub fn search_spans(
        &mut self,
        query: &str,
        limit: usize,
    ) -> Result<Vec<SpanResult>, AtlasError> {
        if query.trim().is_empty() || limit == 0 {
            return Ok(Vec::new());
        }

        // Ensure index is ready (zero-config contract)
        self.ensure_indexed()?;

        let max_candidates = limit.saturating_mul(4).max(limit);
        let query_lower = query.to_lowercase();

        // Stage 1: structured Atlas artifacts (primary evidence)
        let artifacts = self.repository.search_by_symbol(query, max_candidates)?;

        // Decide whether to use the call graph based on query shape to avoid
        // unnecessary overhead for path/model-oriented queries.
        let use_call_graph = looks_function_like(query);

        let call_graph = if use_call_graph && !artifacts.is_empty() {
            Some(self.build_call_graph()?)
        } else {
            None
        };

        use std::collections::HashMap;

        let mut spans: HashMap<(String, usize, usize), SpanResult> = HashMap::new();

        for (rank, artifact) in artifacts.iter().enumerate() {
            // Enforce SecurityConfig at retrieval time; Option A should prevent
            // denied files from being indexed, but this guards against stale
            // databases.
            let full_path = self.project_root.join(&artifact.file_path);
            if !self.is_path_allowed_by_security(&full_path) {
                continue;
            }

            let rel_path = artifact.file_path.to_string_lossy().to_string();
            let key = (rel_path.clone(), artifact.line_start, artifact.line_end);

            // Base score decays with rank and is then boosted by artifact-aware
            // features (kind, exact/partial matches, feature/file/tags, routes).
            let base_score = 1.0f32 / (1.0 + rank as f32);
            let boost = artifact_rel_score(&query_lower, artifact, call_graph.as_ref());
            let total_score = base_score + boost;

            let entry = spans.entry(key).or_insert_with(|| SpanResult {
                file_path: artifact.file_path.clone(),
                line_start: artifact.line_start,
                line_end: artifact.line_end,
                kind: Some(artifact.kind.as_str().to_string()),
                score: 0.0,
                evidence_type: SpanEvidenceType::Artifact,
                snippet: None,
            });

            entry.score += total_score;
        }

        // Stage 2: grep-based evidence (fallback + additional coverage).
        // Grep hits are deliberately de-emphasized relative to structured
        // artifacts to keep precision high while still surfacing novel spans.
        let grep_limit = max_candidates.saturating_mul(2);
        let grep_spans = self.grep_spans(query, grep_limit, None)?;

        for (rank, span) in grep_spans.into_iter().enumerate() {
            let rel_path = span.file_path.to_string_lossy().to_string();
            let key = (rel_path.clone(), span.line_start, span.line_end);

            // Start below artifact scores and apply a small path-based bonus when
            // the file path itself strongly matches the query.
            let mut base_score = 1.0f32 / (2.0 + rank as f32);
            base_score *= 0.5; // global dampening for grep-only evidence

            if rel_path.to_lowercase().contains(&query_lower) {
                base_score += 0.25;
            }

            let entry = spans.entry(key).or_insert_with(|| SpanResult {
                file_path: span.file_path.clone(),
                line_start: span.line_start,
                line_end: span.line_end,
                kind: None,
                score: 0.0,
                evidence_type: SpanEvidenceType::Grep,
                snippet: None,
            });

            entry.score += base_score;

            // Preserve Artifact as primary evidence if present; otherwise mark as Grep.
            if matches!(entry.evidence_type, SpanEvidenceType::Artifact) {
                // keep existing evidence_type
            } else {
                entry.evidence_type = SpanEvidenceType::Grep;
            }
        }

        let mut span_list: Vec<SpanResult> = spans.into_values().collect();

        span_list.sort_by(|a, b| b
            .score
            .partial_cmp(&a.score)
            .unwrap_or(std::cmp::Ordering::Equal));

        span_list.truncate(limit);

        // Stage 3: hydrate snippets for top spans (bounded by max_bytes)
        for span in &mut span_list {
            let rel = span.file_path.to_string_lossy();
            let start = span.line_start.saturating_sub(2);
            let end = span.line_end + 2;
            // Best-effort snippet; errors bubble up to preserve fail-closed semantics.
            let snippet = self.read_span(&rel, start.max(1), end, 8_192)?;
            span.snippet = Some(snippet);
        }

        Ok(span_list)
    }

    /// Get all files that depend on the given file (reverse dependency).
    pub fn get_dependents(&self, file_path: &str) -> Result<Vec<String>, AtlasError> {
        let dep_graph = self.build_dependency_graph()?;
        Ok(dep_graph.get_transitive_dependents(file_path, 10))
    }

    /// Get all files that the given file depends on.
    pub fn get_dependencies(&self, file_path: &str) -> Result<Vec<String>, AtlasError> {
        let dep_graph = self.build_dependency_graph()?;
        Ok(dep_graph.get_transitive_dependencies(file_path, 10))
    }

    /// Find duplicate/similar code patterns.
    pub fn find_duplicates(&self) -> Result<Vec<analysis::DuplicateMatch>, AtlasError> {
        let artifacts = self.repository.get_all_artifacts()?;

        let detector = analysis::DuplicateDetector::new(&artifacts)
            .with_threshold(analysis::SimilarityScore::new(0.75));

        Ok(detector.find_duplicates())
    }

    /// Detect dependency cycles in the import graph.
    pub fn detect_cycles(&self) -> Result<Vec<Vec<String>>, AtlasError> {
        let dep_graph = self.build_dependency_graph()?;
        Ok(dep_graph.detect_cycles())
    }
}

impl Atlas {
    /// Apply `SecurityConfig` rules to determine whether a path is readable
    /// by AI-facing Atlas utilities.
    fn is_path_allowed_by_security(&self, path: &Path) -> bool {
        let security = &self.config.security;

        // Normalize to an absolute path for consistent checks
        let full_path = if path.is_absolute() {
            path.to_path_buf()
        } else {
            self.project_root.join(path)
        };

        // Compute project-relative path where possible; pattern semantics are
        // defined in terms of paths relative to the project root.
        let rel_path = full_path
            .strip_prefix(&self.project_root)
            .unwrap_or(&full_path)
            .to_path_buf();

        // Denied directories take precedence
        for component in rel_path.components() {
            if let std::path::Component::Normal(name) = component {
                let name_str = name.to_string_lossy();
                if security
                    .denied_directories
                    .iter()
                    .any(|d| d == &*name_str)
                {
                    return false;
                }
            }
        }

        // Extension-based rules
        let ext = rel_path
            .extension()
            .and_then(|e| e.to_str())
            .unwrap_or("");

        if security
            .denied_extensions
            .iter()
            .any(|d| d == ext)
        {
            return false;
        }

        if security.strict_mode
            && !security.allowed_extensions.is_empty()
            && !security.allowed_extensions.iter().any(|a| a == ext)
        {
            return false;
        }

        // Denied file patterns (glob)
        let rel_str = rel_path.to_string_lossy();
        let file_name = rel_path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("");

        for pattern_str in &security.denied_file_patterns {
            match Pattern::new(pattern_str) {
                Ok(pattern) => {
                    if pattern.matches(&rel_str) || pattern.matches(file_name) {
                        return false;
                    }
                }
                Err(e) => {
                    // Fail closed on invalid patterns: log and deny access.
                    warn!(
                        pattern = pattern_str,
                        error = %e,
                        "Invalid denied_file_pattern; failing closed"
                    );
                    return false;
                }
            }
        }

        true
    }
}

/// Health status of the Atlas index.
#[derive(Debug, Clone)]
pub struct AtlasHealth {
    /// Number of indexed artifacts
    pub artifact_count: i64,

    /// Timestamp of last scan (Unix epoch)
    pub last_scan: Option<i64>,

    /// Path to the database file
    pub db_path: PathBuf,
}

/// Span-level search result used for precise, verifiable retrieval.
///
/// This struct is intentionally minimal and focused on the SWE-grep-style
/// contract of returning concrete file spans instead of summaries.
#[derive(Debug, Clone, Serialize)]
pub struct SpanResult {
    /// File path relative to the project root
    pub file_path: PathBuf,

    /// Start line (1-indexed, inclusive)
    pub line_start: usize,

    /// End line (1-indexed, inclusive)
    pub line_end: usize,

    /// Optional artifact kind, when this span comes from a structured Atlas artifact
    pub kind: Option<String>,

    /// Fused relevance score from all retrieval sources (higher is better)
    pub score: f32,

    /// Primary evidence type used to retrieve this span
    pub evidence_type: SpanEvidenceType,

    /// Optional snippet text for this span (bounded by a max_bytes budget)
    pub snippet: Option<String>,
}

/// Evidence type for span-level results.
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SpanEvidenceType {
    /// Span came from a structured Atlas artifact (symbol-level match)
    Artifact,

    /// Span came from a text search (grep-style pattern match)
    Grep,
}

/// Heuristic to determine whether a query likely refers to a function-like
/// symbol (as opposed to a path, route, or model name). Used to decide when
/// call-graph-based boosting is worth the overhead.
fn looks_function_like(query: &str) -> bool {
    let q = query.trim();
    if q.is_empty() {
        return false;
    }

    // Route/path queries usually contain '/' or whitespace; skip call graph
    if q.contains('/') || q.contains(' ') {
        return false;
    }

    // If the query contains parentheses, treat it as function-like
    if q.contains('(') || q.contains(')') {
        return true;
    }

    // Underscore or dot are common in function/qualified names
    if q.contains('_') || q.contains('.') {
        return true;
    }

    // Fallback: short alphanumeric tokens are treated as potentially
    // function-like; longer mixed-case identifiers could be classes/models.
    let is_simple_alnum = q
        .chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '_');

    is_simple_alnum && q.len() <= 40
}

/// Compute an artifact-aware relevance boost for a given query and artifact.
///
/// This is intentionally heuristic but deterministic and only depends on
/// structured Atlas metadata and (optionally) the call graph, not on any
/// external scoring system. Higher values indicate a stronger semantic match
/// and are combined with the rank-based base score in `search_spans`.
fn artifact_rel_score(query_lower: &str, artifact: &Artifact, call_graph: Option<&CallGraph>) -> f32 {
    let mut score = 0.0f32;

    let name_lower = artifact.symbol_name.to_lowercase();
    let qualified_lower = artifact.qualified_name.to_lowercase();
    let module_lower = artifact.module_path.to_lowercase();
    let file_lower = artifact.file_path.to_string_lossy().to_lowercase();

    // Exact symbol name match gets a strong boost.
    if name_lower == query_lower {
        score += 3.0;
    } else if name_lower.contains(query_lower) {
        score += 1.5;
    }

    // Qualified name and module path matches support queries like
    // "app.billing.calculate_tax" or "payment".
    if qualified_lower == query_lower {
        score += 2.0;
    } else if qualified_lower.contains(query_lower) {
        score += 1.0;
    }

    if module_lower.contains(query_lower) {
        score += 0.75;
    }

    // File path match is weaker than symbol/qualified name but still useful
    // for queries like "payment" or "tax".
    if file_lower.contains(query_lower) {
        score += 0.5;
    }

    // Feature-based boost (e.g., "payment" feature).
    if let Some(ref feature) = artifact.feature
        && feature.to_lowercase().contains(query_lower)
    {
        score += 0.75;
    }

    // HTTP route metadata is highly indicative for endpoint-centric queries
    // like "/payments" or "GET /orders".
    if let Some(ref route_path) = artifact.route_path
        && route_path.to_lowercase().contains(query_lower)
    {
        score += 1.5;
    }

    if let Some(ref method) = artifact.http_method
        && method.to_lowercase().contains(query_lower)
    {
        score += 0.5;
    }

    // Tag-based boost (decorator-derived tags such as "fastapi_route",
    // "http_get", "contract", etc.).
    for tag in &artifact.tags {
        if tag.to_lowercase().contains(query_lower) {
            score += 0.25;
        }
    }

    // Adjust by artifact kind to slightly prioritize endpoints and contracts
    // for typical agent queries.
    match artifact.kind {
        ArtifactKind::Endpoint => {
            score += 0.5;
        }
        ArtifactKind::Contract => {
            score += 0.3;
        }
        ArtifactKind::Model => {
            score += 0.2;
        }
        _ => {}
    }

    // Call-graph-aware boosting: for function-like artifacts, prefer targets
    // that are heavily called (directly or transitively). This helps surface
    // central utilities and endpoints when the query is function-oriented.
    if let Some(graph) = call_graph {
        match artifact.kind {
            ArtifactKind::Function
            | ArtifactKind::AsyncFunction
            | ArtifactKind::Method
            | ArtifactKind::Endpoint => {
                let qname = &artifact.qualified_name;
                let direct_callers = graph.get_callers(qname).len() as f32;
                let transitive_callers = graph.get_transitive_callers(qname, 5).len() as f32;

                if direct_callers > 0.0 || transitive_callers > 0.0 {
                    // Bound contributions to avoid overpowering name/route
                    // matches while still preferring widely-used functions.
                    let direct_boost = direct_callers.min(10.0) * 0.1;
                    let trans_boost = transitive_callers.min(20.0) * 0.05;
                    score += direct_boost + trans_boost;
                }
            }
            _ => {}
        }
    }

    score
}
