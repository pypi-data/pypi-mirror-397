//! Python import statement parser.
//!
//! Extracts import statements from Python source code.

use ranex_core::FirewallResult;
use std::path::Path;

/// A parsed Python import statement.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PythonImport {
    /// The module being imported
    pub module: String,

    /// Specific names imported (for "from X import Y")
    pub names: Vec<String>,

    /// Whether this is a "from X import Y" style import
    pub is_from_import: bool,

    /// Line number in the source file
    pub line: u32,

    /// The original import statement
    pub raw: String,
}

impl PythonImport {
    /// Get the base package name (first component).
    pub fn base_package(&self) -> &str {
        self.module.split('.').next().unwrap_or(&self.module)
    }

    /// Check if this is a relative import.
    pub fn is_relative(&self) -> bool {
        self.module.starts_with('.')
    }

    /// Check if this imports from standard library.
    pub fn is_stdlib(&self) -> bool {
        STDLIB_MODULES.contains(&self.base_package())
    }
}

/// Parse Python imports from source code.
pub fn parse_imports(source: &str) -> Vec<PythonImport> {
    let mut imports = Vec::new();

    for (line_num, line) in source.lines().enumerate() {
        let line = line.trim();

        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        if line.starts_with('"') || line.starts_with('\'') {
            continue;
        }

        if line.starts_with("import ") {
            if let Some(import) = parse_import_statement(line, line_num as u32 + 1) {
                imports.extend(import);
            }
        } else if line.starts_with("from ")
            && let Some(import) = parse_from_import_statement(line, line_num as u32 + 1)
        {
            imports.push(import);
        }
    }

    imports
}

fn parse_import_statement(line: &str, line_num: u32) -> Option<Vec<PythonImport>> {
    let rest = line.strip_prefix("import ")?.trim();
    let mut imports = Vec::new();

    for part in rest.split(',') {
        let part = part.trim();
        let module = if let Some(idx) = part.find(" as ") {
            &part[..idx]
        } else {
            part
        };

        let module = module.trim();
        if !module.is_empty() {
            imports.push(PythonImport {
                module: module.to_string(),
                names: vec![],
                is_from_import: false,
                line: line_num,
                raw: line.to_string(),
            });
        }
    }

    if imports.is_empty() {
        None
    } else {
        Some(imports)
    }
}

fn parse_from_import_statement(line: &str, line_num: u32) -> Option<PythonImport> {
    let rest = line.strip_prefix("from ")?.trim();
    let import_idx = rest.find(" import ")?;
    let module = rest[..import_idx].trim();
    let names_part = rest[import_idx + 8..].trim();

    let names = if names_part == "*" {
        vec!["*".to_string()]
    } else {
        let names_part = names_part
            .trim_start_matches('(')
            .trim_end_matches(')')
            .trim_end_matches(',');

        names_part
            .split(',')
            .map(|n| {
                let n = n.trim();
                if let Some(idx) = n.find(" as ") {
                    n[..idx].trim().to_string()
                } else {
                    n.to_string()
                }
            })
            .filter(|n| !n.is_empty())
            .collect()
    };

    Some(PythonImport {
        module: module.to_string(),
        names,
        is_from_import: true,
        line: line_num,
        raw: line.to_string(),
    })
}

/// Parse imports from a file.
pub fn parse_imports_from_file(path: &Path) -> FirewallResult<Vec<PythonImport>> {
    let content = std::fs::read_to_string(path)?;
    Ok(parse_imports(&content))
}

/// Python standard library modules (partial list).
const STDLIB_MODULES: &[&str] = &[
    "abc",
    "argparse",
    "ast",
    "asyncio",
    "base64",
    "collections",
    "configparser",
    "contextlib",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "functools",
    "gc",
    "glob",
    "gzip",
    "hashlib",
    "http",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "os",
    "pathlib",
    "pickle",
    "platform",
    "pprint",
    "queue",
    "random",
    "re",
    "shutil",
    "signal",
    "socket",
    "sqlite3",
    "ssl",
    "string",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
    "time",
    "traceback",
    "typing",
    "unittest",
    "urllib",
    "uuid",
    "warnings",
    "weakref",
    "xml",
    "zipfile",
    "_thread",
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_import() {
        let source = "import requests";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.module, "requests");
        assert!(!first.is_from_import);
    }

    #[test]
    fn test_parse_from_import() {
        let source = "from fastapi import FastAPI, Depends";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.module, "fastapi");
        assert_eq!(first.names, vec!["FastAPI", "Depends"]);
        assert!(first.is_from_import);
    }

    #[test]
    fn test_stdlib_detection() {
        let source = "import os\nimport requests";
        let imports = parse_imports(source);

        assert!(imports.len() >= 2);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert!(first.is_stdlib());

        let second = imports.get(1);
        assert!(second.is_some());
        let Some(second) = second else {
            return;
        };
        assert!(!second.is_stdlib());
    }

    #[test]
    fn test_multiple_imports_on_line() {
        let source = "import os, sys, json";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 3);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.module, "os");

        let second = imports.get(1);
        assert!(second.is_some());
        let Some(second) = second else {
            return;
        };
        assert_eq!(second.module, "sys");

        let third = imports.get(2);
        assert!(third.is_some());
        let Some(third) = third else {
            return;
        };
        assert_eq!(third.module, "json");
    }

    #[test]
    fn test_import_with_alias() {
        let source = "import numpy as np";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.module, "numpy");
    }

    #[test]
    fn test_from_import_with_parentheses() {
        let source = "from typing import (Optional, List, Dict,)";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.names, vec!["Optional", "List", "Dict"]);
    }

    #[test]
    fn test_relative_import() {
        let source = "from .models import User";
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert!(first.is_relative());
        assert_eq!(first.module, ".models");
    }

    #[test]
    fn test_skip_comments_and_strings() {
        let source = r#"
# import fake_package
"import not_real"
import real_package
        "#;
        let imports = parse_imports(source);

        assert_eq!(imports.len(), 1);
        let first = imports.first();
        assert!(first.is_some());
        let Some(first) = first else {
            return;
        };
        assert_eq!(first.module, "real_package");
    }

    #[test]
    fn test_base_package() {
        let import = PythonImport {
            module: "django.contrib.auth".to_string(),
            names: vec![],
            is_from_import: false,
            line: 1,
            raw: "import django.contrib.auth".to_string(),
        };

        assert_eq!(import.base_package(), "django");
    }
}
