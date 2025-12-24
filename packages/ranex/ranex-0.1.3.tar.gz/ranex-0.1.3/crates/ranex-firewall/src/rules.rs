//! Firewall rules engine for dependency management.
//!
//! Uses ranex_core::FirewallError for error handling.

use ranex_core::{FirewallError, FirewallResult};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::path::Path;
use tracing::debug;

/// A firewall rule defining allowed or blocked dependencies.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FirewallRule {
    /// Rule name for identification
    pub name: String,

    /// Whether this rule allows or blocks
    pub action: RuleAction,

    /// Package patterns to match
    pub patterns: Vec<String>,

    /// Optional reason for this rule
    pub reason: Option<String>,

    /// Rule priority (higher = checked first)
    pub priority: i32,
}

/// Action to take when a rule matches.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RuleAction {
    Allow,
    Block,
    Warn,
}

/// The firewall rules engine.
#[derive(Debug, Clone, Default)]
pub struct RulesEngine {
    allowed: HashSet<String>,
    blocked: HashSet<String>,
    warned: HashSet<String>,
    rules: Vec<FirewallRule>,
    default_allow: bool,
}

impl RulesEngine {
    /// Create a new rules engine.
    pub fn new() -> Self {
        Self {
            default_allow: true,
            ..Default::default()
        }
    }

    /// Create a strict rules engine that blocks unlisted packages.
    pub fn strict() -> Self {
        Self {
            default_allow: false,
            ..Default::default()
        }
    }

    /// Add an allowed package.
    pub fn allow(&mut self, package: impl Into<String>) -> &mut Self {
        self.allowed.insert(package.into());
        self
    }

    /// Add multiple allowed packages.
    pub fn allow_all(
        &mut self,
        packages: impl IntoIterator<Item = impl Into<String>>,
    ) -> &mut Self {
        for pkg in packages {
            self.allowed.insert(pkg.into());
        }
        self
    }

    /// Add a blocked package.
    pub fn block(&mut self, package: impl Into<String>) -> &mut Self {
        self.blocked.insert(package.into());
        self
    }

    /// Add multiple blocked packages.
    pub fn block_all(
        &mut self,
        packages: impl IntoIterator<Item = impl Into<String>>,
    ) -> &mut Self {
        for pkg in packages {
            self.blocked.insert(pkg.into());
        }
        self
    }

    /// Add a warned package.
    pub fn warn(&mut self, package: impl Into<String>) -> &mut Self {
        self.warned.insert(package.into());
        self
    }

    /// Add a custom rule.
    pub fn add_rule(&mut self, rule: FirewallRule) -> &mut Self {
        self.rules.push(rule);
        self.rules.sort_by(|a, b| b.priority.cmp(&a.priority));
        self
    }

    /// Set whether to allow unlisted packages by default.
    pub fn set_default_allow(&mut self, allow: bool) -> &mut Self {
        self.default_allow = allow;
        self
    }

    /// Check if a package is allowed.
    pub fn check(&self, package: &str) -> RuleCheckResult {
        let base_package = Self::extract_base_package(package);

        // Check explicit blocklist first
        if self.blocked.contains(&base_package) || self.blocked.contains(package) {
            return RuleCheckResult::Blocked {
                reason: Some("Package is blocklisted".to_string()),
            };
        }

        // Check custom rules
        for rule in &self.rules {
            if self.matches_rule(package, rule) {
                match rule.action {
                    RuleAction::Block => {
                        return RuleCheckResult::Blocked {
                            reason: rule.reason.clone(),
                        };
                    }
                    RuleAction::Allow => {
                        return RuleCheckResult::Allowed;
                    }
                    RuleAction::Warn => {
                        return RuleCheckResult::Warned {
                            reason: rule.reason.clone(),
                        };
                    }
                }
            }
        }

        // Check explicit allowlist
        if self.allowed.contains(&base_package) || self.allowed.contains(package) {
            return RuleCheckResult::Allowed;
        }

        // Check warning list
        if self.warned.contains(&base_package) || self.warned.contains(package) {
            return RuleCheckResult::Warned {
                reason: Some("Package is on warning list".to_string()),
            };
        }

        // Default action
        if self.default_allow {
            RuleCheckResult::Allowed
        } else {
            RuleCheckResult::Blocked {
                reason: Some("Package not in allowlist".to_string()),
            }
        }
    }

    fn matches_rule(&self, package: &str, rule: &FirewallRule) -> bool {
        for pattern in &rule.patterns {
            if Self::matches_pattern(package, pattern) {
                return true;
            }
        }
        false
    }

    fn matches_pattern(package: &str, pattern: &str) -> bool {
        if let Some(prefix) = pattern.strip_suffix('*') {
            package.starts_with(prefix)
        } else {
            package == pattern || package.starts_with(&format!("{}.", pattern))
        }
    }

