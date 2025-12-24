//! File system walker for discovering Python files.
//!
//! Uses the `ignore` crate (same as ripgrep) for fast, correct traversal
//! that respects `.gitignore` and `.ranexignore` patterns.

use crate::scanner::IgnoreFilter;
use ignore::WalkBuilder;
use ranex_core::{AtlasConfig, AtlasError};
use std::path::{Path, PathBuf};
use tracing::debug;

/// Options for directory scanning.
#[derive(Debug, Clone)]
pub struct ScanOptions {
    /// Maximum file size to include (bytes)
    pub max_file_size: usize,

    /// Number of parallel threads for walking
    pub threads: usize,

    /// Follow symbolic links
    pub follow_symlinks: bool,

    /// Include hidden files/directories
    pub include_hidden: bool,
}

impl Default for ScanOptions {
    fn default() -> Self {
        Self {
            max_file_size: 1_000_000, // 1 MB
            threads: 4,
            follow_symlinks: false,
            include_hidden: false,
        }
    }
}

impl From<&AtlasConfig> for ScanOptions {
    fn from(config: &AtlasConfig) -> Self {
        Self {
            max_file_size: config.max_file_size,
            threads: config.parallel_workers,
            ..Default::default()
        }
    }
}

/// File system walker that discovers Python files.
///
/// Respects:
/// - `.gitignore` patterns
/// - `.ranexignore` patterns
/// - Built-in ignore patterns (e.g., `__pycache__`, `.venv`)
pub struct FileWalker {
    root: PathBuf,
    options: ScanOptions,
    filter: IgnoreFilter,
}

impl FileWalker {
    /// Create a new file walker.
    ///
    /// # Arguments
    /// * `root` - Project root directory
    /// * `config` - Atlas configuration with ignore patterns
    pub fn new(root: &Path, config: &AtlasConfig) -> Result<Self, AtlasError> {
        let root = root.to_path_buf();
        let options = ScanOptions::from(config);
        let filter = IgnoreFilter::new(&root, &config.ignore_patterns)?;

        Ok(Self {
            root,
            options,
            filter,
        })
    }

    /// Find all Python files in the project.
    ///
    /// # Returns
    /// Vector of paths to `.py` files, excluding ignored patterns.
    pub fn find_python_files(&self) -> Result<Vec<PathBuf>, AtlasError> {
        let mut python_files = Vec::new();

        let walker = WalkBuilder::new(&self.root)
            .hidden(!self.options.include_hidden)
            .follow_links(self.options.follow_symlinks)
            .threads(self.options.threads)
            .add_custom_ignore_filename(".ranexignore")
            .build();

        for entry in walker {
            let entry = entry.map_err(|e| AtlasError::Walk {
                path: self.root.clone(),
                message: e.to_string(),
            })?;

            let path = entry.path();

            // Skip directories
            if path.is_dir() {
                continue;
            }

            // Check if it's a Python file
            if !self.is_python_file(path) {
                continue;
            }

            debug!(path = %path.display(), "Discovered candidate Python file");

            // Check custom ignore patterns
            if self.filter.is_ignored(path) {
                debug!(path = %path.display(), "Skipping Python file ignored by filter");
                continue;
            }

            // Check file size
            if let Ok(metadata) = path.metadata()
                && metadata.len() as usize > self.options.max_file_size
            {
                debug!(
                    path = %path.display(),
                    size = metadata.len(),
                    max = self.options.max_file_size,
                    "Skipping large file"
                );
                continue;
            }

            debug!(path = %path.display(), "Including Python file in scan set");
            python_files.push(path.to_path_buf());
        }

        debug!(count = python_files.len(), "Found Python files");
        Ok(python_files)
    }

    /// Find state machine definition files (`state.yaml`).
    pub fn find_state_machines(&self) -> Result<Vec<PathBuf>, AtlasError> {
        let mut state_files = Vec::new();

        let walker = WalkBuilder::new(&self.root)
            .hidden(!self.options.include_hidden)
            .follow_links(self.options.follow_symlinks)
            .threads(self.options.threads)
            .build();

        for entry in walker.flatten() {
            let path = entry.path();

            if path.is_file()
                && let Some(name) = path.file_name()
                && (name == "state.yaml" || name == "state.yml")
            {
                state_files.push(path.to_path_buf());
            }
        }

        debug!(count = state_files.len(), "Found state machine files");
        Ok(state_files)
    }

    /// Check if a path is a Python file.
    fn is_python_file(&self, path: &Path) -> bool {
        path.extension().map(|ext| ext == "py").unwrap_or(false)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;
    use std::fs;
    use tempfile::TempDir;

    fn create_test_project() -> Result<TempDir, Box<dyn Error>> {
        let temp = TempDir::new()?;

        // Create Python files
        fs::create_dir_all(temp.path().join("app"))?;
        fs::write(temp.path().join("app/main.py"), "def main(): pass")?;
        fs::write(temp.path().join("app/utils.py"), "def helper(): pass")?;

        // Create ignored directory
        fs::create_dir_all(temp.path().join("__pycache__"))?;
        fs::write(temp.path().join("__pycache__/cached.pyc"), "bytecode")?;

        // Create .ranexignore
        fs::write(temp.path().join(".ranexignore"), "test_*.py")?;
        fs::write(temp.path().join("test_ignored.py"), "# ignored")?;

        Ok(temp)
    }

    #[test]
    fn test_find_python_files() -> Result<(), Box<dyn Error>> {
        let temp = create_test_project()?;
        let config = AtlasConfig::default();

        let walker = FileWalker::new(temp.path(), &config)?;
        let files = walker.find_python_files()?;

        // Should find main.py and utils.py, but not __pycache__ or test_ignored.py
        assert_eq!(files.len(), 2);
        assert!(files.iter().any(|p| p.ends_with("main.py")));
        assert!(files.iter().any(|p| p.ends_with("utils.py")));
        Ok(())
    }
}
