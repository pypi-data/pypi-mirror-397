//! # ranex-core
//!
//! Core types, errors, configuration, and logging for the Ranex project.
//!
//! This crate provides foundational abstractions used by all other Ranex crates:
//! - **Types**: `Artifact`, `ArtifactKind`, `FileInfo` - core domain models
//! - **Errors**: `RanexError`, `AtlasError` - unified error handling
//! - **Config**: `RanexConfig` - centralized configuration management
//! - **Logging**: Tracing-based structured logging setup
//!
//! ## Usage
//!
//! ```rust
//! use ranex_core::{Artifact, ArtifactKind, RanexConfig};
//! use ranex_core::logging::{self, LogConfig};
//!
//! // Create artifacts
//! let artifact = Artifact::new(
//!     "my_func",
//!     "app.module.my_func",
//!     ArtifactKind::Function,
//!     "app/module.py",
//!     "app.module",
//!     10,
//!     20,
//! );
//! assert_eq!(artifact.symbol_name, "my_func");
//!
//! // Check default config
//! let config = LogConfig::default();
//! assert_eq!(config.level, "info");
//! ```

pub mod config;
pub mod constants;
pub mod error;
pub mod logging;
pub mod types;

// Re-export commonly used types
pub use config::{
    AtlasConfig, FirewallConfig, GovernanceConfig, LoggingConfig, RanexConfig, SecurityConfig,
};
pub use constants::{DEFAULT_DB_FILENAME, DEFAULT_MAX_FILE_SIZE, VERSION};
pub use error::{AtlasError, ConfigError, FirewallError, FirewallResult, RanexError, RanexResult};
pub use logging::{init_logging, LogConfig, LogFormat};
pub use types::{
    Artifact, ArtifactKind, FileInfo, FileStatus, ImportEdge, ImportType, ScanResult, ScanStats,
};
