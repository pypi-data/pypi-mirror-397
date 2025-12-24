//! Centralized configuration for all Ranex components.
//!
//! Configuration is loaded from:
//! 1. `.ranex/config.toml` in project root (project-specific)
//! 2. `~/.config/ranex/config.toml` (user defaults)
//! 3. Environment variables (RANEX_*)
//!
//! Priority: ENV > project > user defaults

use crate::constants::{
    CONFIG_FILENAME, DEFAULT_DB_FILENAME, DEFAULT_MAX_FILE_SIZE, DEFAULT_PARALLEL_WORKERS,
    RANEX_DIR,
};
use crate::error::ConfigError;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

/// Root configuration structure.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct RanexConfig {
    /// Atlas-specific configuration
    pub atlas: AtlasConfig,

    /// Security configuration for file access
    pub security: SecurityConfig,

    /// Logging configuration
    pub logging: LoggingConfig,

    /// Firewall configuration
    pub firewall: FirewallConfig,

    /// Governance/fail-closed settings
    pub governance: GovernanceConfig,
}

/// Atlas indexing configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct AtlasConfig {
    /// Patterns to ignore during scanning (in addition to .gitignore)
    pub ignore_patterns: Vec<String>,

    /// Maximum file size to parse (in bytes)
    pub max_file_size: usize,

    /// Number of parallel workers for scanning
    pub parallel_workers: usize,

    /// Database filename (relative to .ranex/)
    pub db_filename: String,

    /// Enable incremental scanning (use file hash cache)
    pub incremental: bool,

    /// Extract docstrings from functions/classes
    pub extract_docstrings: bool,

    /// Detect FastAPI endpoints (all HTTP methods on app/router)
    pub detect_endpoints: bool,

    /// Detect @Contract decorators
    pub detect_contracts: bool,

    /// Auto-scan on first search if no index exists
    pub auto_scan_on_first_search: bool,

    /// Track git commit hash for staleness detection
    pub track_git_commit: bool,
}

/// Security configuration for file access control.
///
/// This controls which files AI agents can access through Atlas.
/// By default, only Python source files and documentation are exposed.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct SecurityConfig {
    /// File extensions that ARE allowed to be read/indexed.
    /// If empty, all non-denied files are allowed.
    pub allowed_extensions: Vec<String>,

    /// File extensions that are NEVER allowed.
    /// Takes precedence over allowed_extensions.
    pub denied_extensions: Vec<String>,

    /// Directory patterns that are NEVER traversed.
    /// Applies in addition to .gitignore and ignore_patterns.
    pub denied_directories: Vec<String>,

    /// File patterns that are NEVER exposed (glob patterns).
    /// E.g., ".env*", "*.pem", "secrets/*"
    pub denied_file_patterns: Vec<String>,

    /// Enable strict mode: only explicitly allowed extensions are readable.
    /// If false, everything except denied is allowed.
    pub strict_mode: bool,
}

/// Governance configuration for fail-closed behavior.
///
/// Controls how the system behaves when Atlas is unavailable or empty.
/// For enterprise deployments, this ensures AI agents cannot proceed
/// blindly when critical context is missing.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct GovernanceConfig {
    /// Require Atlas to have indexed artifacts before allowing operations.
    /// If true and Atlas is empty, all searches return an error.
    pub require_index: bool,

    /// Critical paths that MUST have Atlas results before AI can modify.
    /// Glob patterns, e.g., "app/features/payment/**", "app/auth/**"
    pub critical_paths: Vec<String>,

    /// Minimum artifacts required for a path to be considered "covered".
    /// If a critical path has fewer artifacts, operations are blocked.
    pub min_artifacts_per_critical_path: usize,

    /// Block AI operations entirely if Atlas is unavailable.
    /// When false, operations proceed with warnings.
    pub fail_closed_on_unavailable: bool,

    /// Block AI operations if last scan is older than this (in seconds).
    /// 0 means no staleness check.
    pub max_index_age_seconds: u64,
}

/// Logging configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct LoggingConfig {
    /// Log level: "trace", "debug", "info", "warn", "error"
    pub level: String,

    /// Format: "pretty" or "json"
    pub format: String,

    /// Include source code location in logs
    pub include_location: bool,

    /// Include target module in logs
    pub include_target: bool,
}

/// Firewall (dependency security) configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct FirewallConfig {
    /// Enable dependency firewall
    pub enabled: bool,

    /// Path to allowed dependencies file (relative to project root)
    pub allowed_deps_file: Option<PathBuf>,

    /// Path to blocked dependencies file
    pub blocked_deps_file: Option<PathBuf>,

    /// Enable typosquatting detection
    pub typosquat_detection: bool,

    /// Similarity threshold for typosquatting (0.0-1.0)
    pub typosquat_threshold: f64,
}

