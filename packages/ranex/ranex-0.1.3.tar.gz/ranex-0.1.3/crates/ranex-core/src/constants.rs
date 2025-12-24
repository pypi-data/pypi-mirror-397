 //! Global constants for Ranex.
//!
//! Centralized location for version info, default values, and magic numbers.

/// Current version of Ranex (synced with Cargo.toml via build script or manual update)
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Default database filename for Atlas index
pub const DEFAULT_DB_FILENAME: &str = "atlas.sqlite";

/// Default maximum file size to parse (1 MB)
pub const DEFAULT_MAX_FILE_SIZE: usize = 1_000_000;

/// Default number of parallel workers for scanning
pub const DEFAULT_PARALLEL_WORKERS: usize = 4;

/// Default patterns to ignore during scanning
pub const DEFAULT_IGNORE_PATTERNS: &[&str] = &[
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".git",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    "*.egg-info",
    "dist",
    "build",
];

/// Ranex configuration directory name (created in project root)
pub const RANEX_DIR: &str = ".ranex";

/// Configuration file name
pub const CONFIG_FILENAME: &str = "config.toml";

/// Ignore file name (similar to .gitignore)
pub const IGNORE_FILENAME: &str = ".ranexignore";

/// Python file extension
pub const PYTHON_EXTENSION: &str = "py";

/// State machine definition file
pub const STATE_YAML_FILENAME: &str = "state.yaml";
