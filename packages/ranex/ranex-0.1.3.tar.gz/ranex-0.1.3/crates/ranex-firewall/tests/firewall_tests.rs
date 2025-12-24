//! Integration tests for ranex-firewall

use ranex_firewall::{Policy, PolicyMode, TieredValidator, ValidationResult};
use std::io::{self, Write};
use tempfile::NamedTempFile;

#[test]
fn test_full_validation_flow() -> Result<(), Box<dyn std::error::Error>> {
    // Create test policy
    let mut file = NamedTempFile::new()?;
    writeln!(
        file,
        r#"
version: "1.0"
mode: strict
allowed_packages:
  - requests
  - flask
  - stripe
blocked_patterns:
  - pattern: "os.system"
    reason: "Command injection"
    severity: Critical
typo_detection:
  enabled: true
  max_edit_distance: 2
internal_prefixes:
  - "app."
"#
    )
    ?;

    let policy = Policy::load(file.path())?;
    let validator = TieredValidator::from_policy(&policy)?;

    // Test stdlib (Tier 1)
    assert!(matches!(
        validator.validate("json")?,
        ValidationResult::Allowed
    ));

    // Test allowed (Tier 2)
    assert!(matches!(
        validator.validate("requests")?,
        ValidationResult::Allowed
    ));

    // Test blocked (Tier 3)
    assert!(matches!(
        validator.validate("os.system")?,
        ValidationResult::Blocked(_)
    ));

    // Test internal (Tier 4 - returns Unknown for Atlas)
    assert!(matches!(
        validator.validate("app.utils")?,
        ValidationResult::Unknown
    ));

    // Test typosquatting (Tier 5)
    let result = validator.validate("reqeusts")?;
    if let ValidationResult::Typosquat { intended, distance } = result {
        assert_eq!(intended, "requests");
        assert!(distance <= 2);
        Ok(())
    } else {
        Err(io::Error::other(format!("Expected Typosquat, got {:?}", result)).into())
    }
}

#[test]
fn test_audit_mode() -> Result<(), Box<dyn std::error::Error>> {
    let mut file = NamedTempFile::new()?;
    writeln!(
        file,
        r#"
version: "1.0"
mode: audit_only
allowed_packages: []
"#
    )
    ?;

    let policy = Policy::load(file.path())?;
    assert_eq!(policy.mode, PolicyMode::AuditOnly);
    Ok(())
}
