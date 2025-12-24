//! # PyFirewall
//!
//! Python bindings for the Ranex Dependency Firewall.
//!
//! ## Usage from Python
//!
//! ```python
//! from ranex_rust import Firewall
//!
//! # Initialize firewall for a project
//! firewall = Firewall("/path/to/project")
//!
//! # Check if an import is allowed
//! result = firewall.check_import("requests")
//! print(f"Allowed: {result['allowed']}")
//!
//! # Analyze a file
//! report = firewall.analyze_file("app.py")
//! print(f"Violations: {report['violations']}")
//! ```

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use ranex_firewall::{check_typosquat, parse_imports, Policy, TieredValidator, ValidationResult};
use std::path::PathBuf;
use tracing::{debug, info, warn};

/// Python-compatible error type for Firewall operations.
#[derive(Debug)]
pub struct PyFirewallError {
    message: String,
}

impl PyFirewallError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl From<PyFirewallError> for PyErr {
    fn from(err: PyFirewallError) -> PyErr {
        pyo3::exceptions::PyRuntimeError::new_err(err.message)
    }
}

impl From<ranex_core::FirewallError> for PyFirewallError {
    fn from(err: ranex_core::FirewallError) -> Self {
        Self::new(err.to_string())
    }
}

/// Firewall - Python interface to the Ranex Dependency Firewall.
///
/// Validates imports against security policies, detects typosquatting,
/// and enforces dependency rules.
///
/// # Example
///
/// ```python
/// firewall = Firewall("/path/to/project")
/// result = firewall.check_import("os.system")  # Returns blocked
/// ```
#[pyclass(name = "Firewall", unsendable)]
pub struct PyFirewall {
    project_root: PathBuf,
    policy: Policy,
    validator: TieredValidator,
}

#[pymethods]
impl PyFirewall {
    /// Create a new Firewall instance for a project.
    ///
    /// Args:
    ///     project_root: Path to the project root directory.
    ///
    /// Returns:
    ///     Firewall instance ready for validation.
    ///
    /// Raises:
    ///     RuntimeError: If policy loading fails.
    #[new]
    #[pyo3(signature = (project_root))]
    fn new(project_root: String) -> PyResult<Self> {
        let path = PathBuf::from(&project_root);

        // Load policy from project or use production defaults
        let policy_path = path.join(".ranex").join("firewall.yaml");
        let policy = Policy::load(&policy_path).unwrap_or_else(|e| {
            warn!(
                "No firewall policy found at {}: {}, using production defaults",
                policy_path.display(),
                e
            );
            Policy::production_policy()
        });

        let validator = TieredValidator::from_policy(&policy)
            .map_err(|e| PyFirewallError::new(e.to_string()))?;

        info!(project = %project_root, "Firewall initialized");

        Ok(Self {
            project_root: path,
            policy,
            validator,
        })
    }

    /// Check if a single import is allowed.
    ///
    /// Args:
    ///     import_path: Import path to check (e.g., "requests", "os.system").
    ///
    /// Returns:
    ///     dict: Validation result containing:
    ///         - allowed: bool - Whether the import is allowed
    ///         - status: str - Status (allowed, blocked, typosquat, unknown)
    ///         - reason: str - Explanation for the decision
    ///         - suggestion: str - Alternative suggestion if blocked
    ///
    /// Raises:
    ///     RuntimeError: If validation fails.
    #[pyo3(signature = (import_path))]
    fn check_import(&self, py: Python<'_>, import_path: String) -> PyResult<Py<PyAny>> {
        let result = self
            .validator
            .validate(&import_path)
            .map_err(|e| PyFirewallError::new(e.to_string()))?;

        let dict = PyDict::new(py);

        match &result {
            ValidationResult::Allowed => {
                dict.set_item("allowed", true)?;
                dict.set_item("status", "allowed")?;
                dict.set_item("reason", "Import is allowed")?;
                dict.set_item("suggestion", "")?;
            }
            ValidationResult::Blocked(err) => {
                dict.set_item("allowed", false)?;
                dict.set_item("status", "blocked")?;
                dict.set_item("reason", err.to_string())?;
                dict.set_item("suggestion", "")?;
            }
            ValidationResult::Typosquat { intended, distance } => {
                dict.set_item("allowed", false)?;
                dict.set_item("status", "typosquat")?;
                dict.set_item(
                    "reason",
                    format!(
                        "Possible typosquat of '{}' (distance: {})",
                        intended, distance
                    ),
                )?;
                dict.set_item("suggestion", intended)?;
            }
            ValidationResult::Unknown => {
                dict.set_item("allowed", false)?;
                dict.set_item("status", "unknown")?;
                dict.set_item("reason", "Unknown package - not in allowed list")?;
                dict.set_item("suggestion", "")?;
            }
        }

        debug!(import = %import_path, allowed = matches!(result, ValidationResult::Allowed), "Import checked");

        Ok(dict.into())
    }

