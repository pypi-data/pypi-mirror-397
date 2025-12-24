//! # ranex-py
//!
//! Python bindings for the Ranex Atlas codebase indexing system.
//!
//! This crate exposes the Rust-powered Atlas scanner, parser, and storage
//! to Python via PyO3, enabling Python users to index and search their
//! codebases efficiently.
//!
//! ## Usage from Python
//!
//! ```python
//! from ranex_rust import Atlas
//!
//! # Initialize Atlas for a project
//! atlas = Atlas("/path/to/project")
//!
//! # Scan and index the codebase
//! result = atlas.scan()
//! print(f"Found {result['artifacts_found']} artifacts")
//!
//! # Search for symbols
//! results = atlas.search("payment", limit=10)
//! for artifact in results:
//!     print(f"{artifact['symbol_name']} in {artifact['file_path']}")
//! ```

mod error;
mod firewall;
mod types;

use error::PyAtlasError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use ranex_atlas::analysis;
use ranex_atlas::Atlas as RustAtlas;
use ranex_core::ArtifactKind;
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::LazyLock;
use tracing::{debug, info};

/// Atlas - Python interface to the Ranex codebase indexing system.
///
/// Atlas scans Python projects, extracts symbols (functions, classes, endpoints),
/// and stores them in SQLite for fast retrieval.
///
/// # Example
///
/// ```python
/// atlas = Atlas("/path/to/project")
/// atlas.scan()
/// results = atlas.search("calculate_tax")
/// ```
/// Note: `unsendable` is required because `rusqlite::Connection` is not `Sync`.
/// This means the Atlas instance cannot be shared between Python threads,
/// but can still be used from a single thread (which is the common case).
#[pyclass(name = "Atlas", unsendable)]
pub struct PyAtlas {
    inner: RustAtlas,
    project_root: PathBuf,
}

#[pymethods]
impl PyAtlas {
    /// Create a new Atlas instance for a project.
    ///
    /// Args:
    ///     project_root: Path to the Python project root directory.
    ///
    /// Returns:
    ///     Atlas instance ready for scanning.
    ///
    /// Raises:
    ///     RuntimeError: If the project root doesn't exist or database init fails.
    #[new]
    #[pyo3(signature = (project_root))]
    fn new(project_root: String) -> PyResult<Self> {
        let path = PathBuf::from(&project_root);

        // Validate path exists
        if !path.exists() {
            return Err(PyAtlasError::project_not_found(&project_root).into());
        }

        let inner = RustAtlas::new(&path).map_err(PyAtlasError::from)?;

        info!(project = %project_root, "Atlas initialized");

        Ok(Self {
            inner,
            project_root: path,
        })
    }

    /// Scan the project and index all Python files.
    ///
    /// This method walks the project directory, parses all Python files,
    /// extracts symbols (functions, classes, decorators), and stores them
    /// in the SQLite database.
    ///
    /// Returns:
    ///     dict: Scan statistics including:
    ///         - artifacts_found: Number of symbols indexed
    ///         - files_scanned: Total files processed
    ///         - files_parsed: Files successfully parsed
    ///         - files_failed: Files that failed parsing
    ///         - duration_ms: Scan duration in milliseconds
    ///
    /// Raises:
    ///     RuntimeError: If scanning fails due to I/O or database errors.
    fn scan(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        // Note: Cannot release GIL because rusqlite::Connection is not Sync.
        // This is acceptable for scanning which is typically a one-time operation.
        let result = self.inner.scan().map_err(PyAtlasError::from)?;

        // Convert ScanResult to Python dict
        let dict = types::scan_result_to_dict(py, &result)?;

        info!(
            artifacts = result.stats.artifacts_found,
            files = result.stats.files_scanned,
            "Scan complete"
        );

        Ok(dict.into())
    }

