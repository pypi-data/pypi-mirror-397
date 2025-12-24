//! Atlas integration tests

use ranex_firewall::{AtlasClient, AtlasConfig, CircuitState, Policy, TieredValidator, ValidationResult};
use std::io;

#[test]
fn test_atlas_client_circuit_breaker() -> Result<(), Box<dyn std::error::Error>> {
    // Test with non-existent database (should trigger circuit breaker)
    let mut client = AtlasClient::new("/nonexistent/atlas.db")?;

    // Multiple failures should open circuit
    for _ in 0..5 {
        let _ = client.check_exists("app.test");
    }

    // Circuit should be open
    assert_eq!(client.circuit_state(), CircuitState::Open);
    Ok(())
}

#[test]
fn test_atlas_client_fail_closed_behavior() -> Result<(), Box<dyn std::error::Error>> {
    // When configured with fail_open = false, Atlas errors should propagate.
    // Build config in a single struct literal to avoid field reassignment
    // after Default::default().
    let config = AtlasConfig {
        db_path: "/nonexistent/atlas.db".to_string(),
        fail_open: false,
        ..AtlasConfig::default()
    };

    let mut client = AtlasClient::from_config(&config)?;

    // First few calls should eventually hit an error rather than silently
    // allowing unknown imports.
    let result = client.check_exists("app.test");
    assert!(result.is_err());
    Ok(())
}

#[test]
fn test_validator_internal_without_atlas() -> Result<(), Box<dyn std::error::Error>> {
    let policy = Policy::default_test_policy();
    let validator = TieredValidator::from_policy(&policy)?;

    // Without Atlas, internal imports return Unknown
    let result = validator.validate("app.utils.helper")?;
    if matches!(result, ValidationResult::Unknown) {
        Ok(())
    } else {
        Err(io::Error::other(format!("Expected Unknown, got {:?}", result)).into())
    }
}

#[test]
fn test_cache_functionality() -> Result<(), Box<dyn std::error::Error>> {
    let client = AtlasClient::with_ttl("/test.db", 300)?;

    // Manual cache test
    client.set_cached("app.test", true, vec![]);
    assert_eq!(client.get_cached("app.test"), Some(true));

    // Clear cache
    client.clear_cache();
    assert_eq!(client.get_cached("app.test"), None);

    Ok(())
}

#[test]
fn test_validator_with_atlas_constructor() -> Result<(), Box<dyn std::error::Error>> {
    let policy = Policy::default_test_policy();

    // Should not fail even with non-existent database (lazy init)
    let _validator = TieredValidator::with_atlas(&policy, "/nonexistent/atlas.db")?;
    Ok(())
}

#[test]
fn test_atlas_fail_open_on_error() -> Result<(), Box<dyn std::error::Error>> {
    let policy = Policy::default_test_policy();
    let validator = TieredValidator::with_atlas(&policy, "/nonexistent/atlas.db")?;

    // Internal imports should fail open when Atlas errors
    // (after circuit opens, it allows imports for availability)
    let result = validator.validate("app.nonexistent")?;
    if matches!(result, ValidationResult::Allowed | ValidationResult::Unknown) {
        Ok(())
    } else {
        Err(
            io::Error::other(format!(
                "Expected Allowed or Unknown on Atlas error, got {:?}",
                result
            ))
            .into(),
        )
    }
}