    fn extract_base_package(package: &str) -> String {
        package.split('.').next().unwrap_or(package).to_string()
    }

    /// Load rules from a file.
    /// Returns FirewallError::RulesNotFound if file doesn't exist.
    /// Returns FirewallError::InvalidRule for parse errors.
    pub fn load_from_file(path: &Path) -> FirewallResult<Self> {
        if !path.exists() {
            return Err(FirewallError::RulesNotFound {
                path: path.display().to_string(),
            });
        }

        let content = std::fs::read_to_string(path)?;
        Self::parse_rules_file(&content, path)
    }

    /// Parse a rules file (simple line-based format).
    fn parse_rules_file(content: &str, path: &Path) -> FirewallResult<Self> {
        let mut engine = Self::new();

        for (line_num, line) in content.lines().enumerate() {
            let line = line.trim();

            if line.is_empty() || line.starts_with('#') {
                continue;
            }

            let parts: Vec<&str> = line.splitn(2, ' ').collect();
            let (action, package) = match parts.as_slice() {
                [action, package] => (action.to_lowercase(), package.trim()),
                _ => {
                    return Err(FirewallError::InvalidRule {
                        name: format!("line_{}", line_num + 1),
                        reason: format!("Invalid rule format: {}", line),
                    })
                }
            };

            match action.as_str() {
                "allow" => {
                    engine.allow(package);
                }
                "block" => {
                    engine.block(package);
                }
                "warn" => {
                    engine.warn(package);
                }
                _ => {
                    return Err(FirewallError::InvalidRule {
                        name: format!("line_{}", line_num + 1),
                        reason: format!(
                            "Unknown action '{}': must be allow, block, or warn",
                            action
                        ),
                    });
                }
            }
        }

        debug!(
            path = %path.display(),
            allowed = engine.allowed.len(),
            blocked = engine.blocked.len(),
            "Rules loaded"
        );

        Ok(engine)
    }

    pub fn allowed_count(&self) -> usize {
        self.allowed.len()
    }

    pub fn blocked_count(&self) -> usize {
        self.blocked.len()
    }
}

/// Result of checking a package against rules.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RuleCheckResult {
    Allowed,
    Blocked { reason: Option<String> },
    Warned { reason: Option<String> },
}

impl RuleCheckResult {
    pub fn is_allowed(&self) -> bool {
        matches!(self, Self::Allowed | Self::Warned { .. })
    }

    pub fn is_blocked(&self) -> bool {
        matches!(self, Self::Blocked { .. })
    }

    pub fn is_warned(&self) -> bool {
        matches!(self, Self::Warned { .. })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_allow_block() {
        let mut engine = RulesEngine::new();
        engine.allow("requests");
        engine.block("evil_package");

        assert!(engine.check("requests").is_allowed());
        assert!(engine.check("evil_package").is_blocked());
        assert!(engine.check("unknown").is_allowed()); // default_allow = true
    }

    #[test]
    fn test_strict_mode() {
        let mut engine = RulesEngine::strict();
        engine.allow("requests");

        assert!(engine.check("requests").is_allowed());
        assert!(engine.check("unknown").is_blocked());
    }

    #[test]
    fn test_submodule_matching() {
        let mut engine = RulesEngine::new();
        engine.allow("requests");
        engine.block("os");

        assert!(engine.check("requests.auth").is_allowed());
        assert!(engine.check("os.path").is_blocked());
    }

    #[test]
    fn test_parse_rules_file() -> FirewallResult<()> {
        let content = r#"
# Allowed packages
allow requests
allow fastapi

# Blocked packages
block os
block subprocess
"#;
        use std::io::Write;
        use tempfile::NamedTempFile;

        let mut file = NamedTempFile::new()?;
        file.write_all(content.as_bytes())?;
        file.flush()?;

        let engine = RulesEngine::load_from_file(file.path())?;
        assert!(engine.check("requests").is_allowed());
        assert!(engine.check("fastapi").is_allowed());
        assert!(engine.check("os").is_blocked());
        assert!(engine.check("subprocess").is_blocked());

        Ok(())
    }

    #[test]
    fn test_wildcard_patterns() {
        let mut engine = RulesEngine::new();
        engine.add_rule(FirewallRule {
            name: "block_private".to_string(),
            action: RuleAction::Block,
            patterns: vec!["_internal*".to_string()],
            reason: Some("Private packages blocked".to_string()),
            priority: 100,
        });

        assert!(engine.check("_internal").is_blocked());
        assert!(engine.check("_internal_stuff").is_blocked());
        assert!(engine.check("public").is_allowed());
    }
}