    /// Search for artifacts by symbol name.
    ///
    /// Performs a partial match search on symbol names (e.g., "payment"
    /// matches "process_payment", "PaymentRequest", etc.).
    ///
    /// Args:
    ///     query: Search query (partial match on symbol name).
    ///     limit: Maximum number of results (default: 100).
    ///
    /// Returns:
    ///     list[dict]: List of matching artifacts, each containing:
    ///         - symbol_name: Simple name (e.g., "calculate_tax")
    ///         - qualified_name: Full import path
    ///         - kind: Type (function, class, endpoint, etc.)
    ///         - file_path: Relative file path
    ///         - line_start: Starting line number
    ///         - line_end: Ending line number
    ///         - signature: Function signature (if applicable)
    ///         - docstring: Extracted docstring (if available)
    ///         - feature: Extracted feature name (if detected)
    ///         - tags: List of tags (e.g., ["fastapi_route"])
    ///
    /// Raises:
    ///     RuntimeError: If database query fails.
    #[pyo3(signature = (query, limit=None))]
    fn search(
        &mut self,
        py: Python<'_>,
        query: String,
        limit: Option<usize>,
    ) -> PyResult<Py<PyAny>> {
        let limit = limit.unwrap_or(100);

        let artifacts = self
            .inner
            .search(&query, limit)
            .map_err(PyAtlasError::from)?;

        debug!(query = %query, results = artifacts.len(), "Search completed");

        let list = types::artifacts_to_list(py, &artifacts)?;
        Ok(list.into())
    }

    /// Search for artifacts by feature name.
    ///
    /// Returns all artifacts belonging to a specific feature module
    /// (e.g., "payment" returns all symbols from payment-related files).
    ///
    /// Args:
    ///     feature: Feature name to search for.
    ///
    /// Returns:
    ///     list[dict]: List of artifacts in the feature.
    ///
    /// Raises:
    ///     RuntimeError: If database query fails.
    #[pyo3(signature = (feature))]
    fn search_by_feature(&mut self, py: Python<'_>, feature: String) -> PyResult<Py<PyAny>> {
        let artifacts = self
            .inner
            .search_by_feature(&feature)
            .map_err(PyAtlasError::from)?;

        debug!(feature = %feature, results = artifacts.len(), "Feature search completed");

        let list = types::artifacts_to_list(py, &artifacts)?;
        Ok(list.into())
    }

    /// Get the count of indexed artifacts.
    ///
    /// Returns:
    ///     int: Total number of artifacts in the index.
    ///
    /// Raises:
    ///     RuntimeError: If database query fails.
    fn count(&self, _py: Python<'_>) -> PyResult<i64> {
        Ok(self.inner.count().map_err(PyAtlasError::from)?)
    }

    /// Get health status of the Atlas index.
    ///
    /// Returns:
    ///     dict: Health information including:
    ///         - artifact_count: Number of indexed artifacts
    ///         - last_scan: Unix timestamp of last scan (or None)
    ///         - db_path: Path to the SQLite database
    ///         - status: "healthy" or "needs_scan"
    ///
    /// Raises:
    ///     RuntimeError: If health check fails.
    fn health(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let health = self.inner.health().map_err(PyAtlasError::from)?;

        let dict = PyDict::new(py);
        dict.set_item("artifact_count", health.artifact_count)?;
        dict.set_item("last_scan", health.last_scan)?;
        dict.set_item("db_path", health.db_path.to_string_lossy().to_string())?;

        let status = if health.artifact_count > 0 {
            "healthy"
        } else {
            "needs_scan"
        };
        dict.set_item("status", status)?;

        Ok(dict.into())
    }

    /// Get the project root path.
    ///
    /// Returns:
    ///     str: Absolute path to the project root.
    #[getter]
    fn project_root(&self) -> String {
        self.project_root.to_string_lossy().to_string()
    }

    /// String representation for debugging.
    fn __repr__(&self) -> String {
        format!(
            "Atlas(project_root='{}')",
            self.project_root.to_string_lossy()
        )
    }

    /// String representation.
    fn __str__(&self) -> String {
        self.__repr__()
    }

    // ========================================================================
    // Analysis Methods (Phase 1-4)
    // ========================================================================

