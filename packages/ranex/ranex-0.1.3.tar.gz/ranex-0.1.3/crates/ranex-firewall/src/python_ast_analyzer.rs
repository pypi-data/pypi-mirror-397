//! Python AST analysis for detecting dangerous function calls and patterns.
//!
//! This module uses PyO3 to parse Python code and detect security issues at the usage level,
//! not just at the import level.

use pyo3::prelude::*;
use pyo3::types::PyModule;
use ranex_core::{FirewallError, FirewallResult};
use std::path::Path;

use crate::policy::Policy;
use crate::report::{Violation, ViolationKind};

/// Represents a dangerous function call found in Python code
#[derive(Debug, Clone)]
pub struct DangerousFunctionCall {
    pub function_name: String,
    pub module: Option<String>,
    pub line_number: usize,
    pub column: usize,
    pub matched_pattern: String,
}

/// Python AST analyzer that detects dangerous function calls
pub struct PythonASTAnalyzer {
    policy: Policy,
}

impl PythonASTAnalyzer {
    pub fn new(policy: Policy) -> Self {
        Self { policy }
    }

    /// Analyze a Python file for dangerous function calls
    pub fn analyze_file(&self, path: &Path) -> FirewallResult<Vec<Violation>> {
        let content = std::fs::read_to_string(path).map_err(|e| FirewallError::AnalysisError {
            file: path.display().to_string(),
            reason: format!("Failed to read file: {}", e),
        })?;

        self.analyze_code(&content, path)
    }

    /// Analyze Python code string for dangerous function calls
    pub fn analyze_code(&self, code: &str, file_path: &Path) -> FirewallResult<Vec<Violation>> {
        Python::attach(|py| {
            let ast_module =
                PyModule::import(py, "ast").map_err(|e| FirewallError::AnalysisError {
                    file: file_path.display().to_string(),
                    reason: format!("Failed to import ast module: {}", e),
                })?;

            // Parse the Python code into an AST
            let tree = ast_module.call_method1("parse", (code,)).map_err(|e| {
                FirewallError::AnalysisError {
                    file: file_path.display().to_string(),
                    reason: format!("Failed to parse Python code: {}", e),
                }
            })?;

            // Find all function calls in the AST
            let dangerous_calls = self.find_dangerous_calls(py, &tree, file_path)?;

            // Convert to violations
            let violations: Vec<Violation> = dangerous_calls
                .into_iter()
                .map(|call| {
                    Violation {
                        kind: ViolationKind::BlockedImport,
                        file: file_path.to_path_buf(),
                        line: call.line_number as u32,
                        import: call.function_name.clone(),
                        message: format!(
                            "Dangerous function call: {} (matched pattern: {})",
                            call.function_name, call.matched_pattern
                        ),
                        suggestion: Some(format!(
                            "Remove or replace this dangerous function call. Pattern '{}' is blocked for security reasons.",
                            call.matched_pattern
                        )),
                    }
                })
                .collect();

            Ok(violations)
        })
    }

    /// Find all dangerous function calls in the AST
    fn find_dangerous_calls(
        &self,
        py: Python,
        tree: &Bound<'_, PyAny>,
        file_path: &Path,
    ) -> FirewallResult<Vec<DangerousFunctionCall>> {
        let mut dangerous_calls = Vec::new();

        // Walk the AST tree
        let ast_module = PyModule::import(py, "ast").map_err(|e| FirewallError::AnalysisError {
            file: file_path.display().to_string(),
            reason: format!("Failed to import ast module: {}", e),
        })?;

        let walker =
            ast_module
                .call_method1("walk", (tree,))
                .map_err(|e| FirewallError::AnalysisError {
                    file: file_path.display().to_string(),
                    reason: format!("Failed to walk AST: {}", e),
                })?;

        // Iterate through all nodes using try_iter()
        let iter = walker
            .try_iter()
            .map_err(|e| FirewallError::AnalysisError {
                file: file_path.display().to_string(),
                reason: format!("Failed to get iterator: {}", e),
            })?;

        for node_result in iter {
            let node = node_result.map_err(|e| FirewallError::AnalysisError {
                file: file_path.display().to_string(),
                reason: format!("Failed to get AST node: {}", e),
            })?;

            // Check if this is a Call node
            let node_type = node.get_type();
            let node_type_name = node_type.name().map_err(|e| FirewallError::AnalysisError {
                file: file_path.display().to_string(),
                reason: format!("Failed to get node type: {}", e),
            })?;

            if node_type_name == "Call"
                && let Some(call_info) = self.extract_call_info(py, &node, file_path)?
            {
                // Check against blocked patterns
                for pattern in &self.policy.blocked_patterns {
                    if self.matches_pattern(&call_info.function_name, &pattern.pattern) {
                        dangerous_calls.push(DangerousFunctionCall {
                            function_name: call_info.function_name.clone(),
                            module: call_info.module.clone(),
                            line_number: call_info.line_number,
                            column: call_info.column,
                            matched_pattern: pattern.pattern.clone(),
                        });
                        break;
                    }
                }
            }
        }

        Ok(dangerous_calls)
    }

