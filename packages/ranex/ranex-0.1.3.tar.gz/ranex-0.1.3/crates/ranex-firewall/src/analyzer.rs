//! Main firewall analysis orchestrator.
//!
//! Uses ranex_core::FirewallError and FirewallResult.

use ranex_core::{FirewallError, FirewallResult};
use std::path::Path;
use tracing::{debug, info, warn};

use crate::policy::Policy;
use crate::python_ast_analyzer::PythonASTAnalyzer;
use crate::python_imports::{parse_imports_from_file, PythonImport};
use crate::report::{FirewallReport, ViolationBuilder, ViolationKind, Warning, WarningKind};
use crate::rules::{RuleCheckResult, RulesEngine};
use crate::typosquat::check_typosquat;

/// Configuration for the firewall analyzer.
#[derive(Debug, Clone)]
pub struct AnalyzerConfig {
    pub rules: RulesEngine,
    pub check_typosquats: bool,
    pub typosquat_threshold: f64,
    pub skip_stdlib: bool,
    pub skip_relative: bool,
    pub check_usage: bool,      // NEW: Enable AST-based usage analysis
    pub policy: Option<Policy>, // NEW: Policy for usage analysis
}

impl Default for AnalyzerConfig {
    fn default() -> Self {
        Self {
            rules: RulesEngine::new(),
            check_typosquats: true,
            typosquat_threshold: 0.8,
            skip_stdlib: true,
            skip_relative: true,
            check_usage: true, // Enable usage analysis by default
            policy: Some(Policy::production_policy()), // Use production policy by default
        }
    }
}

impl AnalyzerConfig {
    /// Strict configuration derived from a given policy.
    ///
    /// Uses `RulesEngine::strict()` so that any package not explicitly
    /// allowed or covered by a rule is treated as blocked.
    pub fn strict_from_policy(policy: &Policy) -> Self {
        let mut rules = RulesEngine::strict();
        rules.allow_all(policy.allowed_packages.clone());
        for pattern in &policy.blocked_patterns {
            rules.block(&pattern.pattern);
        }

        Self {
            rules,
            check_typosquats: policy.typo_detection.enabled,
            typosquat_threshold: 0.8,
            skip_stdlib: true,
            skip_relative: true,
            check_usage: true,
            policy: Some(policy.clone()),
        }
    }
}

/// The firewall analyzer.
pub struct FirewallAnalyzer {
    config: AnalyzerConfig,
}

impl FirewallAnalyzer {
    pub fn new(config: AnalyzerConfig) -> Self {
        Self { config }
    }

    pub fn with_defaults() -> Self {
        Self::new(AnalyzerConfig::default())
    }

    /// Strict preset: deny-by-default semantics backed by the production policy.
    ///
    /// This uses a `RulesEngine::strict()` instance so that any package not on
    /// the allowlist (explicit allow or rule) is treated as blocked. It also
    /// enables typosquat and usage analysis with the production policy.
    pub fn with_strict_defaults() -> Self {
        let policy = Policy::production_policy();
        let config = AnalyzerConfig::strict_from_policy(&policy);
        Self::new(config)
    }

    /// Analyze a single file.
    /// Returns FirewallError::AnalysisError on failures.
    pub fn analyze_file(&self, path: &Path) -> FirewallResult<FirewallReport> {
        // Parse imports
        let imports = parse_imports_from_file(path).map_err(|e| FirewallError::AnalysisError {
            file: path.display().to_string(),
            reason: e.to_string(),
        })?;

        // Analyze imports
        let mut report = self.analyze_imports(path, &imports)?;

        // NEW: Perform AST-based usage analysis if enabled
        if self.config.check_usage
            && let Some(ref policy) = self.config.policy
        {
            let ast_analyzer = PythonASTAnalyzer::new(policy.clone());
            match ast_analyzer.analyze_file(path) {
                Ok(usage_violations) => {
                    // Add usage violations to the report
                    for violation in usage_violations {
                        report.add_violation(violation);
                    }
                    debug!(
                        file = %path.display(),
                        usage_violations = report.violations.len(),
                        "AST usage analysis completed"
                    );
                }
                Err(e) => {
                    warn!(
                        file = %path.display(),
                        error = %e,
                        "AST usage analysis failed, continuing with import-only analysis"
                    );
                }
            }
        }

        Ok(report)
    }

    /// Analyze a list of imports.
    pub fn analyze_imports(
        &self,
        file: &Path,
        imports: &[PythonImport],
    ) -> FirewallResult<FirewallReport> {
        let mut report = FirewallReport::new();
        report.files_checked = 1;
        report.imports_checked = imports.len() as u32;

        for import in imports {
            self.check_import(file, import, &mut report);
        }

        debug!(
            file = %file.display(),
            imports = imports.len(),
            violations = report.violations.len(),
            "File analyzed"
        );

        Ok(report)
    }