    /// Detect architectural patterns in the codebase.
    ///
    /// Analyzes indexed artifacts to detect common patterns like:
    /// - CRUD: Services with create/read/update/delete methods
    /// - Repository: Data access layer pattern
    /// - Factory: Object creation pattern
    /// - ServiceLayer: Business logic encapsulation
    ///
    /// Returns:
    ///     list[dict]: Detected patterns, each containing:
    ///         - pattern_type: Type of pattern (crud, repository, etc.)
    ///         - name: Name of the class implementing the pattern
    ///         - file_path: File where the pattern is found
    ///         - confidence: Detection confidence (0.0-1.0)
    ///         - explanation: Human-readable explanation
    ///
    /// Raises:
    ///     RuntimeError: If pattern detection fails.
    fn detect_patterns(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let patterns = self.inner.detect_patterns().map_err(PyAtlasError::from)?;

        let list = pyo3::types::PyList::empty(py);
        for pattern in &patterns {
            let dict = PyDict::new(py);
            dict.set_item("pattern_type", pattern.pattern_type.as_str())?;
            dict.set_item("name", &pattern.name)?;
            dict.set_item("file_path", &pattern.file_path)?;
            dict.set_item("confidence", pattern.confidence.value())?;
            dict.set_item("artifacts", &pattern.artifacts)?;
            dict.set_item("indicators", &pattern.indicators)?;
            dict.set_item("explanation", &pattern.explanation)?;
            list.append(dict)?;
        }

        info!(pattern_count = patterns.len(), "Pattern detection complete");
        Ok(list.into())
    }

    /// Get all detected patterns from the database.
    ///
    /// Returns patterns detected by a previous `detect_patterns()` call.
    ///
    /// Returns:
    ///     list[dict]: Detected patterns.
    fn get_patterns(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let patterns = self.inner.get_patterns().map_err(PyAtlasError::from)?;

        let list = pyo3::types::PyList::empty(py);
        for pattern in &patterns {
            let dict = PyDict::new(py);
            dict.set_item("pattern_type", pattern.pattern_type.as_str())?;
            dict.set_item("name", &pattern.name)?;
            dict.set_item("file_path", &pattern.file_path)?;
            dict.set_item("confidence", pattern.confidence.value())?;
            dict.set_item("artifacts", &pattern.artifacts)?;
            dict.set_item("indicators", &pattern.indicators)?;
            dict.set_item("explanation", &pattern.explanation)?;
            list.append(dict)?;
        }
        Ok(list.into())
    }

    /// Analyze the impact of changing a function.
    ///
    /// Predicts the blast radius of modifying a specific function.
    ///
    /// Args:
    ///     qualified_name: Fully qualified name of the function
    ///                    (e.g., "app.services.orders.OrderService.get_order").
    ///
    /// Returns:
    ///     dict: Impact report containing:
    ///         - target: The function being analyzed
    ///         - risk_level: Overall risk (none, low, medium, high, critical)
    ///         - direct_callers: Number of functions that directly call this one
    ///         - transitive_callers: Functions that indirectly depend on it
    ///         - test_files: Number of test files that cover this function
    ///         - api_endpoints: Number of API endpoints affected
    ///         - summary: Human-readable summary
    ///         - affected_items: List of affected items with details
    ///
    /// Raises:
    ///     RuntimeError: If analysis fails.
    #[pyo3(signature = (qualified_name))]
    fn analyze_function_impact(
        &self,
        py: Python<'_>,
        qualified_name: String,
    ) -> PyResult<Py<PyAny>> {
        let report = self
            .inner
            .analyze_function_impact(&qualified_name)
            .map_err(PyAtlasError::from)?;

        let dict = PyDict::new(py);
        dict.set_item("target", &report.target)?;
        dict.set_item("risk_level", report.risk_level.as_str())?;
        dict.set_item("direct_callers", report.stats.direct_callers)?;
        dict.set_item("transitive_callers", report.stats.transitive_callers)?;
        dict.set_item("test_files", report.stats.test_files)?;
        dict.set_item("api_endpoints", report.stats.api_endpoints)?;
        dict.set_item("summary", &report.summary)?;

        // Add affected items
        let items_list = pyo3::types::PyList::empty(py);
        for item in &report.affected_items {
            let item_dict = PyDict::new(py);
            item_dict.set_item("qualified_name", &item.qualified_name)?;
            item_dict.set_item("file_path", &item.file_path)?;
            item_dict.set_item("impact_type", item.impact_type.as_str())?;
            item_dict.set_item("distance", item.distance)?;
            item_dict.set_item("line_number", item.line_number)?;
            items_list.append(item_dict)?;
        }
        dict.set_item("affected_items", items_list)?;

        Ok(dict.into())
    }

