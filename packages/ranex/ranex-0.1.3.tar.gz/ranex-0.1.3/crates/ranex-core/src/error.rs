//! Unified error types for all Ranex crates.
//!
//! This module defines all error types used across Ranex. Each crate should
//! use these error types rather than defining their own.
//!
//! ## Error Hierarchy
//!
//! - `RanexError` - Top-level error enum for all operations
//! - `AtlasError` - Atlas-specific errors (scanning, parsing, storage)
//! - `ConfigError` - Configuration loading/parsing errors
//!
//! ## Design Principles
//!
//! 1. **Structured Errors**: Include context for debugging (file paths, line numbers)
//! 2. **No Panics**: Libraries return `Result`, panics are reserved for bugs
//! 3. **AI-Friendly**: Error messages help AI diagnose issues
//! 4. **SpanTrace**: Errors capture call-stack context for debugging
//!
//! ## SpanTrace Support
//!
//! Key error variants include `SpanTrace` fields that automatically capture
//! the tracing span context when errors are created. This helps AI agents
//! understand the call path that led to the error.
//!
//! To see SpanTrace in error output, ensure logging is initialized via
//! `ranex_core::logging::init_logging()` before errors occur.

use std::path::PathBuf;
use thiserror::Error;
use tracing_error::SpanTrace;

/// Result type alias using `RanexError`
pub type RanexResult<T> = Result<T, RanexError>;