    fn check_import(&self, file: &Path, import: &PythonImport, report: &mut FirewallReport) {
        if self.config.skip_relative && import.is_relative() {
            report.stats.relative_imports += 1;
            return;
        }

        if self.config.skip_stdlib && import.is_stdlib() {
            report.stats.stdlib_imports += 1;
            return;
        }

        report.stats.third_party_imports += 1;

        // Check star imports
        if import.names.contains(&"*".to_string()) {
            report.add_warning(Warning {
                kind: WarningKind::StarImport,
                file: file.to_path_buf(),
                line: import.line,
                import: import.raw.clone(),
                message: format!(
                    "Star import from '{}' - consider importing specific names",
                    import.module
                ),
            });
        }

        // Check against rules
        let result = self.config.rules.check(&import.module);

        match result {
            RuleCheckResult::Blocked { reason } => {
                report.stats.blocked_imports += 1;
                report.add_violation(
                    ViolationBuilder::new(ViolationKind::BlockedImport)
                        .file(file)
                        .line(import.line)
                        .import(&import.module)
                        .message(reason.unwrap_or_else(|| {
                            format!("Import '{}' is blocked by firewall policy", import.module)
                        }))
                        .build(),
                );
            }
            RuleCheckResult::Warned { reason } => {
                report.add_warning(Warning {
                    kind: WarningKind::DeprecatedPackage,
                    file: file.to_path_buf(),
                    line: import.line,
                    import: import.module.clone(),
                    message: reason.unwrap_or_else(|| {
                        format!("Import '{}' is on the warning list", import.module)
                    }),
                });
            }
            RuleCheckResult::Allowed => {
                // Check for typosquatting
                if self.config.check_typosquats
                    && let Some(match_result) =
                        check_typosquat(&import.module, self.config.typosquat_threshold)
                {
                    report.stats.typosquats += 1;
                    report.add_violation(
                        ViolationBuilder::new(ViolationKind::Typosquat)
                            .file(file)
                            .line(import.line)
                            .import(&import.module)
                            .message(match_result.warning_message())
                            .suggestion(format!("Did you mean '{}'?", match_result.similar_to))
                            .build(),
                    );
                }
            }
        }
    }

    /// Analyze multiple files.
    pub fn analyze_files(&self, files: &[&Path]) -> FirewallResult<FirewallReport> {
        let mut combined_report = FirewallReport::new();

        for file in files {
            match self.analyze_file(file) {
                Ok(report) => {
                    combined_report.files_checked += 1;
                    combined_report.imports_checked += report.imports_checked;
                    combined_report.violations.extend(report.violations);
                    combined_report.warnings.extend(report.warnings);
                    combined_report.stats.blocked_imports += report.stats.blocked_imports;
                    combined_report.stats.unlisted_imports += report.stats.unlisted_imports;
                    combined_report.stats.typosquats += report.stats.typosquats;
                    combined_report.stats.stdlib_imports += report.stats.stdlib_imports;
                    combined_report.stats.third_party_imports += report.stats.third_party_imports;
                    combined_report.stats.relative_imports += report.stats.relative_imports;
                }
                Err(e) => {
                    warn!(file = %file.display(), error = %e, "Failed to analyze file");
                }
            }
        }

        combined_report.is_clean = combined_report.violations.is_empty();

        info!(
            files = combined_report.files_checked,
            violations = combined_report.violations.len(),
            warnings = combined_report.warnings.len(),
            "Analysis complete"
        );

        Ok(combined_report)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_analyze_clean_file() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let file = dir.path().join("app.py");
        fs::write(&file, "import json\nimport os")?;

        let analyzer = FirewallAnalyzer::with_defaults();
        let report = analyzer.analyze_file(&file)?;

        assert!(report.is_clean);
        Ok(())
    }

    #[test]
    fn test_detect_blocked_import() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let file = dir.path().join("app.py");
        fs::write(&file, "import evil_package")?;

        let mut config = AnalyzerConfig::default();
        config.rules.block("evil_package");

        let analyzer = FirewallAnalyzer::new(config);
        let report = analyzer.analyze_file(&file)?;

        assert!(!report.is_clean);
        assert_eq!(report.violations.len(), 1);
        let first = report
            .violations
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing violation"))?;
        assert_eq!(first.kind, ViolationKind::BlockedImport);
        Ok(())
    }

    #[test]
    fn test_detect_typosquat() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let file = dir.path().join("app.py");
        fs::write(&file, "import requets")?; // typo of 'requests'

        let analyzer = FirewallAnalyzer::with_defaults();
        let report = analyzer.analyze_file(&file)?;

        assert!(!report.is_clean);
        assert_eq!(report.stats.typosquats, 1);
        Ok(())
    }

    #[test]
    fn test_skip_stdlib() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let file = dir.path().join("app.py");
        fs::write(&file, "import os\nimport sys")?;

        let analyzer = FirewallAnalyzer::with_defaults();
        let report = analyzer.analyze_file(&file)?;

        assert_eq!(report.stats.stdlib_imports, 2);
        assert_eq!(report.stats.third_party_imports, 0);
        Ok(())
    }

    #[test]
    fn test_star_import_warning() -> Result<(), Box<dyn Error>> {
        let dir = tempdir()?;
        let file = dir.path().join("app.py");
        fs::write(&file, "from something import *")?;

        let mut rules = RulesEngine::new();
        rules.allow("something");
        let config = AnalyzerConfig {
            rules,
            skip_stdlib: false,
            ..AnalyzerConfig::default()
        };

        let analyzer = FirewallAnalyzer::new(config);
        let report = analyzer.analyze_file(&file)?;

        assert_eq!(report.warnings.len(), 1);
        let first = report
            .warnings
            .first()
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing warning"))?;
        assert_eq!(first.kind, WarningKind::StarImport);
        Ok(())
    }
}