    /// Analyze the impact of changing a file.
    ///
    /// Predicts the blast radius of modifying a specific file.
    ///
    /// Args:
    ///     file_path: Relative path to the file (e.g., "app/services/orders.py").
    ///
    /// Returns:
    ///     dict: Impact report (same structure as analyze_function_impact).
    ///
    /// Raises:
    ///     RuntimeError: If analysis fails.
    #[pyo3(signature = (file_path))]
    fn analyze_file_impact(&self, py: Python<'_>, file_path: String) -> PyResult<Py<PyAny>> {
        let report = self
            .inner
            .analyze_file_impact(&file_path)
            .map_err(PyAtlasError::from)?;

        let dict = PyDict::new(py);
        dict.set_item("target", &report.target)?;
        dict.set_item("risk_level", report.risk_level.as_str())?;
        dict.set_item("direct_importers", report.stats.direct_importers)?;
        dict.set_item("transitive_importers", report.stats.transitive_importers)?;
        dict.set_item("test_files", report.stats.test_files)?;
        dict.set_item("summary", &report.summary)?;

        // Add affected items
        let items_list = pyo3::types::PyList::empty(py);
        for item in &report.affected_items {
            let item_dict = PyDict::new(py);
            item_dict.set_item("qualified_name", &item.qualified_name)?;
            item_dict.set_item("file_path", &item.file_path)?;
            item_dict.set_item("impact_type", item.impact_type.as_str())?;
            item_dict.set_item("distance", item.distance)?;
            items_list.append(item_dict)?;
        }
        dict.set_item("affected_items", items_list)?;

        Ok(dict.into())
    }

    /// Get all files that depend on a given file.
    ///
    /// Returns files that directly or indirectly import the specified file.
    ///
    /// Args:
    ///     file_path: Relative path to the file.
    ///
    /// Returns:
    ///     list[str]: List of dependent file paths.
    #[pyo3(signature = (file_path))]
    fn get_dependents(&self, py: Python<'_>, file_path: String) -> PyResult<Py<PyAny>> {
        let dependents = self
            .inner
            .get_dependents(&file_path)
            .map_err(PyAtlasError::from)?;
        let list = pyo3::types::PyList::new(py, &dependents)?;
        Ok(list.into())
    }

    /// Get all files that a given file depends on.
    ///
    /// Returns files that are directly or indirectly imported by the specified file.
    ///
    /// Args:
    ///     file_path: Relative path to the file.
    ///
    /// Returns:
    ///     list[str]: List of dependency file paths.
    #[pyo3(signature = (file_path))]
    fn get_dependencies(&self, py: Python<'_>, file_path: String) -> PyResult<Py<PyAny>> {
        let dependencies = self
            .inner
            .get_dependencies(&file_path)
            .map_err(PyAtlasError::from)?;
        let list = pyo3::types::PyList::new(py, &dependencies)?;
        Ok(list.into())
    }

    /// Find duplicate or similar code.
    ///
    /// Detects functions with similar signatures or naming patterns.
    ///
    /// Returns:
    ///     list[dict]: Duplicate matches, each containing:
    ///         - artifact_a: First artifact's qualified name
    ///         - artifact_b: Second artifact's qualified name
    ///         - file_a, file_b: File paths
    ///         - similarity: Similarity score (0.0-1.0)
    ///         - match_type: Type of match (similar_signature, similar_naming)
    ///         - suggestion: Refactoring suggestion
    fn find_duplicates(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let matches = self.inner.find_duplicates().map_err(PyAtlasError::from)?;

        let list = pyo3::types::PyList::empty(py);
        for m in &matches {
            let dict = PyDict::new(py);
            dict.set_item("artifact_a", &m.artifact_a)?;
            dict.set_item("artifact_b", &m.artifact_b)?;
            dict.set_item("file_a", &m.file_a)?;
            dict.set_item("file_b", &m.file_b)?;
            dict.set_item("lines_a", (m.lines_a.0, m.lines_a.1))?;
            dict.set_item("lines_b", (m.lines_b.0, m.lines_b.1))?;
            dict.set_item("similarity", m.similarity.value())?;
            dict.set_item("match_type", m.match_type.as_str())?;
            dict.set_item("suggestion", &m.suggestion)?;
            list.append(dict)?;
        }
        Ok(list.into())
    }

