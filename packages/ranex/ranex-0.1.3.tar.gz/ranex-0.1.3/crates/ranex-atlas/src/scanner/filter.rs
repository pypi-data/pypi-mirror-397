//! Ignore pattern filtering.
//!
//! Handles `.ranexignore` and custom ignore patterns.
//!
//! ## Default Ignored Directories
//!
//! The following directories are ignored by default:
//! - `venv/`, `.venv/`, `env/`, `.env/` - Python virtual environments
//! - `__pycache__/` - Python bytecode cache
//! - `.git/` - Git repository
//! - `node_modules/` - Node.js dependencies
//! - `*.egg-info/`, `dist/`, `build/` - Python build artifacts
//! - `.tox/`, `.nox/`, `.pytest_cache/` - Test runners
//!
//! You can override these with a `.ranexignore` file in your project root.

use ranex_core::AtlasError;
use std::path::Path;
use tracing::debug;

/// Default directories to ignore (always excluded unless overridden).
/// These patterns match directory names anywhere in the path.
const DEFAULT_IGNORE_DIRS: &[&str] = &[
    // Python virtual environments
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
    ".virtualenv",
    // Python build/cache
    "__pycache__",
    "*.egg-info",
    "dist",
    "build",
    "eggs",
    ".eggs",
    // Version control
    ".git",
    ".hg",
    ".svn",
    // IDE/Editor
    ".idea",
    ".vscode",
    // Node.js
    "node_modules",
    // Test runners
    ".tox",
    ".nox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    // Ranex release/install directories
    ".ranex",        // Our database directory
    "ranex-[0-9]*",       // Release packages (ranex-0.1.0, etc.)
    "site-packages", // Installed packages
];

/// Filter for ignoring files based on patterns.
pub struct IgnoreFilter {
    patterns: Vec<glob::Pattern>,
    ignore_dirs: Vec<String>,
}

impl IgnoreFilter {
    /// Create a new ignore filter.
    ///
    /// # Arguments
    /// * `root` - Project root (for loading `.ranexignore`)
    /// * `extra_patterns` - Additional patterns from configuration
    pub fn new(root: &Path, extra_patterns: &[String]) -> Result<Self, AtlasError> {
        let mut patterns = Vec::new();

        // Load .ranexignore if it exists
        let ranexignore_path = root.join(".ranexignore");
        if ranexignore_path.exists()
            && let Ok(content) = std::fs::read_to_string(&ranexignore_path)
        {
            for line in content.lines() {
                let line = line.trim();
                if line.is_empty() || line.starts_with('#') {
                    continue;
                }
                if let Ok(pattern) = glob::Pattern::new(line) {
                    patterns.push(pattern);
                }
            }
        }

        // Add extra patterns from config
        for pattern_str in extra_patterns {
            if let Ok(pattern) = glob::Pattern::new(pattern_str) {
                patterns.push(pattern);
            }
        }

        // Build list of directories to ignore
        let ignore_dirs: Vec<String> = DEFAULT_IGNORE_DIRS.iter().map(|s| s.to_string()).collect();

        debug!(
            default_dirs = ignore_dirs.len(),
            custom_patterns = patterns.len(),
            "Initialized ignore filter"
        );

        Ok(Self {
            patterns,
            ignore_dirs,
        })
    }

    /// Check if a path should be ignored.
    pub fn is_ignored(&self, path: &Path) -> bool {
        // First check if any path component matches a default ignore directory
        for component in path.components() {
            if let std::path::Component::Normal(name) = component {
                let name_str = name.to_string_lossy();
                for ignore_dir in &self.ignore_dirs {
                    // Exact match for most patterns
                    if &*name_str == ignore_dir {
                        return true;
                    }
                    // Glob match for patterns like *.egg-info
                    if ignore_dir.contains('*')
                        && let Ok(pattern) = glob::Pattern::new(ignore_dir)
                        && pattern.matches(&name_str)
                    {
                        return true;
                    }
                }
            }
        }

        // Then check custom patterns
        let path_str = path.to_string_lossy();

        for pattern in &self.patterns {
            // Check against full path
            if pattern.matches(&path_str) {
                return true;
            }

            // Check against filename only
            if let Some(filename) = path.file_name()
                && pattern.matches(&filename.to_string_lossy())
            {
                return true;
            }
        }

        false
    }

    /// Add a pattern to the filter.
    pub fn add_pattern(&mut self, pattern: &str) -> Result<(), AtlasError> {
        let pattern = glob::Pattern::new(pattern).map_err(|e| AtlasError::Walk {
            path: std::path::PathBuf::new(),
            message: format!("Invalid glob pattern '{}': {}", pattern, e),
        })?;
        self.patterns.push(pattern);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;

    #[test]
    fn test_ignore_patterns() -> Result<(), Box<dyn Error>> {
        let filter = IgnoreFilter::new(
            Path::new("/fake"),
            &["__pycache__".to_string(), "*.pyc".to_string()],
        )?;

        assert!(filter.is_ignored(Path::new("__pycache__")));
        assert!(filter.is_ignored(Path::new("module.pyc")));
        assert!(!filter.is_ignored(Path::new("main.py")));
        Ok(())
    }

    #[test]
    fn test_wildcard_patterns() -> Result<(), Box<dyn Error>> {
        let filter = IgnoreFilter::new(Path::new("/fake"), &["test_*.py".to_string()])?;

        assert!(filter.is_ignored(Path::new("test_main.py")));
        assert!(filter.is_ignored(Path::new("test_utils.py")));
        assert!(!filter.is_ignored(Path::new("main.py")));
        Ok(())
    }

    #[test]
    fn test_default_venv_ignored() -> Result<(), Box<dyn Error>> {
        let filter = IgnoreFilter::new(Path::new("/fake"), &[])?;

        // Virtual environments should be ignored by default
        assert!(filter.is_ignored(Path::new(
            "/project/venv/lib/python3.12/site-packages/requests/api.py"
        )));
        assert!(filter.is_ignored(Path::new("/project/.venv/lib/site-packages/module.py")));
        assert!(filter.is_ignored(Path::new("venv/bin/activate.py")));

        // Regular project files should NOT be ignored
        assert!(!filter.is_ignored(Path::new("/project/app/main.py")));
        assert!(!filter.is_ignored(Path::new("/project/src/module.py")));
        Ok(())
    }

    #[test]
    fn test_default_cache_ignored() -> Result<(), Box<dyn Error>> {
        let filter = IgnoreFilter::new(Path::new("/fake"), &[])?;

        // Cache directories should be ignored
        assert!(filter.is_ignored(Path::new("/project/__pycache__/module.cpython-312.pyc")));
        assert!(filter.is_ignored(Path::new("/project/.pytest_cache/data.py")));
        assert!(filter.is_ignored(Path::new("/project/.mypy_cache/module.py")));
        Ok(())
    }

    #[test]
    fn test_default_build_ignored() -> Result<(), Box<dyn Error>> {
        let filter = IgnoreFilter::new(Path::new("/fake"), &[])?;

        // Build directories should be ignored
        assert!(filter.is_ignored(Path::new("/project/dist/package.py")));
        assert!(filter.is_ignored(Path::new("/project/build/lib/module.py")));
        assert!(filter.is_ignored(Path::new("/project/mypackage.egg-info/PKG-INFO")));
        Ok(())
    }
}