    /// Check multiple imports at once.
    ///
    /// Args:
    ///     imports: List of import paths to check.
    ///
    /// Returns:
    ///     list[dict]: List of validation results.
    #[pyo3(signature = (imports))]
    fn check_imports(&self, py: Python<'_>, imports: Vec<String>) -> PyResult<Py<PyAny>> {
        let list = PyList::empty(py);

        for import_path in imports {
            let result = self
                .validator
                .validate(&import_path)
                .map_err(|e| PyFirewallError::new(e.to_string()))?;

            let dict = PyDict::new(py);
            dict.set_item("import", &import_path)?;

            match &result {
                ValidationResult::Allowed => {
                    dict.set_item("allowed", true)?;
                    dict.set_item("status", "allowed")?;
                    dict.set_item("reason", "Import is allowed")?;
                }
                ValidationResult::Blocked(err) => {
                    dict.set_item("allowed", false)?;
                    dict.set_item("status", "blocked")?;
                    dict.set_item("reason", err.to_string())?;
                }
                ValidationResult::Typosquat {
                    intended,
                    distance: _,
                } => {
                    dict.set_item("allowed", false)?;
                    dict.set_item("status", "typosquat")?;
                    dict.set_item("reason", format!("Possible typosquat of '{}'", intended))?;
                }
                ValidationResult::Unknown => {
                    dict.set_item("allowed", false)?;
                    dict.set_item("status", "unknown")?;
                    dict.set_item("reason", "Unknown package")?;
                }
            }

            list.append(dict)?;
        }

        Ok(list.into())
    }

    /// Analyze a Python file for import violations.
    ///
    /// Args:
    ///     file_path: Path to the Python file to analyze.
    ///
    /// Returns:
    ///     dict: Analysis report containing:
    ///         - file_path: str - The analyzed file
    ///         - imports_found: int - Number of imports found
    ///         - violations: list[dict] - List of violations
    ///         - passed: bool - Whether the file passed validation
    ///
    /// Raises:
    ///     RuntimeError: If file parsing fails.
    #[pyo3(signature = (file_path))]
    fn analyze_file(&self, py: Python<'_>, file_path: String) -> PyResult<Py<PyAny>> {
        let path = PathBuf::from(&file_path);

        // Parse imports from file
        let imports = parse_imports_from_file(&path)
            .map_err(|e| PyFirewallError::new(format!("Failed to parse file: {}", e)))?;

        let dict = PyDict::new(py);
        dict.set_item("file_path", &file_path)?;
        dict.set_item("imports_found", imports.len())?;

        let violations = PyList::empty(py);
        let mut passed = true;

        for import in &imports {
            let result = self
                .validator
                .validate(&import.module)
                .map_err(|e| PyFirewallError::new(e.to_string()))?;

            match &result {
                ValidationResult::Allowed => {
                    // OK, no violation
                }
                ValidationResult::Blocked(err) => {
                    passed = false;
                    let v = PyDict::new(py);
                    v.set_item("import", &import.module)?;
                    v.set_item("line", import.line)?;
                    v.set_item("status", "blocked")?;
                    v.set_item("reason", err.to_string())?;
                    violations.append(v)?;
                }
                ValidationResult::Typosquat { intended, distance } => {
                    passed = false;
                    let v = PyDict::new(py);
                    v.set_item("import", &import.module)?;
                    v.set_item("line", import.line)?;
                    v.set_item("status", "typosquat")?;
                    v.set_item(
                        "reason",
                        format!(
                            "Possible typosquat of '{}' (distance: {})",
                            intended, distance
                        ),
                    )?;
                    v.set_item("suggestion", intended)?;
                    violations.append(v)?;
                }
                ValidationResult::Unknown => {
                    passed = false;
                    let v = PyDict::new(py);
                    v.set_item("import", &import.module)?;
                    v.set_item("line", import.line)?;
                    v.set_item("status", "unknown")?;
                    v.set_item("reason", "Unknown package - not in allowed list")?;
                    violations.append(v)?;
                }
            }
        }

        let violations_count = violations.len();
        dict.set_item("violations", violations)?;
        dict.set_item("passed", passed)?;

        info!(file = %file_path, violations = violations_count, "File analyzed");

        Ok(dict.into())
    }

    /// Check for typosquatting (misspelled package names).
    ///
    /// Args:
    ///     package_name: Package name to check.
    ///
    /// Returns:
    ///     dict: Typosquat check result containing:
    ///         - is_typosquat: bool - Whether this looks like a typo
    ///         - intended_package: str - What package was probably intended
    ///         - distance: int - Edit distance
    #[pyo3(signature = (package_name))]
    fn check_typosquat(&self, py: Python<'_>, package_name: String) -> PyResult<Py<PyAny>> {
        // Use threshold of 0.8 (80% similar)
        let result = check_typosquat(&package_name, 0.8);

        let dict = PyDict::new(py);

        if let Some(typo_match) = result {
            dict.set_item("is_typosquat", true)?;
            dict.set_item("intended_package", &typo_match.similar_to)?;
            dict.set_item("similarity", typo_match.similarity)?;
        } else {
            dict.set_item("is_typosquat", false)?;
            dict.set_item("intended_package", "")?;
            dict.set_item("similarity", 0.0)?;
        }

        Ok(dict.into())
    }