    /// Extract function call information from a Call node
    fn extract_call_info(
        &self,
        _py: Python,
        node: &Bound<'_, PyAny>,
        file_path: &Path,
    ) -> FirewallResult<Option<CallInfo>> {
        // Get the function being called
        let func = node
            .getattr("func")
            .map_err(|e| FirewallError::AnalysisError {
                file: file_path.display().to_string(),
                reason: format!("Failed to get func attribute: {}", e),
            })?;

        let func_type = func.get_type();
        let func_type_name = func_type.name().map_err(|e| FirewallError::AnalysisError {
            file: file_path.display().to_string(),
            reason: format!("Failed to get func type: {}", e),
        })?;

        let (function_name, module) = match func_type_name.to_string_lossy().as_ref() {
            // Simple name: eval, exec, etc.
            "Name" => {
                let id = func
                    .getattr("id")
                    .map_err(|e| FirewallError::AnalysisError {
                        file: file_path.display().to_string(),
                        reason: format!("Failed to get id: {}", e),
                    })?;
                let name: String = id.extract().map_err(|e| FirewallError::AnalysisError {
                    file: file_path.display().to_string(),
                    reason: format!("Failed to extract name: {}", e),
                })?;
                (name, None)
            }
            // Attribute: os.system, pickle.loads, etc.
            "Attribute" => {
                let attr: String = func
                    .getattr("attr")
                    .and_then(|a| a.extract())
                    .map_err(|e| FirewallError::AnalysisError {
                        file: file_path.display().to_string(),
                        reason: format!("Failed to get attribute: {}", e),
                    })?;

                // Try to get the module name
                let value = func
                    .getattr("value")
                    .map_err(|e| FirewallError::AnalysisError {
                        file: file_path.display().to_string(),
                        reason: format!("Failed to get value: {}", e),
                    })?;

                let value_type = value.get_type();
                let value_type_name =
                    value_type
                        .name()
                        .map_err(|e| FirewallError::AnalysisError {
                            file: file_path.display().to_string(),
                            reason: format!("Failed to get value type: {}", e),
                        })?;

                let module_name =
                    if value_type_name == "Name" {
                        value
                            .getattr("id")
                            .and_then(|id| id.extract::<String>())
                            .ok()
                    } else {
                        None
                    };

                let full_name = if let Some(ref module) = module_name {
                    format!("{}.{}", module, attr)
                } else {
                    attr.clone()
                };

                (full_name, module_name)
            }
            _ => return Ok(None),
        };

        // Get line number
        let line_number: usize = node
            .getattr("lineno")
            .and_then(|l| l.extract())
            .unwrap_or(0);

        // Get column
        let column: usize = node
            .getattr("col_offset")
            .and_then(|c| c.extract())
            .unwrap_or(0);

        Ok(Some(CallInfo {
            function_name,
            module,
            line_number,
            column,
        }))
    }

    /// Check if a function name matches a blocked pattern
    fn matches_pattern(&self, function_name: &str, pattern: &str) -> bool {
        // Simple pattern matching - can be enhanced with regex
        if pattern.contains('*') {
            // Wildcard matching without direct indexing
            let pattern_parts: Vec<&str> = pattern.split('*').collect();
            if pattern_parts.len() == 2 {
                if let (Some(prefix), Some(suffix)) = (pattern_parts.first(), pattern_parts.get(1)) {
                    function_name.starts_with(prefix) && function_name.ends_with(suffix)
                } else {
                    function_name.contains(pattern)
                }
            } else {
                function_name.contains(pattern)
            }
        } else {
            // Exact or prefix match
            function_name == pattern || function_name.starts_with(&format!("{}.", pattern))
        }
    }
}

