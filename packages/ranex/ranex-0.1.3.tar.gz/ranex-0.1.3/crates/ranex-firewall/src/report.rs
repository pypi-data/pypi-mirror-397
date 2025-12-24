//! Firewall violation report generation.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// A firewall check report.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FirewallReport {
    pub is_clean: bool,
    pub files_checked: u32,
    pub imports_checked: u32,
    pub violations: Vec<Violation>,
    pub warnings: Vec<Warning>,
    pub stats: ReportStats,
}

impl FirewallReport {
    pub fn new() -> Self {
        Self {
            is_clean: true,
            files_checked: 0,
            imports_checked: 0,
            violations: Vec::new(),
            warnings: Vec::new(),
            stats: ReportStats::default(),
        }
    }

    pub fn add_violation(&mut self, violation: Violation) {
        self.is_clean = false;
        self.violations.push(violation);
    }

    pub fn add_warning(&mut self, warning: Warning) {
        self.warnings.push(warning);
    }

    pub fn total_issues(&self) -> usize {
        self.violations.len() + self.warnings.len()
    }
}

impl Default for FirewallReport {
    fn default() -> Self {
        Self::new()
    }
}

/// A policy violation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Violation {
    pub kind: ViolationKind,
    pub file: PathBuf,
    pub line: u32,
    pub import: String,
    pub message: String,
    pub suggestion: Option<String>,
}

/// Type of violation.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ViolationKind {
    BlockedImport,
    UnlistedImport,
    Typosquat,
}

impl ViolationKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::BlockedImport => "blocked_import",
            Self::UnlistedImport => "unlisted_import",
            Self::Typosquat => "typosquat",
        }
    }
}

/// A non-blocking warning.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Warning {
    pub kind: WarningKind,
    pub file: PathBuf,
    pub line: u32,
    pub import: String,
    pub message: String,
}

/// Type of warning.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WarningKind {
    DeprecatedPackage,
    PossibleTyposquat,
    StarImport,
}

/// Summary statistics for the report.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ReportStats {
    pub blocked_imports: u32,
    pub unlisted_imports: u32,
    pub typosquats: u32,
    pub stdlib_imports: u32,
    pub third_party_imports: u32,
    pub relative_imports: u32,
}

/// Builder for creating violations.
pub struct ViolationBuilder {
    kind: ViolationKind,
    file: PathBuf,
    line: u32,
    import: String,
    message: Option<String>,
    suggestion: Option<String>,
}

impl ViolationBuilder {
    pub fn new(kind: ViolationKind) -> Self {
        Self {
            kind,
            file: PathBuf::new(),
            line: 0,
            import: String::new(),
            message: None,
            suggestion: None,
        }
    }

    pub fn file(mut self, file: impl Into<PathBuf>) -> Self {
        self.file = file.into();
        self
    }

    pub fn line(mut self, line: u32) -> Self {
        self.line = line;
        self
    }

    pub fn import(mut self, import: impl Into<String>) -> Self {
        self.import = import.into();
        self
    }

    pub fn message(mut self, message: impl Into<String>) -> Self {
        self.message = Some(message.into());
        self
    }

    pub fn suggestion(mut self, suggestion: impl Into<String>) -> Self {
        self.suggestion = Some(suggestion.into());
        self
    }

    pub fn build(self) -> Violation {
        let message = self.message.unwrap_or_else(|| match self.kind {
            ViolationKind::BlockedImport => {
                format!("Import '{}' is blocked by firewall policy", self.import)
            }
            ViolationKind::UnlistedImport => {
                format!("Import '{}' is not in the allowlist", self.import)
            }
            ViolationKind::Typosquat => {
                format!("Import '{}' may be a typosquat", self.import)
            }
        });

        Violation {
            kind: self.kind,
            file: self.file,
            line: self.line,
            import: self.import,
            message,
            suggestion: self.suggestion,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_report_creation() {
        let mut report = FirewallReport::new();
        assert!(report.is_clean);

        report.add_violation(
            ViolationBuilder::new(ViolationKind::BlockedImport)
                .file("test.py")
                .line(10)
                .import("evil_package")
                .build(),
        );

        assert!(!report.is_clean);
        assert_eq!(report.violations.len(), 1);
    }

    #[test]
    fn test_violation_builder() {
        let violation = ViolationBuilder::new(ViolationKind::BlockedImport)
            .file("app.py")
            .line(5)
            .import("subprocess")
            .message("subprocess is not allowed")
            .suggestion("Use subprocess32 instead")
            .build();

        assert_eq!(violation.kind, ViolationKind::BlockedImport);
        assert_eq!(violation.file, PathBuf::from("app.py"));
        assert_eq!(violation.line, 5);
        assert_eq!(violation.import, "subprocess");
        assert_eq!(violation.message, "subprocess is not allowed");
        assert_eq!(
            violation.suggestion,
            Some("Use subprocess32 instead".to_string())
        );
    }

    #[test]
    fn test_default_messages() {
        let blocked = ViolationBuilder::new(ViolationKind::BlockedImport)
            .file("test.py")
            .line(1)
            .import("test")
            .build();

        assert!(blocked.message.contains("blocked by firewall policy"));

        let unlisted = ViolationBuilder::new(ViolationKind::UnlistedImport)
            .file("test.py")
            .line(1)
            .import("test")
            .build();

        assert!(unlisted.message.contains("not in the allowlist"));
    }

    #[test]
    fn test_report_stats() {
        let mut report = FirewallReport::new();
        report.stats.blocked_imports = 5;
        report.stats.stdlib_imports = 10;
        report.stats.third_party_imports = 3;

        assert_eq!(report.stats.blocked_imports, 5);
        assert_eq!(report.stats.stdlib_imports, 10);
    }
}