    /// Detect circular dependencies in the import graph.
    ///
    /// Returns:
    ///     list[list[str]]: List of cycles, where each cycle is a list
    ///                     of file paths forming the circular dependency.
    fn detect_cycles(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let cycles = self.inner.detect_cycles().map_err(PyAtlasError::from)?;

        let list = pyo3::types::PyList::empty(py);
        for cycle in &cycles {
            let cycle_list = pyo3::types::PyList::new(py, cycle)?;
            list.append(cycle_list)?;
        }
        Ok(list.into())
    }

    #[pyo3(signature = (pattern, limit=None))]
    fn glob_python_files(
        &self,
        py: Python<'_>,
        pattern: String,
        limit: Option<usize>,
    ) -> PyResult<Py<PyAny>> {
        let limit = limit.unwrap_or(10);
        let files = self
            .inner
            .glob_python_files(&pattern, limit)
            .map_err(PyAtlasError::from)?;

        let results: Vec<String> = files
            .iter()
            .map(|p| p.to_string_lossy().to_string())
            .collect();
        let list = PyList::new(py, &results)?;
        Ok(list.into())
    }

    #[pyo3(signature = (query, limit=None, path_glob=None))]
    fn grep_spans(
        &self,
        py: Python<'_>,
        query: String,
        limit: Option<usize>,
        path_glob: Option<String>,
    ) -> PyResult<Py<PyAny>> {
        let limit = limit.unwrap_or(10);
        let spans = self
            .inner
            .grep_spans(&query, limit, path_glob.as_deref())
            .map_err(PyAtlasError::from)?;

        let json = serde_json::to_value(&spans)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }

    #[pyo3(signature = (file_path, line_start, line_end, max_bytes=None))]
    fn read_span(
        &self,
        _py: Python<'_>,
        file_path: String,
        line_start: usize,
        line_end: usize,
        max_bytes: Option<usize>,
    ) -> PyResult<String> {
        let max_bytes = max_bytes.unwrap_or(8_192);
        let snippet = self
            .inner
            .read_span(&file_path, line_start, line_end, max_bytes)
            .map_err(PyAtlasError::from)?;
        Ok(snippet)
    }

    #[pyo3(signature = (query, limit=None))]
    fn search_spans(
        &mut self,
        py: Python<'_>,
        query: String,
        limit: Option<usize>,
    ) -> PyResult<Py<PyAny>> {
        let limit = limit.unwrap_or(10);
        let spans = self
            .inner
            .search_spans(&query, limit)
            .map_err(PyAtlasError::from)?;

        let json = serde_json::to_value(&spans)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }

    fn fastapi_scaling_policy(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let policy = analysis::FastapiScalingPolicy::load(&self.project_root)
            .map_err(PyAtlasError::from)?;
        let json = serde_json::to_value(&policy)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }

    fn analyze_fastapi_scaling(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let report = self
            .inner
            .analyze_fastapi_scaling()
            .map_err(PyAtlasError::from)?;
        let json = serde_json::to_value(&report)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }

    fn analyze_fastapi_router_topology(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let report = self
            .inner
            .analyze_fastapi_router_topology()
            .map_err(PyAtlasError::from)?;
        let json = serde_json::to_value(&report)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }

    #[pyo3(signature = (**kwargs))]
    fn fastapi_truth_capsule(
        &mut self,
        py: Python<'_>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let get_opt_string = |key: &str| -> PyResult<Option<String>> {
            let Some(kwargs) = kwargs else {
                return Ok(None);
            };
            let Some(v) = kwargs.get_item(key)? else {
                return Ok(None);
            };
            if v.is_none() {
                return Ok(None);
            }
            Ok(Some(v.extract::<String>()?))
        };