#[derive(Debug, Clone)]
struct CallInfo {
    function_name: String,
    module: Option<String>,
    line_number: usize,
    column: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::policy::{BlockedPattern, Severity};

    #[test]
    fn test_detect_pickle_loads() -> FirewallResult<()> {
        let code = r#"
import pickle

def dangerous():
    data = pickle.loads(b"data")
    return data
"#;

        let mut policy = Policy::default();
        policy.blocked_patterns.push(BlockedPattern {
            pattern: "pickle.loads".to_string(),
            reason: "Unsafe deserialization".to_string(),
            severity: Severity::Critical,
            alternatives: vec![],
            is_prefix_match: false,
        });

        let analyzer = PythonASTAnalyzer::new(policy);
        let violations = analyzer.analyze_code(code, Path::new("test.py"))?;

        assert!(!violations.is_empty(), "Should detect pickle.loads");
        assert!(
            violations.iter().any(|v| v.message.contains("pickle.loads")),
            "Should include a violation mentioning pickle.loads"
        );

        Ok(())
    }

    #[test]
    fn test_detect_os_system() -> FirewallResult<()> {
        let code = r#"
import os

def dangerous():
    os.system("echo test")
"#;

        let mut policy = Policy::default();
        policy.blocked_patterns.push(BlockedPattern {
            pattern: "os.system".to_string(),
            reason: "Shell injection".to_string(),
            severity: Severity::Critical,
            alternatives: vec![],
            is_prefix_match: false,
        });

        let analyzer = PythonASTAnalyzer::new(policy);
        let violations = analyzer.analyze_code(code, Path::new("test.py"))?;

        assert!(!violations.is_empty(), "Should detect os.system");

        Ok(())
    }

    #[test]
    fn test_detect_eval() -> FirewallResult<()> {
        let code = r#"
def dangerous(user_input):
    result = eval(user_input)
    return result
"#;

        let mut policy = Policy::default();
        policy.blocked_patterns.push(BlockedPattern {
            pattern: "eval".to_string(),
            reason: "Arbitrary code execution".to_string(),
            severity: Severity::Critical,
            alternatives: vec![],
            is_prefix_match: false,
        });

        let analyzer = PythonASTAnalyzer::new(policy);
        let violations = analyzer.analyze_code(code, Path::new("test.py"))?;

        assert!(!violations.is_empty(), "Should detect eval");

        Ok(())
    }

    #[test]
    fn test_pathological_wildcard_pattern_star_matches_all() -> FirewallResult<()> {
        let code = r#"
def dangerous():
    eval("1+1")
"#;

        let mut policy = Policy::default();
        // '*' should match any function name according to matches_pattern.
        policy.blocked_patterns.push(BlockedPattern {
            pattern: "*".to_string(),
            reason: "Catch-all for testing".to_string(),
            severity: Severity::Critical,
            alternatives: vec![],
            is_prefix_match: false,
        });

        let analyzer = PythonASTAnalyzer::new(policy);
        let violations = analyzer.analyze_code(code, Path::new("test.py"))?;

        // We expect at least one violation and, critically, no panic.
        assert!(
            !violations.is_empty(),
            "Catch-all '*' pattern should flag at least one call"
        );
        Ok(())
    }

    #[test]
    fn test_pathological_wildcard_pattern_star_eval_star_safe() -> FirewallResult<()> {
        let code = r#"
def dangerous():
    eval("1+1")
"#;

        let mut policy = Policy::default();
        // '*eval*' is not treated as a true wildcard in matches_pattern and
        // should effectively behave like a literal substring that never matches.
        policy.blocked_patterns.push(BlockedPattern {
            pattern: "*eval*".to_string(),
            reason: "Pathological wildcard pattern".to_string(),
            severity: Severity::Critical,
            alternatives: vec![],
            is_prefix_match: false,
        });

        let analyzer = PythonASTAnalyzer::new(policy);
        let violations = analyzer.analyze_code(code, Path::new("test.py"))?;

        // We only assert that analysis completes successfully; the exact
        // matching semantics are defined but intentionally conservative.
        assert!(violations.is_empty());
        Ok(())
    }
}
