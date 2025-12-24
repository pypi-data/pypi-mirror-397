//! Ranex Firewall - Dependency validation and security.
//!
//! This crate uses ranex_core error types:
//! - `FirewallError` - All firewall-specific errors
//! - `FirewallResult` - Result<T, FirewallError>
//!
//! # Usage
//!
//! ```rust,ignore
//! use ranex_firewall::{FirewallAnalyzer, AnalyzerConfig, RulesEngine};
//!
//! let mut rules = RulesEngine::new();
//! rules.block("malicious_package");
//!
//! let config = AnalyzerConfig {
//!     rules,
//!     ..Default::default()
//! };
//!
//! let analyzer = FirewallAnalyzer::new(config);
//! let report = analyzer.analyze_file(Path::new("app.py"))?;
//! ```

mod analyzer;
mod atlas;
mod audit;
mod bktree;
mod circuit;
mod policy;
mod python_ast_analyzer;
mod python_imports;
mod report;
mod rules;
mod trie;
mod typosquat;
mod validator;

pub use analyzer::{AnalyzerConfig, FirewallAnalyzer};
pub use atlas::AtlasClient;
pub use audit::{AuditEvent, AuditEventType, AuditRingBuffer};
pub use bktree::BKTree;
pub use circuit::{CircuitBreaker, CircuitBreakerError, CircuitState};
pub use policy::{AtlasConfig, BlockedPattern, Policy, PolicyMode, Severity, TypoDetectionConfig};
pub use python_ast_analyzer::{DangerousFunctionCall, PythonASTAnalyzer};
pub use python_imports::{parse_imports, parse_imports_from_file, PythonImport};
pub use report::{
    FirewallReport, ReportStats, Violation, ViolationBuilder, ViolationKind, Warning, WarningKind,
};
pub use rules::{FirewallRule, RuleAction, RuleCheckResult, RulesEngine};
pub use trie::PatternTrie;
pub use typosquat::{
    check_typosquat, levenshtein_distance, normalized_levenshtein, TyposquatMatch,
};
pub use validator::{TieredValidator, ValidationResult};

// Re-export ranex_core types for convenience
pub use ranex_core::config::FirewallConfig;
pub use ranex_core::{FirewallError, FirewallResult};