        let get_opt_bool = |key: &str| -> PyResult<Option<bool>> {
            let Some(kwargs) = kwargs else {
                return Ok(None);
            };
            let Some(v) = kwargs.get_item(key)? else {
                return Ok(None);
            };
            if v.is_none() {
                return Ok(None);
            }
            Ok(Some(v.extract::<bool>()?))
        };

        let get_opt_usize = |key: &str| -> PyResult<Option<usize>> {
            let Some(kwargs) = kwargs else {
                return Ok(None);
            };
            let Some(v) = kwargs.get_item(key)? else {
                return Ok(None);
            };
            if v.is_none() {
                return Ok(None);
            }
            Ok(Some(v.extract::<usize>()?))
        };

        let method = get_opt_string("method")?;
        let path = get_opt_string("path")?;
        let operation_id = get_opt_string("operation_id")?;
        let handler_qualified_name = get_opt_string("handler_qualified_name")?;
        let mode = get_opt_string("mode")?;
        let strict = get_opt_bool("strict")?;
        let max_spans = get_opt_usize("max_spans")?;
        let max_dependency_depth = get_opt_usize("max_dependency_depth")?;
        let max_call_depth = get_opt_usize("max_call_depth")?;
        let max_call_nodes = get_opt_usize("max_call_nodes")?;
        let include_snippets = get_opt_bool("include_snippets")?;
        let snippet_max_lines = get_opt_usize("snippet_max_lines")?;

        let request = analysis::FastapiTruthCapsuleRequest {
            method,
            path,
            operation_id,
            handler_qualified_name,
            mode: mode.unwrap_or_else(|| "static".to_string()),
            strict: strict.unwrap_or(false),
            max_spans: max_spans.unwrap_or(1024),
            max_dependency_depth: max_dependency_depth.unwrap_or(8),
            max_call_depth: max_call_depth.unwrap_or(6),
            max_call_nodes: max_call_nodes.unwrap_or(256),
            include_snippets: include_snippets.unwrap_or(false),
            snippet_max_lines: snippet_max_lines.unwrap_or(0),
        };

        let capsule = self
            .inner
            .fastapi_truth_capsule(request)
            .map_err(PyAtlasError::from)?;

        let json = serde_json::to_value(&capsule)
            .map_err(|e| PyAtlasError::Generic(format!("JSON serialization error: {e}")))?;
        types::json_to_py(py, &json)
    }
}

/// Artifact kind enumeration exposed to Python.
///
/// Represents the classification of a code artifact.
#[pyclass(name = "ArtifactKind")]
#[derive(Clone)]
pub struct PyArtifactKind {
    inner: ArtifactKind,
}

#[pymethods]
impl PyArtifactKind {
    /// Function definition.
    #[classattr]
    const FUNCTION: &'static str = "function";

    /// Async function definition.
    #[classattr]
    const ASYNC_FUNCTION: &'static str = "async_function";

    /// Class definition.
    #[classattr]
    const CLASS: &'static str = "class";

    /// Method inside a class.
    #[classattr]
    const METHOD: &'static str = "method";

    /// HTTP endpoint (FastAPI route).
    #[classattr]
    const ENDPOINT: &'static str = "endpoint";

    /// Contract-decorated function.
    #[classattr]
    const CONTRACT: &'static str = "contract";

    /// Pydantic model.
    #[classattr]
    const MODEL: &'static str = "model";

    /// Module-level constant.
    #[classattr]
    const CONSTANT: &'static str = "constant";

    fn __repr__(&self) -> String {
        format!("ArtifactKind.{}", self.inner.as_str().to_uppercase())
    }
}

/// Get the version of the ranex_rust module.
#[pyfunction]
fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Initialize logging for the Ranex library.
///
/// Args:
///     level: Log level ("trace", "debug", "info", "warn", "error").
///            Default is "info".
#[pyfunction]
#[pyo3(signature = (level=None))]
fn init_logging(level: Option<&str>) -> PyResult<()> {
    let level = level.unwrap_or("info");
    let config = ranex_core::LogConfig {
        level: level.to_string(),
        format: ranex_core::LogFormat::Pretty,
        include_location: false,
        include_target: true,
    };
    ranex_core::init_logging(config);
    Ok(())
}

// ============================================================================
// Integrity Verification (Tamper Detection)
// ============================================================================

