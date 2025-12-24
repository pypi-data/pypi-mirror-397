//! Type conversion utilities for Python bindings.
//!
//! This module provides functions to convert Rust types to Python types
//! for crossing the FFI boundary.

use pyo3::prelude::*;
use pyo3::conversion::IntoPyObjectExt;
use pyo3::types::{PyDict, PyList};
use ranex_core::{Artifact, ScanResult, ScanStats};
use serde_json::Value as JsonValue;

/// Convert an Artifact to a Python dictionary.
pub fn artifact_to_dict<'py>(py: Python<'py>, artifact: &Artifact) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);

    // Required fields
    dict.set_item("symbol_name", &artifact.symbol_name)?;
    dict.set_item("qualified_name", &artifact.qualified_name)?;
    dict.set_item("kind", artifact.kind.as_str())?;
    dict.set_item(
        "file_path",
        artifact.file_path.to_string_lossy().to_string(),
    )?;
    dict.set_item("module_path", &artifact.module_path)?;
    dict.set_item("line_start", artifact.line_start)?;
    dict.set_item("line_end", artifact.line_end)?;

    // Optional fields
    dict.set_item("signature", artifact.signature.as_deref())?;
    dict.set_item("docstring", artifact.docstring.as_deref())?;
    dict.set_item("feature", artifact.feature.as_deref())?;
    dict.set_item("hash", artifact.hash.as_deref())?;

    dict.set_item("http_method", artifact.http_method.as_deref())?;
    dict.set_item("route_path", artifact.route_path.as_deref())?;
    dict.set_item("router_prefix", artifact.router_prefix.as_deref())?;

    let direct_deps = PyList::new(py, &artifact.direct_dependencies)?;
    dict.set_item("direct_dependencies", direct_deps)?;

    let dependency_chain = PyList::new(py, &artifact.dependency_chain)?;
    dict.set_item("dependency_chain", dependency_chain)?;

    let security_deps = PyList::new(py, &artifact.security_dependencies)?;
    dict.set_item("security_dependencies", security_deps)?;

    // Tags as list
    let tags = PyList::new(py, &artifact.tags)?;
    dict.set_item("tags", tags)?;

    Ok(dict)
}

pub fn json_to_py(py: Python<'_>, value: &JsonValue) -> PyResult<Py<PyAny>> {
    match value {
        JsonValue::Null => Ok(py.None()),
        JsonValue::Bool(v) => Ok(v.into_py_any(py)?),
        JsonValue::Number(v) => {
            if let Some(i) = v.as_i64() {
                Ok(i.into_py_any(py)?)
            } else if let Some(u) = v.as_u64() {
                Ok(u.into_py_any(py)?)
            } else if let Some(f) = v.as_f64() {
                Ok(f.into_py_any(py)?)
            } else {
                Ok(py.None())
            }
        }
        JsonValue::String(v) => Ok(v.clone().into_py_any(py)?),
        JsonValue::Array(values) => {
            let list = PyList::empty(py);
            for item in values {
                list.append(json_to_py(py, item)?)?;
            }
            Ok(list.into_py_any(py)?)
        }
        JsonValue::Object(map) => {
            let dict = PyDict::new(py);
            for (k, v) in map {
                dict.set_item(k, json_to_py(py, v)?)?;
            }
            Ok(dict.into_py_any(py)?)
        }
    }
}

/// Convert a list of Artifacts to a Python list of dictionaries.
pub fn artifacts_to_list<'py>(
    py: Python<'py>,
    artifacts: &[Artifact],
) -> PyResult<Bound<'py, PyList>> {
    let mut dicts = Vec::with_capacity(artifacts.len());

    for artifact in artifacts {
        let dict = artifact_to_dict(py, artifact)?;
        dicts.push(dict);
    }

    PyList::new(py, dicts)
}

/// Convert ScanStats to a Python dictionary.
pub fn scan_stats_to_dict<'py>(py: Python<'py>, stats: &ScanStats) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);

    dict.set_item("files_scanned", stats.files_scanned)?;
    dict.set_item("files_parsed", stats.files_parsed)?;
    dict.set_item("files_failed", stats.files_failed)?;
    dict.set_item("files_skipped", stats.files_skipped)?;
    dict.set_item("files_cached", stats.files_cached)?;
    dict.set_item("artifacts_found", stats.artifacts_found)?;

    // Convert artifacts_by_kind HashMap to Python dict
    let by_kind = PyDict::new(py);
    for (kind, count) in &stats.artifacts_by_kind {
        by_kind.set_item(kind.as_str(), count)?;
    }
    dict.set_item("artifacts_by_kind", by_kind)?;

    Ok(dict)
}

/// Convert ScanResult to a Python dictionary.
pub fn scan_result_to_dict<'py>(
    py: Python<'py>,
    result: &ScanResult,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);

    // Embed stats
    let stats_dict = scan_stats_to_dict(py, &result.stats)?;
    dict.set_item("stats", stats_dict)?;

    // Top-level convenience fields
    dict.set_item("artifacts_found", result.stats.artifacts_found)?;
    dict.set_item("files_scanned", result.stats.files_scanned)?;
    dict.set_item("files_parsed", result.stats.files_parsed)?;
    dict.set_item("files_failed", result.stats.files_failed)?;
    dict.set_item("duration_ms", result.duration_ms)?;

    // Failed files as list of dicts
    let mut failed_items = Vec::with_capacity(result.failed_files.len());
    for f in &result.failed_files {
        let d = PyDict::new(py);
        d.set_item("path", f.path.to_string_lossy().to_string())?;
        d.set_item("error", f.error.as_deref())?;
        failed_items.push(d);
    }
    let failed = PyList::new(py, failed_items)?;
    dict.set_item("failed_files", failed)?;

    Ok(dict)
}

#[cfg(test)]
mod tests {
    use ranex_core::ArtifactKind;

    #[test]
    fn test_artifact_kind_conversion() {
        assert_eq!(ArtifactKind::Function.as_str(), "function");
        assert_eq!(ArtifactKind::Class.as_str(), "class");
        assert_eq!(ArtifactKind::Endpoint.as_str(), "endpoint");
    }

    #[test]
    fn test_artifact_kind_from_str() {
        assert_eq!(
            ArtifactKind::parse("function"),
            Some(ArtifactKind::Function)
        );
        assert_eq!(ArtifactKind::parse("class"), Some(ArtifactKind::Class));
        assert_eq!(ArtifactKind::parse("invalid"), None);
    }
}