impl Default for AtlasConfig {
    fn default() -> Self {
        Self {
            ignore_patterns: vec![
                "__pycache__".to_string(),
                ".venv".to_string(),
                "venv".to_string(),
                "node_modules".to_string(),
                ".git".to_string(),
                ".tox".to_string(),
                ".pytest_cache".to_string(),
                ".mypy_cache".to_string(),
                "*.egg-info".to_string(),
            ],
            max_file_size: DEFAULT_MAX_FILE_SIZE,
            parallel_workers: DEFAULT_PARALLEL_WORKERS,
            db_filename: DEFAULT_DB_FILENAME.to_string(),
            incremental: true,
            extract_docstrings: true,
            detect_endpoints: true,
            detect_contracts: true,
            auto_scan_on_first_search: true, // Zero-config: auto-scan when index is empty
            track_git_commit: true,
        }
    }
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            // Allow Python source, docs, and config by default
            allowed_extensions: vec![
                "py".to_string(),
                "pyi".to_string(),
                "md".to_string(),
                "rst".to_string(),
                "txt".to_string(),
                "yaml".to_string(),
                "yml".to_string(),
                "toml".to_string(),
                "json".to_string(),
            ],
            // NEVER expose secrets or sensitive files
            denied_extensions: vec![
                "pem".to_string(),
                "key".to_string(),
                "crt".to_string(),
                "p12".to_string(),
                "pfx".to_string(),
                "jks".to_string(),
                "keystore".to_string(),
            ],
            // NEVER traverse secret directories
            denied_directories: vec![
                "secrets".to_string(),
                "certs".to_string(),
                "certificates".to_string(),
                "private".to_string(),
                ".ssh".to_string(),
            ],
            // NEVER expose these file patterns
            denied_file_patterns: vec![
                ".env".to_string(),
                ".env.*".to_string(),
                "*.secret".to_string(),
                "*.secrets".to_string(),
                "id_rsa*".to_string(),
                "id_ed25519*".to_string(),
                "*password*".to_string(),
                "*credentials*".to_string(),
            ],
            // Default to permissive mode with explicit denials
            strict_mode: false,
        }
    }
}

impl Default for GovernanceConfig {
    fn default() -> Self {
        Self {
            // By default, allow operations even without index (graceful degradation)
            require_index: false,
            // No critical paths by default
            critical_paths: Vec::new(),
            // Require at least 1 artifact per critical path
            min_artifacts_per_critical_path: 1,
            // By default, warn but don't block
            fail_closed_on_unavailable: false,
            // No staleness check by default (0 = disabled)
            max_index_age_seconds: 0,
        }
    }
}

impl Default for LoggingConfig {
    fn default() -> Self {
        Self {
            level: "info".to_string(),
            format: "pretty".to_string(),
            include_location: false,
            include_target: true,
        }
    }
}

impl Default for FirewallConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            allowed_deps_file: None,
            blocked_deps_file: None,
            typosquat_detection: true,
            typosquat_threshold: 0.8,
        }
    }
}

impl RanexConfig {
    /// Load configuration from project root.
    ///
    /// Looks for `.ranex/config.toml` in the given directory.
    /// Returns default config if file doesn't exist.
    pub fn load(project_root: &Path) -> Result<Self, ConfigError> {
        let config_path = project_root.join(RANEX_DIR).join(CONFIG_FILENAME);

        if config_path.exists() {
            let contents = std::fs::read_to_string(&config_path)?;
            let config: RanexConfig = toml::from_str(&contents)?;
            Ok(config)
        } else {
            Ok(Self::default())
        }
    }

    /// Save configuration to project root.
    ///
    /// Creates `.ranex/` directory if it doesn't exist.
    pub fn save(&self, project_root: &Path) -> Result<(), ConfigError> {
        let ranex_dir = project_root.join(RANEX_DIR);
        std::fs::create_dir_all(&ranex_dir)?;

        let config_path = ranex_dir.join(CONFIG_FILENAME);
        let contents = toml::to_string_pretty(self)?;
        std::fs::write(config_path, contents)?;

        Ok(())
    }

    /// Get the database path for this project.
    pub fn db_path(&self, project_root: &Path) -> PathBuf {
        project_root.join(RANEX_DIR).join(&self.atlas.db_filename)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_default_config() {
        let config = RanexConfig::default();
        assert_eq!(config.atlas.max_file_size, DEFAULT_MAX_FILE_SIZE);
        assert_eq!(config.logging.level, "info");
        assert!(!config.firewall.enabled);
    }

    #[test]
    fn test_save_and_load() {
        let temp_res = TempDir::new();
        assert!(temp_res.is_ok(), "Expected temp dir to be created");
        let Ok(temp) = temp_res else {
            return;
        };
        let config = RanexConfig::default();

        let save_res = config.save(temp.path());
        assert!(save_res.is_ok(), "Expected config to save");

        let loaded_res = RanexConfig::load(temp.path());
        assert!(loaded_res.is_ok(), "Expected config to load");
        let Ok(loaded) = loaded_res else {
            return;
        };

        assert_eq!(loaded.atlas.db_filename, config.atlas.db_filename);
        assert_eq!(loaded.logging.level, config.logging.level);
    }

    #[test]
    fn test_load_nonexistent_returns_default() {
        let temp_res = TempDir::new();
        assert!(temp_res.is_ok(), "Expected temp dir to be created");
        let Ok(temp) = temp_res else {
            return;
        };
        let config_res = RanexConfig::load(temp.path());
        assert!(config_res.is_ok(), "Expected default config to load");
        let Ok(config) = config_res else {
            return;
        };
        assert_eq!(config.atlas.db_filename, DEFAULT_DB_FILENAME);
    }
}
