//! Centralized logging configuration for all Ranex crates.
//!
//! # Usage
//!
//! Call `init_logging()` once at application startup:
//!
//! ```rust
//! use ranex_core::logging::{LogConfig, LogFormat};
//!
//! // Create different logging configurations
//! let default_config = LogConfig::default();
//! assert_eq!(default_config.level, "info");
//! assert_eq!(default_config.format, LogFormat::Pretty);
//!
//! let debug_config = LogConfig::debug();
//! assert_eq!(debug_config.level, "debug");
//! assert!(debug_config.include_location);
//!
//! let prod_config = LogConfig::production();
//! assert_eq!(prod_config.format, LogFormat::Json);
//! ```
//!
//! Note: `init_logging()` should only be called once per process, typically in `main()`.
//!
//! # Log Levels
//!
//! - `trace`: Very verbose, internal state
//! - `debug`: Development debugging
//! - `info`: Normal operation milestones
//! - `warn`: Recoverable issues
//! - `error`: Failures requiring attention

use std::sync::OnceLock;
use tracing_error::ErrorLayer;
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

/// Global flag to track if logging has been initialized
static INITIALIZED: OnceLock<bool> = OnceLock::new();

/// Logging configuration options.
#[derive(Debug, Clone)]
pub struct LogConfig {
    /// Log level filter (e.g., "info", "debug", "ranex_atlas=debug")
    pub level: String,

    /// Output format
    pub format: LogFormat,

    /// Include source code location in logs
    pub include_location: bool,

    /// Include target module in logs
    pub include_target: bool,
}

/// Log output format.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum LogFormat {
    /// Human-readable colored output
    #[default]
    Pretty,

    /// Structured JSON output (for log aggregation)
    Json,

    /// Compact single-line output
    Compact,
}

impl Default for LogConfig {
    fn default() -> Self {
        Self {
            level: "info".to_string(),
            format: LogFormat::Pretty,
            include_location: false,
            include_target: true,
        }
    }
}

impl LogConfig {
    /// Create config for debug logging
    pub fn debug() -> Self {
        Self {
            level: "debug".to_string(),
            format: LogFormat::Pretty,
            include_location: true,
            include_target: true,
        }
    }

    /// Create config for production (JSON format)
    pub fn production() -> Self {
        Self {
            level: "info".to_string(),
            format: LogFormat::Json,
            include_location: false,
            include_target: true,
        }
    }

    /// Create config from environment or use defaults
    pub fn from_env() -> Self {
        let level = std::env::var("RANEX_LOG")
            .or_else(|_| std::env::var("RUST_LOG"))
            .unwrap_or_else(|_| "info".to_string());

        let format = std::env::var("RANEX_LOG_FORMAT")
            .map(|s| match s.to_lowercase().as_str() {
                "json" => LogFormat::Json,
                "compact" => LogFormat::Compact,
                _ => LogFormat::Pretty,
            })
            .unwrap_or(LogFormat::Pretty);

        Self {
            level,
            format,
            include_location: false,
            include_target: true,
        }
    }
}

/// Initialize the global tracing subscriber.
///
/// Call this ONCE at application startup. Subsequent calls are no-ops.
///
/// This function:
/// - Sets up tracing with the specified format (Pretty, JSON, or Compact)
/// - Enables SpanTrace capture via ErrorLayer (for error context)
/// - Installs a panic hook to log panics with tracing
///
/// # Example
///
/// ```rust,no_run
/// use ranex_core::logging::{init_logging, LogConfig};
///
/// // Initialize logging (should only be called once per process)
/// init_logging(LogConfig::default());
///
/// // Now you can use tracing macros
/// tracing::info!("Logging initialized");
/// ```
///
/// Note: This doc test uses `no_run` because `init_logging` modifies global state
/// and can only be called once per process. The code is still compiled to verify correctness.
pub fn init_logging(config: LogConfig) {
    // Only initialize once
    if INITIALIZED.get().is_some() {
        return;
    }

    let filter = EnvFilter::try_from_default_env()
        .or_else(|_| EnvFilter::try_new(&config.level))
        .unwrap_or_else(|_| EnvFilter::new("info"));

    // ErrorLayer enables SpanTrace::capture() to work
    let error_layer = ErrorLayer::default();

    let result = match config.format {
        LogFormat::Pretty => {
            let layer = fmt::layer()
                .with_target(config.include_target)
                .with_file(config.include_location)
                .with_line_number(config.include_location)
                .with_ansi(true)
                .with_writer(std::io::stderr);

            tracing_subscriber::registry()
                .with(filter)
                .with(error_layer)
                .with(layer)
                .try_init()
        }
        LogFormat::Json => {
            let layer = fmt::layer()
                .json()
                .with_target(config.include_target)
                .with_file(config.include_location)
                .with_line_number(config.include_location)
                .with_writer(std::io::stderr);

            tracing_subscriber::registry()
                .with(filter)
                .with(error_layer)
                .with(layer)
                .try_init()
        }
        LogFormat::Compact => {
            let layer = fmt::layer()
                .compact()
                .with_target(config.include_target)
                .with_file(config.include_location)
                .with_line_number(config.include_location)
                .with_writer(std::io::stderr);

            tracing_subscriber::registry()
                .with(filter)
                .with(error_layer)
                .with(layer)
                .try_init()
        }
    };

    if result.is_ok() {
        let _ = INITIALIZED.set(true);
        install_panic_hook();
    }
}

/// Install a panic hook that logs panics using tracing.
///
/// This ensures panics are captured in the same log stream as other errors,
/// making them visible to AI agents debugging the code.
fn install_panic_hook() {
    let default_hook = std::panic::take_hook();

    std::panic::set_hook(Box::new(move |panic_info| {
        // Extract panic message
        let message = panic_info
            .payload()
            .downcast_ref::<&str>()
            .map(|s| s.to_string())
            .or_else(|| panic_info.payload().downcast_ref::<String>().cloned())
            .unwrap_or_else(|| "Unknown panic".to_string());

        // Extract location
        let location = panic_info
            .location()
            .map(|l| format!("{}:{}:{}", l.file(), l.line(), l.column()));

        // Log the panic with tracing
        tracing::error!(
            panic = true,
            message = %message,
            location = ?location,
            "PANIC - This is a bug in Ranex. Please report it."
        );

        // Call the default hook (prints to stderr)
        default_hook(panic_info);
    }));
}

/// Check if logging has been initialized
pub fn is_initialized() -> bool {
    INITIALIZED.get().copied().unwrap_or(false)
}

/// Initialize logging with environment-based configuration
pub fn init_from_env() {
    init_logging(LogConfig::from_env());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = LogConfig::default();
        assert_eq!(config.level, "info");
        assert_eq!(config.format, LogFormat::Pretty);
    }

    #[test]
    fn test_debug_config() {
        let config = LogConfig::debug();
        assert_eq!(config.level, "debug");
        assert!(config.include_location);
    }

    #[test]
    fn test_production_config() {
        let config = LogConfig::production();
        assert_eq!(config.format, LogFormat::Json);
        assert!(!config.include_location);
    }
}