/// Top-level error type for all Ranex operations.
///
/// Use this for cross-crate error handling. Specific crates may convert
/// their internal errors into `RanexError` variants.
#[derive(Debug, Error)]
pub enum RanexError {
    /// Atlas indexing/scanning error
    #[error("Atlas error: {0}")]
    Atlas(#[from] AtlasError),

    /// Configuration error
    #[error("Configuration error: {0}")]
    Config(#[from] ConfigError),

    /// File I/O error with path context and span trace
    #[error("Failed to read file '{path}': {source}")]
    FileRead {
        path: PathBuf,
        #[source]
        source: std::io::Error,
        /// Call-stack context at error creation
        span_trace: SpanTrace,
    },

    /// File write error with path context and span trace
    #[error("Failed to write file '{path}': {source}")]
    FileWrite {
        path: PathBuf,
        #[source]
        source: std::io::Error,
        /// Call-stack context at error creation
        span_trace: SpanTrace,
    },

    /// Validation rule violation
    #[error("Validation failed [{rule}]: {message}")]
    Validation { rule: String, message: String },

    /// Security violation detected
    #[error("Security violation [{severity}] in {file_path}:{line}: {message}")]
    SecurityViolation {
        severity: String,
        file_path: PathBuf,
        line: usize,
        message: String,
    },

    /// Import validation failed
    #[error("Import '{package}' not allowed: {reason}")]
    ImportValidation {
        package: String,
        reason: String,
        alternatives: Vec<String>,
    },

    /// Generic error (use sparingly)
    #[error("{message}")]
    Generic {
        message: String,
        #[source]
        source: Option<Box<dyn std::error::Error + Send + Sync>>,
        /// Call-stack context at error creation
        span_trace: SpanTrace,
    },
}

impl RanexError {
    /// Get the span trace if this error variant has one.
    ///
    /// Returns the SpanTrace for errors that capture call-stack context.
    /// This is useful for AI agents debugging error chains.
    pub fn span_trace(&self) -> Option<&SpanTrace> {
        match self {
            Self::FileRead { span_trace, .. } => Some(span_trace),
            Self::FileWrite { span_trace, .. } => Some(span_trace),
            Self::Generic { span_trace, .. } => Some(span_trace),
            _ => None,
        }
    }
}

/// Atlas-specific errors for scanning, parsing, and storage operations.
#[derive(Debug, Error)]
pub enum AtlasError {
    /// File system traversal error
    #[error("Failed to walk directory '{path}': {message}")]
    Walk { path: PathBuf, message: String },

    /// Python file parsing error
    #[error("Failed to parse Python file '{path}': {message}")]
    Parse { path: PathBuf, message: String },

    /// Python AST error (syntax error in source)
    #[error("Syntax error in '{path}' at line {line}: {message}")]
    Syntax {
        path: PathBuf,
        line: usize,
        message: String,
    },

    /// SQLite database error
    #[error("Database error in {operation}: {message}")]
    Database { operation: String, message: String },

    /// Schema migration error
    #[error("Schema migration failed from v{from_version} to v{to_version}: {message}")]
    Migration {
        from_version: u32,
        to_version: u32,
        message: String,
    },

    /// File not found
    #[error("File not found: {0}")]
    NotFound(PathBuf),

    /// File too large to process
    #[error("File '{path}' exceeds maximum size ({size} > {max_size} bytes)")]
    FileTooLarge {
        path: PathBuf,
        size: usize,
        max_size: usize,
    },

    /// Encoding error
    #[error("File '{path}' has invalid encoding: {message}")]
    Encoding { path: PathBuf, message: String },

    /// Project root not found (no .git, pyproject.toml, etc.)
    #[error("Could not detect project root from '{start_path}'")]
    ProjectRootNotFound { start_path: PathBuf },

    /// I/O error wrapper
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    /// Atlas index unavailable - fail-closed error for zero-config behavior.
    ///
    /// This error is returned when `ensure_index()` cannot guarantee a valid,
    /// fresh index. AI tools MUST NOT treat this as "empty results" - it means
    /// the index is genuinely unavailable and the operation should fail.
    #[error("Atlas unavailable: {reason}. The index cannot be guaranteed valid.")]
    Unavailable {
        reason: String,
        /// Whether a retry might succeed (e.g., transient I/O error)
        recoverable: bool,
    },

    /// Index is stale and needs refresh
    #[error("Atlas index is stale: {reason}")]
    IndexStale { reason: String },

    /// Schema version incompatible
    #[error("Schema version {found} is incompatible (expected {expected})")]
    SchemaIncompatible { found: u32, expected: u32 },

    #[error("Analysis config error in '{path}': {message}")]
    AnalysisConfig { path: PathBuf, message: String },
}

/// Configuration-related errors.
#[derive(Debug, Error)]
pub enum ConfigError {
    /// Config file not found
    #[error("Configuration file not found: {0}")]
    NotFound(PathBuf),

    /// TOML parsing error
    #[error("Failed to parse TOML config: {0}")]
    TomlParse(#[from] toml::de::Error),

    /// TOML serialization error
    #[error("Failed to serialize config: {0}")]
    TomlSerialize(#[from] toml::ser::Error),

    /// Invalid configuration value
    #[error("Invalid config value for '{key}': {message}")]
    InvalidValue { key: String, message: String },

    /// Missing required configuration
    #[error("Missing required configuration: {0}")]
    Missing(String),

    /// I/O error reading/writing config
    #[error("Config I/O error: {0}")]
    Io(#[from] std::io::Error),
}

/// Result type alias for Firewall operations.
pub type FirewallResult<T> = Result<T, FirewallError>;

/// Firewall-specific errors for dependency validation.
#[derive(Debug, Clone, Error)]
pub enum FirewallError {
    /// Package blocked by policy pattern
    #[error("Package '{package}' blocked by pattern '{pattern}': {reason}")]
    BlockedPattern {
        package: String,
        pattern: String,
        reason: String,
    },

    /// Possible typosquatting detected
    #[error("Possible typosquatting: '{package}' looks like '{intended}' (distance: {distance})")]
    Typosquat {
        package: String,
        intended: String,
        distance: usize,
    },

    /// Internal import not found in Atlas
    #[error("Internal import '{module}' not found in codebase")]
    InternalNotFound {
        module: String,
        suggestions: Vec<String>,
    },

    /// Policy file error
    #[error("Policy error in '{config_path}': {reason}")]
    PolicyError { config_path: String, reason: String },

    /// Analysis error
    #[error("Analysis error in '{file}': {reason}")]
    AnalysisError { file: String, reason: String },

    /// Rules file not found
    #[error("Rules file not found: {path}")]
    RulesNotFound { path: String },

    /// Invalid rule configuration
    #[error("Invalid rule '{name}': {reason}")]
    InvalidRule { name: String, reason: String },

    /// YAML parsing error
    #[error("YAML parse error: {0}")]
    YamlParse(String),

    /// I/O error
    #[error("Firewall I/O error: {0}")]
    Io(String),
}

impl From<std::io::Error> for FirewallError {
    fn from(e: std::io::Error) -> Self {
        FirewallError::Io(e.to_string())
    }
}

impl From<AtlasError> for FirewallError {
    fn from(e: AtlasError) -> Self {
        FirewallError::PolicyError {
            config_path: "atlas".to_string(),
            reason: e.to_string(),
        }
    }
}

impl FirewallError {
    /// Create a blocked pattern error
    pub fn blocked_pattern(
        package: impl Into<String>,
        pattern: impl Into<String>,
        reason: impl Into<String>,
    ) -> Self {
        FirewallError::BlockedPattern {
            package: package.into(),
            pattern: pattern.into(),
            reason: reason.into(),
        }
    }

    /// Create a typosquat error
    pub fn typosquat(
        package: impl Into<String>,
        intended: impl Into<String>,
        distance: usize,
    ) -> Self {
        FirewallError::Typosquat {
            package: package.into(),
            intended: intended.into(),
            distance,
        }
    }

    /// Create an internal not found error
    pub fn internal_not_found(module: impl Into<String>, suggestions: Vec<String>) -> Self {
        FirewallError::InternalNotFound {
            module: module.into(),
            suggestions,
        }
    }

    /// Create a policy error
    pub fn policy_error(config_path: impl Into<String>, reason: impl Into<String>) -> Self {
        FirewallError::PolicyError {
            config_path: config_path.into(),
            reason: reason.into(),
        }
    }
}

impl RanexError {
    /// Create a file read error with automatic SpanTrace capture.
    ///
    /// # Example
    /// ```ignore
    /// let err = RanexError::file_read("/path/to/file", io_error);
    /// ```
    pub fn file_read(path: impl Into<PathBuf>, source: std::io::Error) -> Self {
        RanexError::FileRead {
            path: path.into(),
            source,
            span_trace: SpanTrace::capture(),
        }
    }

    /// Create a file write error with automatic SpanTrace capture.
    pub fn file_write(path: impl Into<PathBuf>, source: std::io::Error) -> Self {
        RanexError::FileWrite {
            path: path.into(),
            source,
            span_trace: SpanTrace::capture(),
        }
    }

    /// Create a generic error with automatic SpanTrace capture.
    pub fn generic(message: impl Into<String>) -> Self {
        RanexError::Generic {
            message: message.into(),
            source: None,
            span_trace: SpanTrace::capture(),
        }
    }

    /// Create a generic error with a source and automatic SpanTrace capture.
    pub fn generic_with_source(
        message: impl Into<String>,
        source: impl std::error::Error + Send + Sync + 'static,
    ) -> Self {
        RanexError::Generic {
            message: message.into(),
            source: Some(Box::new(source)),
            span_trace: SpanTrace::capture(),
        }
    }
}

impl AtlasError {
    /// Create a walk error
    pub fn walk(path: impl Into<PathBuf>, message: impl Into<String>) -> Self {
        AtlasError::Walk {
            path: path.into(),
            message: message.into(),
        }
    }

    /// Create a parse error
    pub fn parse(path: impl Into<PathBuf>, message: impl Into<String>) -> Self {
        AtlasError::Parse {
            path: path.into(),
            message: message.into(),
        }
    }

    /// Create a database error
    pub fn database(operation: impl Into<String>, message: impl Into<String>) -> Self {
        AtlasError::Database {
            operation: operation.into(),
            message: message.into(),
        }
    }

    /// Create an unavailable error (fail-closed)
    pub fn unavailable(reason: impl Into<String>, recoverable: bool) -> Self {
        AtlasError::Unavailable {
            reason: reason.into(),
            recoverable,
        }
    }

    /// Create an index stale error
    pub fn index_stale(reason: impl Into<String>) -> Self {
        AtlasError::IndexStale {
            reason: reason.into(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_atlas_error_display() {
        let err = AtlasError::Parse {
            path: PathBuf::from("/tmp/test.py"),
            message: "unexpected token".to_string(),
        };
        let display = err.to_string();
        assert!(display.contains("test.py"));
        assert!(display.contains("unexpected token"));
    }

    #[test]
    fn test_ranex_error_from_atlas() {
        let atlas_err = AtlasError::NotFound(PathBuf::from("/missing.py"));
        let ranex_err: RanexError = atlas_err.into();
        assert!(ranex_err.to_string().contains("missing.py"));
    }

    #[test]
    fn test_config_error_display() {
        let err = ConfigError::InvalidValue {
            key: "max_file_size".to_string(),
            message: "must be positive".to_string(),
        };
        assert!(err.to_string().contains("max_file_size"));
        assert!(err.to_string().contains("must be positive"));
    }
}
