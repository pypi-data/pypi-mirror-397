//! Python AST parsing via PyO3.
//!
//! Uses Python's built-in `ast` module for accurate parsing of all Python syntax.
//! This approach ensures 100% compatibility with Python 3.8-3.12+.

use crate::parser::extractor::{CallInfo, DefinitionInfo, ImportInfo, SymbolExtractor};
use pyo3::prelude::*;
use ranex_core::AtlasError;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tracing::{debug, trace};

/// Result of parsing a Python file.
#[derive(Debug, Clone)]
pub struct ParseResult {
    /// Content hash for change detection
    pub hash: String,

    /// Extracted definitions (functions, classes)
    pub definitions: Vec<DefinitionInfo>,

    /// Extracted import statements
    pub imports: Vec<ImportInfo>,

    /// Extracted function calls
    pub calls: Vec<CallInfo>,

    /// Number of lines in file
    pub line_count: usize,

    /// Whether file was loaded from cache
    pub from_cache: bool,
}

type ExtractedAst = (Vec<DefinitionInfo>, Vec<ImportInfo>, Vec<CallInfo>);

/// Python AST parser with caching support.
///
/// Uses Python's `ast.parse()` via PyO3 for accurate parsing.
pub struct PythonParser {
    /// Cache of file hashes for incremental parsing
    cache: HashMap<PathBuf, String>,
}

impl PythonParser {
    /// Create a new Python parser.
    pub fn new() -> Result<Self, AtlasError> {
        // Verify Python is available
        Python::attach(|py| -> Result<(), AtlasError> {
            py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import Python ast module: {}", e),
            })?;
            Ok(())
        })?;

        Ok(Self {
            cache: HashMap::new(),
        })
    }

    /// Create parser with existing cache.
    pub fn with_cache(cache: HashMap<PathBuf, String>) -> Result<Self, AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import Python ast module: {}", e),
            })?;
            Ok(())
        })?;

        Ok(Self { cache })
    }

    /// Parse a Python file.
    ///
    /// # Arguments
    /// * `path` - Path to the Python file
    ///
    /// # Returns
    /// ParseResult with extracted definitions and metadata.
    pub fn parse_file(&mut self, path: &Path) -> Result<ParseResult, AtlasError> {
        // Read file content
        let content = std::fs::read_to_string(path).map_err(|e| AtlasError::Parse {
            path: path.to_path_buf(),
            message: format!("Failed to read file: {}", e),
        })?;

        // Calculate hash
        let hash = self.hash_content(&content);

        // Check cache
        if let Some(cached_hash) = self.cache.get(path)
            && cached_hash == &hash
        {
            trace!(path = %path.display(), "Using cached parse result");
            return Ok(ParseResult {
                hash,
                definitions: Vec::new(),
                imports: Vec::new(),
                calls: Vec::new(),
                line_count: content.lines().count(),
                from_cache: true,
            });
        }

        // Parse with Python AST - extract definitions, imports, and calls
        let (definitions, imports, calls) = self.parse_with_python_ast(path, &content)?;

        // Update cache
        self.cache.insert(path.to_path_buf(), hash.clone());

        debug!(
            path = %path.display(),
            definitions = definitions.len(),
            imports = imports.len(),
            calls = calls.len(),
            "Parsed file"
        );

        Ok(ParseResult {
            hash,
            definitions,
            imports,
            calls,
            line_count: content.lines().count(),
            from_cache: false,
        })
    }

    /// Parse using Python's ast module.
    ///
    /// Returns (definitions, imports, calls) tuple.
    fn parse_with_python_ast(
        &self,
        path: &Path,
        content: &str,
    ) -> Result<ExtractedAst, AtlasError> {
        Python::attach(|py| {
            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: path.to_path_buf(),
                message: format!("Failed to import ast: {}", e),
            })?;

            // Parse to AST
            let tree = ast
                .call_method1("parse", (content,))
                .map_err(|e| AtlasError::Syntax {
                    path: path.to_path_buf(),
                    line: self.extract_line_from_error(&e),
                    message: e.to_string(),
                })?;

            // Extract definitions, imports, and calls using our extractor
            let extractor = SymbolExtractor::new();
            let definitions = extractor.extract_from_tree(tree.clone())?;
            let imports = extractor.extract_imports_from_tree(tree.clone())?;
            let calls = extractor.extract_calls_from_tree(tree)?;

            Ok((definitions, imports, calls))
        })
    }

    /// Calculate SHA256 hash of content.
    fn hash_content(&self, content: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(content.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    /// Extract line number from Python error message.
    fn extract_line_from_error(&self, error: &PyErr) -> usize {
        // Try to extract line number from Python SyntaxError
        let msg = error.to_string();
        if let Some(pos) = msg.find("line ") {
            let rest = &msg[pos + 5..];
            if let Some(end) = rest.find(|c: char| !c.is_ascii_digit())
                && let Ok(line) = rest[..end].parse::<usize>()
            {
                return line;
            }
        }
        0
    }

    /// Get the current cache.
    pub fn cache(&self) -> &HashMap<PathBuf, String> {
        &self.cache
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_parse_simple_function() -> Result<(), AtlasError> {
        let temp = TempDir::new().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: e.to_string(),
        })?;
        let file_path = temp.path().join("test.py");
        fs::write(&file_path, "def hello():\n    pass\n").map_err(|e| AtlasError::Parse {
            path: file_path.clone(),
            message: e.to_string(),
        })?;

        let mut parser = PythonParser::new()?;
        let result = parser.parse_file(&file_path)?;

        assert!(!result.from_cache);
        assert!(!result.definitions.is_empty());
        Ok(())
    }

    #[test]
    fn test_cache_hit() -> Result<(), AtlasError> {
        let temp = TempDir::new().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: e.to_string(),
        })?;
        let file_path = temp.path().join("test.py");
        fs::write(&file_path, "def cached(): pass").map_err(|e| AtlasError::Parse {
            path: file_path.clone(),
            message: e.to_string(),
        })?;

        let mut parser = PythonParser::new()?;

        // First parse
        let result1 = parser.parse_file(&file_path)?;
        assert!(!result1.from_cache);

        // Second parse (should hit cache)
        let result2 = parser.parse_file(&file_path)?;
        assert!(result2.from_cache);
        Ok(())
    }

    #[test]
    fn test_syntax_error() -> Result<(), AtlasError> {
        let temp = TempDir::new().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: e.to_string(),
        })?;
        let file_path = temp.path().join("bad.py");
        fs::write(&file_path, "def broken(\n").map_err(|e| AtlasError::Parse {
            path: file_path.clone(),
            message: e.to_string(),
        })?;

        let mut parser = PythonParser::new()?;
        let err = match parser.parse_file(&file_path) {
            Ok(_) => {
                return Err(AtlasError::Parse {
                    path: file_path,
                    message: "Expected syntax error, parse succeeded".to_string(),
                });
            }
            Err(e) => e,
        };

        match err {
            AtlasError::Syntax { line, .. } => {
                assert!(line > 0);
            }
            other => {
                return Err(AtlasError::Parse {
                    path: PathBuf::new(),
                    message: format!("Expected AtlasError::Syntax, got: {}", other),
                });
            }
        }

        Ok(())
    }
}