    /// Get the current policy mode.
    ///
    /// Returns:
    ///     str: Policy mode ("strict", "audit_only", or "disabled").
    #[getter]
    fn policy_mode(&self) -> &str {
        match self.policy.mode {
            ranex_firewall::PolicyMode::Strict => "strict",
            ranex_firewall::PolicyMode::AuditOnly => "audit_only",
            ranex_firewall::PolicyMode::Disabled => "disabled",
        }
    }

    /// Get the list of blocked patterns.
    ///
    /// Returns:
    ///     list[str]: List of blocked import patterns.
    #[pyo3(signature = ())]
    fn get_blocked_patterns(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let list = PyList::empty(py);
        for pattern in &self.policy.blocked_patterns {
            let dict = PyDict::new(py);
            dict.set_item("pattern", &pattern.pattern)?;
            dict.set_item("reason", &pattern.reason)?;
            dict.set_item("severity", format!("{:?}", pattern.severity))?;
            list.append(dict)?;
        }
        Ok(list.into())
    }

    /// Get policy information for debugging
    #[pyo3(signature = ())]
    fn get_policy_info(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);
        dict.set_item("version", &self.policy.version)?;
        dict.set_item("mode", format!("{:?}", self.policy.mode))?;
        dict.set_item("allowed_packages_count", self.policy.allowed_packages.len())?;
        dict.set_item("blocked_patterns_count", self.policy.blocked_patterns.len())?;
        dict.set_item(
            "internal_prefixes_count",
            self.policy.internal_prefixes.len(),
        )?;
        dict.set_item("typo_detection_enabled", self.policy.typo_detection.enabled)?;
        dict.set_item("atlas_enabled", self.policy.atlas.enabled)?;

        // Show if using production defaults or loaded from file
        let policy_path = self.project_root.join(".ranex").join("firewall.yaml");
        if policy_path.exists() {
            dict.set_item("config_source", "file")?;
            dict.set_item("config_path", policy_path.to_string_lossy())?;
        } else {
            dict.set_item("config_source", "production_defaults")?;
            dict.set_item("config_path", "")?;
        }

        Ok(dict.into())
    }

    /// List all firewall rules and policies.
    ///
    /// Returns:
    ///     dict: Complete firewall configuration including:
    ///         - allowed_packages: list[str] - Explicitly allowed packages
    ///         - blocked_patterns: list[dict] - Blocked patterns with reasons
    ///         - internal_prefixes: list[str] - Internal module prefixes
    ///         - policy_mode: str - Current policy mode
    ///         - config_source: str - Where config was loaded from
    #[pyo3(signature = ())]
    fn list_rules(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);

        // Allowed packages
        let allowed = PyList::empty(py);
        for package in &self.policy.allowed_packages {
            allowed.append(package)?;
        }
        dict.set_item("allowed_packages", allowed)?;

        // Blocked patterns (with details)
        let blocked = PyList::empty(py);
        for pattern in &self.policy.blocked_patterns {
            let pattern_dict = PyDict::new(py);
            pattern_dict.set_item("pattern", &pattern.pattern)?;
            pattern_dict.set_item("reason", &pattern.reason)?;
            pattern_dict.set_item("severity", format!("{:?}", pattern.severity))?;
            blocked.append(pattern_dict)?;
        }
        dict.set_item("blocked_patterns", blocked)?;

        // Internal prefixes
        let internal = PyList::empty(py);
        for prefix in &self.policy.internal_prefixes {
            internal.append(prefix)?;
        }
        dict.set_item("internal_prefixes", internal)?;

        // Policy settings
        dict.set_item("policy_mode", self.policy_mode())?;
        dict.set_item("typo_detection_enabled", self.policy.typo_detection.enabled)?;
        dict.set_item("atlas_enabled", self.policy.atlas.enabled)?;
        dict.set_item("version", &self.policy.version)?;

        // Config source info
        let policy_path = self.project_root.join(".ranex").join("firewall.yaml");
        if policy_path.exists() {
            dict.set_item("config_source", "file")?;
            dict.set_item("config_path", policy_path.to_string_lossy())?;
        } else {
            dict.set_item("config_source", "production_defaults")?;
            dict.set_item("config_path", "")?;
        }

        Ok(dict.into())
    }

    /// Get the list of allowed packages.
    ///
    /// Returns:
    ///     list[str]: List of explicitly allowed packages.
    fn get_allowed_packages(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let list = PyList::empty(py);
        for pkg in &self.policy.allowed_packages {
            list.append(pkg)?;
        }
        Ok(list.into())
    }

    /// String representation for debugging.
    fn __repr__(&self) -> String {
        format!(
            "Firewall(project_root='{}', mode='{}')",
            self.project_root.to_string_lossy(),
            self.policy_mode()
        )
    }
}

/// Helper function to parse imports from a file path.
fn parse_imports_from_file(path: &PathBuf) -> Result<Vec<ranex_firewall::PythonImport>, String> {
    let content = std::fs::read_to_string(path).map_err(|e| format!("Cannot read file: {}", e))?;
    Ok(parse_imports(&content))
}
