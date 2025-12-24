//! Error handling for Python bindings.
//!
//! This module provides error types that convert Rust errors into
//! appropriate Python exceptions.

use pyo3::exceptions::{PyFileNotFoundError, PyIOError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use ranex_core::AtlasError;
use thiserror::Error;

/// Python-compatible error type for Atlas operations.
///
/// This error type wraps Rust errors and converts them to appropriate
/// Python exceptions when crossing the FFI boundary.
#[derive(Debug, Error)]
pub enum PyAtlasError {
    /// Project directory not found
    #[error("Project not found: {path}")]
    ProjectNotFound { path: String },

    /// Database initialization or query failed
    #[error("Database error: {message}")]
    Database { message: String },

    /// File parsing failed
    #[error("Parse error in {path}: {message}")]
    Parse { path: String, message: String },

    /// File I/O error
    #[error("I/O error: {message}")]
    Io { message: String },

    /// Invalid argument provided
    #[error("Invalid argument: {message}")]
    InvalidArgument { message: String },

    /// Generic error
    #[error("{0}")]
    Generic(String),
}

impl PyAtlasError {
    /// Create a "project not found" error.
    pub fn project_not_found(path: &str) -> Self {
        PyAtlasError::ProjectNotFound {
            path: path.to_string(),
        }
    }

    /// Create a database error.
    pub fn database(message: impl Into<String>) -> Self {
        PyAtlasError::Database {
            message: message.into(),
        }
    }

    /// Create a parse error.
    pub fn parse(path: impl Into<String>, message: impl Into<String>) -> Self {
        PyAtlasError::Parse {
            path: path.into(),
            message: message.into(),
        }
    }

    /// Create an I/O error.
    pub fn io(message: impl Into<String>) -> Self {
        PyAtlasError::Io {
            message: message.into(),
        }
    }

    /// Create an invalid argument error.
    pub fn invalid_argument(message: impl Into<String>) -> Self {
        PyAtlasError::InvalidArgument {
            message: message.into(),
        }
    }
}

impl From<AtlasError> for PyAtlasError {
    fn from(err: AtlasError) -> Self {
        match err {
            AtlasError::Walk { path, message } => PyAtlasError::Io {
                message: format!("Failed to walk {}: {}", path.display(), message),
            },
            AtlasError::Parse { path, message } => PyAtlasError::Parse {
                path: path.to_string_lossy().to_string(),
                message,
            },
            AtlasError::Syntax {
                path,
                line,
                message,
            } => PyAtlasError::Parse {
                path: path.to_string_lossy().to_string(),
                message: format!("Line {}: {}", line, message),
            },
            AtlasError::Database { operation, message } => PyAtlasError::Database {
                message: format!("{}: {}", operation, message),
            },
            AtlasError::Migration {
                from_version,
                to_version,
                message,
            } => PyAtlasError::Database {
                message: format!(
                    "Migration failed (v{} -> v{}): {}",
                    from_version, to_version, message
                ),
            },
            AtlasError::NotFound(path) => PyAtlasError::ProjectNotFound {
                path: path.to_string_lossy().to_string(),
            },
            AtlasError::FileTooLarge {
                path,
                size,
                max_size,
            } => PyAtlasError::Io {
                message: format!(
                    "File {} too large ({} bytes, max {})",
                    path.display(),
                    size,
                    max_size
                ),
            },
            AtlasError::Encoding { path, message } => PyAtlasError::Parse {
                path: path.to_string_lossy().to_string(),
                message: format!("Encoding error: {}", message),
            },
            AtlasError::ProjectRootNotFound { start_path } => PyAtlasError::ProjectNotFound {
                path: start_path.to_string_lossy().to_string(),
            },
            AtlasError::Io(err) => PyAtlasError::Io {
                message: err.to_string(),
            },
            AtlasError::Unavailable {
                reason,
                recoverable,
            } => PyAtlasError::Database {
                message: format!(
                    "Atlas unavailable: {} (recoverable: {})",
                    reason, recoverable
                ),
            },
            AtlasError::IndexStale { reason } => PyAtlasError::Database {
                message: format!("Index stale: {}", reason),
            },
            AtlasError::SchemaIncompatible { found, expected } => PyAtlasError::Database {
                message: format!(
                    "Schema version {} incompatible (expected {})",
                    found, expected
                ),
            },
            AtlasError::AnalysisConfig { path, message } => PyAtlasError::InvalidArgument {
                message: format!(
                    "Analysis config error in '{}': {}",
                    path.display(), message
                ),
            },
        }
    }
}

impl From<PyAtlasError> for PyErr {
    fn from(err: PyAtlasError) -> PyErr {
        match &err {
            PyAtlasError::ProjectNotFound { .. } => PyFileNotFoundError::new_err(err.to_string()),
            PyAtlasError::Database { .. } => PyRuntimeError::new_err(err.to_string()),
            PyAtlasError::Parse { .. } => PyRuntimeError::new_err(err.to_string()),
            PyAtlasError::Io { .. } => PyIOError::new_err(err.to_string()),
            PyAtlasError::InvalidArgument { .. } => PyValueError::new_err(err.to_string()),
            PyAtlasError::Generic(_) => PyRuntimeError::new_err(err.to_string()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_project_not_found_error() {
        let err = PyAtlasError::project_not_found("/missing/path");
        assert!(err.to_string().contains("/missing/path"));
    }

    #[test]
    fn test_database_error() {
        let err = PyAtlasError::database("connection failed");
        assert!(err.to_string().contains("connection failed"));
    }

    #[test]
    fn test_parse_error() {
        let err = PyAtlasError::parse("test.py", "syntax error");
        assert!(err.to_string().contains("test.py"));
        assert!(err.to_string().contains("syntax error"));
    }

    #[test]
    fn test_io_error() {
        let err = PyAtlasError::io("permission denied");
        assert!(err.to_string().contains("permission denied"));
    }

    #[test]
    fn test_atlas_error_conversion() {
        let atlas_err = AtlasError::Database {
            operation: "insert".to_string(),
            message: "table not found".to_string(),
        };
        let py_err: PyAtlasError = atlas_err.into();

        assert!(
            matches!(&py_err, PyAtlasError::Database { .. }),
            "Expected Database error"
        );

        if let PyAtlasError::Database { message } = py_err {
            assert!(message.contains("insert"));
            assert!(message.contains("table not found"));
        }
    }
}