/// Embedded hashes of critical Python files.
/// These are computed at build time and embedded into the binary.
///
/// NOTE: In production, these would be generated by a build script.
/// For now, we use placeholders that get updated on first run in "learn" mode.
static INTEGRITY_HASHES: LazyLock<HashMap<&'static str, &'static str>> = LazyLock::new(|| {
    let mut m = HashMap::new();
    // These hashes should be updated by the build process
    // Format: relative path from package root -> blake3 hash
    m.insert("ranex/__init__.py", "PLACEHOLDER_INIT");
    m.insert("ranex/cli.py", "PLACEHOLDER_CLI");
    m
});

/// Compute the blake3 hash of a file.
///
/// Args:
///     file_path: Path to the file to hash.
///
/// Returns:
///     Hex-encoded blake3 hash of the file contents.
///
/// Raises:
///     IOError: If the file cannot be read.
#[pyfunction]
fn compute_file_hash(file_path: &str) -> PyResult<String> {
    let contents = std::fs::read(file_path).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to read {}: {}", file_path, e))
    })?;

    let hash = blake3::hash(&contents);
    Ok(hash.to_hex().to_string())
}

/// Verify the integrity of a Python file against embedded hash.
///
/// Args:
///     file_path: Absolute path to the file to verify.
///     relative_path: Relative path used as key in the hash registry.
///
/// Returns:
///     True if the file hash matches the embedded hash, False otherwise.
///     Also returns False if the file cannot be read or hash is not found.
fn verify_file_integrity_with_mode(strict_mode: bool, file_path: &str, relative_path: &str) -> bool {
    // Get expected hash
    let expected = match INTEGRITY_HASHES.get(relative_path) {
        Some(hash) if !hash.starts_with("PLACEHOLDER") => *hash,
        _ => {
            debug!(
                path = relative_path,
                "No embedded hash found (or placeholder)"
            );
            return !strict_mode;
        }
    };

    // Compute actual hash
    let actual = match std::fs::read(file_path) {
        Ok(contents) => blake3::hash(&contents).to_hex().to_string(),
        Err(e) => {
            debug!(path = file_path, error = %e, "Failed to read file for integrity check");
            return false;
        }
    };

    let matches = actual == expected;
    if !matches {
        info!(
            path = relative_path,
            expected = expected,
            actual = actual,
            "Integrity check failed"
        );
    }
    matches
}

#[pyfunction]
fn verify_file_integrity(file_path: &str, relative_path: &str) -> bool {
    verify_file_integrity_with_mode(is_strict_integrity_mode(), file_path, relative_path)
}

/// Verify all critical CLI files at once.
///
/// Returns:
///     Dict mapping relative paths to (verified: bool, reason: str).
fn verify_cli_integrity_with_mode(
    py: Python<'_>,
    strict_mode: bool,
    package_dir: &str,
) -> PyResult<Py<PyDict>> {
    let dict = PyDict::new(py);

    for (rel_path, expected_hash) in INTEGRITY_HASHES.iter() {
        let full_path = format!("{}/{}", package_dir, rel_path);

        let (verified, reason) = if expected_hash.starts_with("PLACEHOLDER") {
            if strict_mode {
                (false, "placeholder_hash".to_string())
            } else {
                (true, "development_mode".to_string())
            }
        } else {
            match std::fs::read(&full_path) {
                Ok(contents) => {
                    let actual = blake3::hash(&contents).to_hex().to_string();
                    if actual == *expected_hash {
                        (true, "hash_match".to_string())
                    } else {
                        (
                            false,
                            format!(
                                "hash_mismatch: expected={}, actual={}",
                                expected_hash, actual
                            ),
                        )
                    }
                }
                Err(e) => (false, format!("read_error: {}", e)),
            }
        };

        let result = PyDict::new(py);
        result.set_item("verified", verified)?;
        result.set_item("reason", reason)?;
        dict.set_item(*rel_path, result)?;
    }

    Ok(dict.into())
}

#[pyfunction]
fn verify_cli_integrity(py: Python<'_>, package_dir: &str) -> PyResult<Py<PyDict>> {
    verify_cli_integrity_with_mode(py, is_strict_integrity_mode(), package_dir)
}

