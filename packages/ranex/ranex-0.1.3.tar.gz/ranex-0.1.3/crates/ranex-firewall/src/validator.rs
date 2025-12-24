//! Tiered validation engine.
//!
//! Implements fast-path-first validation:
//! - Tier 1: O(1) stdlib lookup
//! - Tier 2: O(1) allowed packages lookup
//! - Tier 3: O(k) blocked pattern trie
//! - Tier 4: O(log n) Atlas (external)
//! - Tier 5: O(log n) BK-tree typosquatting

use crate::atlas::AtlasClient;
use crate::bktree::BKTree;
use crate::policy::Policy;
use crate::trie::PatternTrie;
use parking_lot::Mutex;
use ranex_core::{FirewallError, FirewallResult};
use std::collections::HashSet;
use std::sync::Arc;

/// Validation result from tiered validator
#[derive(Debug, Clone)]
pub enum ValidationResult {
    /// Package is allowed (Tier 1-2 hit or Tier 4 pass)
    Allowed,
    /// Package is blocked by pattern or policy
    Blocked(FirewallError),
    /// Possible typosquatting detected
    Typosquat { intended: String, distance: usize },
    /// Unknown package - not in any list
    Unknown,
}

/// Main tiered validator
pub struct TieredValidator {
    /// Tier 1: O(1) stdlib lookup
    stdlib_set: HashSet<String>,

    /// Tier 2: O(1) allowed packages lookup
    allowed_set: HashSet<String>,

    /// Tier 3: O(k) blocked patterns
    blocked_trie: PatternTrie,

    /// Tier 4: Optional Atlas client for internal imports
    atlas: Option<Arc<Mutex<AtlasClient>>>,

    /// Tier 5: O(log n) typosquatting detection
    typosquat_tree: BKTree,

    /// Internal import prefixes (e.g., ["app.", "src."])
    internal_prefixes: Vec<String>,

    /// Maximum edit distance for typosquatting
    max_edit_distance: usize,

    /// Typosquatting detection enabled
    typo_detection_enabled: bool,
}

impl TieredValidator {
    /// Create validator from policy
    pub fn from_policy(policy: &Policy) -> FirewallResult<Self> {
        let stdlib_set = Self::load_stdlib_modules();
        let allowed_set = policy.allowed_packages_set();
        let blocked_trie = PatternTrie::from_patterns(&policy.blocked_patterns);
        let mut allowed_packages: Vec<String> = allowed_set
            .iter()
            .map(std::clone::Clone::clone)
            .collect();
        allowed_packages.sort();

        let mut typosquat_tree = BKTree::from_packages(&allowed_packages);
        for known in &policy.typo_detection.known_typos {
            for typo in &known.typos {
                typosquat_tree.insert_with_intended(typo, &known.actual);
            }
        }

        Ok(Self {
            stdlib_set,
            allowed_set,
            blocked_trie,
            atlas: None,
            typosquat_tree,
            internal_prefixes: policy.internal_prefixes.clone(),
            max_edit_distance: policy.typo_detection.max_edit_distance,
            typo_detection_enabled: policy.typo_detection.enabled,
        })
    }

    /// Create validator with Atlas support for internal import validation
    ///
    /// # Arguments
    ///
    /// * `policy` - Firewall policy configuration
    /// * `atlas_db_path` - Path to Atlas SQLite database
    ///
    /// # Example
    ///
    /// ```rust,ignore
    /// let validator = TieredValidator::with_atlas(&policy, ".ranex/atlas.sqlite")?;
    /// ```
    pub fn with_atlas(policy: &Policy, atlas_db_path: &str) -> FirewallResult<Self> {
        let mut validator = Self::from_policy(policy)?;
        let mut atlas_config = policy.atlas.clone();
        // Allow caller to override db_path explicitly while still honoring
        // other AtlasConfig fields (TTL, fail_open, enabled).
        atlas_config.db_path = atlas_db_path.to_string();
        let atlas_client = AtlasClient::from_config(&atlas_config)?;
        validator.atlas = Some(Arc::new(Mutex::new(atlas_client)));
        Ok(validator)
    }

    /// Main validation entry point
    #[inline]
    pub fn validate(&self, module_name: &str) -> FirewallResult<ValidationResult> {
        // TIER 1: O(k) - Blocked pattern check (DENY takes precedence)
        if let Some(pattern) = self.blocked_trie.find_match(module_name) {
            return Ok(ValidationResult::Blocked(FirewallError::BlockedPattern {
                package: module_name.to_string(),
                pattern: pattern.pattern.clone(),
                reason: pattern.reason.clone(),
            }));
        }

        // TIER 2: O(1) - Stdlib check
        if self.stdlib_set.contains(module_name) {
            return Ok(ValidationResult::Allowed);
        }

        // Extract top-level package
        let top_level = Self::extract_top_level(module_name);

        // TIER 3: O(1) - Allowed package check
        if self.allowed_set.contains(top_level) {
            return Ok(ValidationResult::Allowed);
        }

        // TIER 4: Internal import - check Atlas if configured
        if self.is_internal(module_name) {
            return self.validate_internal(module_name);
        }

        // TIER 5: O(log n) - Typosquatting check
        if self.typo_detection_enabled
            && let Some((intended, distance)) = self
                .typosquat_tree
                .find_similar(top_level, self.max_edit_distance)
        {
            return Ok(ValidationResult::Typosquat { intended, distance });
        }

        // Unknown package
        Ok(ValidationResult::Unknown)
    }

    /// Check if module is internal (app.*, src.*)
    #[inline]
    fn is_internal(&self, module_name: &str) -> bool {
        self.internal_prefixes
            .iter()
            .any(|p| module_name.starts_with(p))
    }

    /// Validate internal import via Atlas (Tier 4)
    fn validate_internal(&self, module_name: &str) -> FirewallResult<ValidationResult> {
        let Some(atlas) = &self.atlas else {
            // No Atlas configured - return Unknown
            // Caller can decide whether to allow or block
            return Ok(ValidationResult::Unknown);
        };

        let mut atlas = atlas.lock();

        match atlas.check_exists(module_name) {
            Ok(true) => Ok(ValidationResult::Allowed),
            Ok(false) => {
                // Module not found in codebase - get suggestions
                let suggestions = atlas.find_similar(module_name, 5).unwrap_or_default();

                Ok(ValidationResult::Blocked(FirewallError::InternalNotFound {
                    module: module_name.to_string(),
                    suggestions,
                }))
            }
            Err(e) => {
                // Respect Atlas fail_open configuration: if fail_open is false,
                // propagate the error so callers can treat this as a hard failure.
                tracing::warn!("Atlas validation failed for {}: {}", module_name, e);
                Err(e)
            }
        }
    }

    /// Extract top-level package name
    #[inline]
    fn extract_top_level(module_name: &str) -> &str {
        module_name.split('.').next().unwrap_or(module_name)
    }

    /// Load stdlib module names from embedded file
    fn load_stdlib_modules() -> HashSet<String> {
        include_str!("stdlib_modules.txt")
            .lines()
            .filter(|s| !s.is_empty() && !s.starts_with('#'))
            .map(|s| s.trim().to_string())
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;

    fn test_policy() -> Policy {
        Policy::default_test_policy()
    }

    #[test]
    fn test_stdlib_allowed() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;
        let result = validator.validate("os")?;
        assert!(matches!(result, ValidationResult::Allowed));
        Ok(())
    }

    #[test]
    fn test_allowed_package() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;
        let result = validator.validate("requests")?;
        assert!(matches!(result, ValidationResult::Allowed));
        Ok(())
    }

    #[test]
    fn test_blocked_pattern() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;
        let result = validator.validate("os.system")?;
        assert!(matches!(result, ValidationResult::Blocked(_)));
        Ok(())
    }

    #[test]
    fn test_unknown_package() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;
        let result = validator.validate("nonexistent_package")?;
        assert!(matches!(result, ValidationResult::Unknown | ValidationResult::Typosquat { .. }));
        Ok(())
    }

    #[test]
    fn test_internal_prefix() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;
        let result = validator.validate("app.utils.helper")?;
        assert!(matches!(result, ValidationResult::Unknown));
        Ok(())
    }

    #[test]
    fn test_very_long_module_name_does_not_panic() -> Result<(), Box<dyn Error>> {
        let validator = TieredValidator::from_policy(&test_policy())?;

        // Construct a very long but syntactically plausible module path.
        let long_suffix = "submodule".repeat(200); // ~1.6k chars
        let long_module = format!("requests.{}", long_suffix);

        let result = validator.validate(&long_module)?;
        // We only assert that validation completes and returns a well-formed result.
        assert!(matches!(
            result,
            ValidationResult::Allowed
                | ValidationResult::Blocked(_)
                | ValidationResult::Typosquat { .. }
                | ValidationResult::Unknown
        ));
        Ok(())
    }

    #[test]
    fn test_unicode_package_name_in_allowed_list() -> Result<(), Box<dyn Error>> {
        let mut policy = test_policy();
        policy.allowed_packages.push("unicodé".to_string());

        let validator = TieredValidator::from_policy(&policy)?;
        let result = validator.validate("unicodé")?;
        assert!(matches!(result, ValidationResult::Allowed));
        Ok(())
    }

    #[test]
    fn test_extract_top_level() {
        assert_eq!(TieredValidator::extract_top_level("requests"), "requests");
        assert_eq!(
            TieredValidator::extract_top_level("stripe.api.v2"),
            "stripe"
        );
        assert_eq!(TieredValidator::extract_top_level(""), "");
    }
}