#[cfg(test)]
mod integrity_tests {
    use super::{verify_cli_integrity_with_mode, verify_file_integrity_with_mode};
    use pyo3::exceptions::PyKeyError;
    use pyo3::prelude::*;
    use pyo3::types::PyDict;
    use tempfile::tempdir;

    #[test]
    fn test_verify_file_integrity_placeholder_non_strict_allows(
    ) -> Result<(), Box<dyn std::error::Error>> {
        let dir = tempdir()?;
        let file_path = dir.path().join("cli.py");
        std::fs::write(&file_path, "print('hello')\n")?;

        let ok = verify_file_integrity_with_mode(false, &file_path.to_string_lossy(), "ranex/cli.py");
        assert!(ok);
        Ok(())
    }

    #[test]
    fn test_verify_file_integrity_placeholder_strict_fails(
    ) -> Result<(), Box<dyn std::error::Error>> {
        let dir = tempdir()?;
        let file_path = dir.path().join("cli.py");
        std::fs::write(&file_path, "print('hello')\n")?;

        let ok = verify_file_integrity_with_mode(true, &file_path.to_string_lossy(), "ranex/cli.py");
        assert!(!ok);
        Ok(())
    }

    #[test]
    fn test_verify_file_integrity_missing_hash_strict_fails(
    ) -> Result<(), Box<dyn std::error::Error>> {
        let dir = tempdir()?;
        let file_path = dir.path().join("something.py");
        std::fs::write(&file_path, "print('x')\n")?;

        let ok = verify_file_integrity_with_mode(true, &file_path.to_string_lossy(), "unknown/path.py");
        assert!(!ok);
        Ok(())
    }

    #[test]
    fn test_verify_cli_integrity_placeholder_strict_fails() -> PyResult<()> {
        let dir = tempdir().map_err(PyErr::from)?;

        Python::initialize();

        Python::attach(|py| -> PyResult<()> {
            let result = verify_cli_integrity_with_mode(py, true, &dir.path().to_string_lossy())?;
            let result = result.bind(py);
            let result_dict: &Bound<'_, PyDict> = result.cast()?;

            let cli_entry_any = result_dict
                .get_item("ranex/cli.py")?
                .ok_or_else(|| PyKeyError::new_err("missing ranex/cli.py entry"))?;
            let cli_dict: &Bound<'_, PyDict> = cli_entry_any.cast()?;

            let verified_any = cli_dict
                .get_item("verified")?
                .ok_or_else(|| PyKeyError::new_err("missing verified"))?;
            let verified: bool = verified_any.extract()?;

            let reason_any = cli_dict
                .get_item("reason")?
                .ok_or_else(|| PyKeyError::new_err("missing reason"))?;
            let reason: String = reason_any.extract()?;

            assert!(!verified);
            assert_eq!(reason, "placeholder_hash");
            Ok(())
        })?;
        Ok(())
    }
}

/// Check if we're running in integrity enforcement mode.
///
/// Returns True if RANEX_INTEGRITY_MODE environment variable is set to "strict".
#[pyfunction]
fn is_strict_integrity_mode() -> bool {
    std::env::var("RANEX_INTEGRITY_MODE")
        .map(|v| v.to_lowercase() == "strict")
        .unwrap_or(false)
}

/// Python module definition.
///
/// Exposes:
/// - Atlas: Main class for codebase indexing
/// - ArtifactKind: Enumeration of artifact types
/// - version(): Get module version
/// - init_logging(): Initialize logging
#[pymodule]
pub fn ranex_rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Add version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // Add classes
    m.add_class::<PyAtlas>()?;
    m.add_class::<PyArtifactKind>()?;

    // Add functions
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(init_logging, m)?)?;

    // Integrity verification functions
    m.add_function(wrap_pyfunction!(compute_file_hash, m)?)?;
    m.add_function(wrap_pyfunction!(verify_file_integrity, m)?)?;
    m.add_function(wrap_pyfunction!(verify_cli_integrity, m)?)?;
    m.add_function(wrap_pyfunction!(is_strict_integrity_mode, m)?)?;

    // Firewall class
    m.add_class::<firewall::PyFirewall>()?;

    Ok(())
}
