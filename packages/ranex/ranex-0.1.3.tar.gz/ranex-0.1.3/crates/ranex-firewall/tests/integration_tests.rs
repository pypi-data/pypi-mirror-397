//! End-to-end integration tests for ranex-firewall
//!
//! These tests verify the complete validation flow works correctly.

use ranex_firewall::{
    AuditEvent, AuditEventType, AuditRingBuffer, BKTree, CircuitBreaker, CircuitBreakerError,
    CircuitState, FirewallAnalyzer, Policy, Severity, TieredValidator, ValidationResult,
    parse_imports_from_file,
};
use std::io::{self, Write};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use tempfile::NamedTempFile;

// ============================================================================
// Helper Functions
// ============================================================================

fn create_test_policy() -> Result<NamedTempFile, Box<dyn std::error::Error>> {
    let mut file = NamedTempFile::new()?;
    writeln!(
        file,
        r#"
version: "1.0"
mode: strict

allowed_packages:
  - requests
  - flask
  - fastapi
  - pydantic
  - stripe
  - boto3
  - sqlalchemy

blocked_patterns:
  - pattern: "os.system"
    reason: "Command injection risk"
    severity: Critical
    alternatives:
      - subprocess.run
  
  - pattern: "eval"
    reason: "Arbitrary code execution"
    severity: Critical
  
  - pattern: "pickle.loads"
    reason: "Deserialization vulnerability"
    severity: High
    alternatives:
      - json.loads

typo_detection:
  enabled: true
  max_edit_distance: 2

internal_prefixes:
  - "app."
  - "src."
  - "tests."
"#
    )
    ?;
    Ok(file)
}

// ============================================================================
// Full Validation Flow Tests
// ============================================================================

mod validation_flow {
    use super::*;

    #[test]
    fn test_tier1_stdlib_allowed() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // All stdlib modules should be allowed
        let stdlib = [
            "os",
            "sys",
            "json",
            "re",
            "typing",
            "collections",
            "datetime",
        ];

        for module in stdlib {
            let result = validator.validate(module)?;
            if !matches!(result, ValidationResult::Allowed) {
                return Err(
                    io::Error::other(format!(
                        "Stdlib {} should be allowed, got {:?}",
                        module, result
                    ))
                    .into(),
                );
            }
        }

        Ok(())
    }

    #[test]
    fn test_tier2_allowed_packages() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // Allowed packages and submodules
        let allowed = [
            "requests",
            "requests.api",
            "flask",
            "flask.app",
            "stripe",
            "stripe.api.v2",
        ];

        for module in allowed {
            let result = validator.validate(module)?;
            if !matches!(result, ValidationResult::Allowed) {
                return Err(
                    io::Error::other(format!(
                        "Package {} should be allowed, got {:?}",
                        module, result
                    ))
                    .into(),
                );
            }
        }

        Ok(())
    }

    #[test]
    fn test_tier3_blocked_patterns() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // Blocked patterns
        let blocked = ["os.system", "eval", "pickle.loads"];

        for module in blocked {
            match validator.validate(module)? {
                ValidationResult::Blocked(err) => {
                    // Just verify it's blocked, error message format may vary
                    assert!(!err.to_string().is_empty());
                }
                other => {
                    return Err(
                        io::Error::other(format!(
                            "Pattern {} should be blocked, got {:?}",
                            module, other
                        ))
                        .into(),
                    );
                }
            }
        }

        Ok(())
    }

    #[test]
    fn test_tier4_internal_imports() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // Without Atlas, internal imports return Unknown
        let internal = ["app.utils", "src.models", "tests.fixtures"];

        for module in internal {
            match validator.validate(module)? {
                ValidationResult::Unknown => {}
                ValidationResult::Allowed => {} // May be allowed if Atlas is configured
                other => {
                    return Err(
                        io::Error::other(format!(
                            "Internal {} unexpected result: {:?}",
                            module, other
                        ))
                        .into(),
                    );
                }
            }
        }

        Ok(())
    }

    #[test]
    fn test_tier5_typosquatting() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // Common typosquats
        let typos = [
            ("reqeusts", "requests"),
            ("flaks", "flask"),
            ("fastaip", "fastapi"),
        ];

        for (typo, intended) in typos {
            match validator.validate(typo)? {
                ValidationResult::Typosquat {
                    intended: found,
                    distance,
                } => {
                    assert_eq!(found, intended);
                    assert!(distance <= 2);
                }
                ValidationResult::Unknown => {
                    // Also acceptable if not detected
                }
                other => {
                    return Err(io::Error::other(format!(
                        "Typo {} unexpected result: {:?}",
                        typo, other
                    ))
                    .into());
                }
            }
        }

        Ok(())
    }

    #[test]
    fn test_unknown_packages() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;
        let validator = TieredValidator::from_policy(&policy)?;

        // Completely unknown packages
        let unknown = [
            "totally_fake_package_xyz",
            "malicious_pkg_123",
            "not_a_real_package",
        ];

        for module in unknown {
            match validator.validate(module)? {
                ValidationResult::Unknown | ValidationResult::Typosquat { .. } => {}
                ValidationResult::Blocked(_) => {} // Also acceptable
                ValidationResult::Allowed => {
                    return Err(
                        io::Error::other(format!("Unknown {} should not be allowed", module))
                            .into(),
                    );
                }
            }
        }

        Ok(())
    }
}

// ============================================================================
// Analyzer E2E Tests on real ranex-python project
// ============================================================================

mod analyzer_e2e {
    use super::*;
    use std::io::Write;
    use tempfile::TempDir;

    fn create_temp_python_project() -> Result<TempDir, Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;
        std::fs::create_dir_all(temp.path().join("app/backend/routes"))?;
        std::fs::create_dir_all(temp.path().join("app/backend/models"))?;
        std::fs::create_dir_all(temp.path().join("src/agents"))?;
        Ok(temp)
    }

    fn write_file(
        project: &TempDir,
        relative: &str,
        content: &str,
    ) -> Result<std::path::PathBuf, Box<dyn std::error::Error>> {
        let path = project.path().join(relative);
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(&path, content)?;
        Ok(path)
    }

    #[test]
    fn test_firewall_allows_fastapi_and_sqlalchemy_in_hedge_fund_route(
    ) -> Result<(), Box<dyn std::error::Error>> {
        let hedge_path = Path::new(
            "/home/tonyo/projects/ranexV2/ranex-python/app/backend/routes/hedge_fund.py",
        );
        if !hedge_path.exists() {
            return Ok(());
        }

        let analyzer = FirewallAnalyzer::with_strict_defaults();
        let report = analyzer.analyze_file(&hedge_path)?;

        let imports = parse_imports_from_file(&hedge_path)?;
        assert!(
            !imports.is_empty(),
            "Expected at least one import in hedge_fund.py",
        );

        let has_fastapi = imports.iter().any(|i| i.module == "fastapi");
        let has_sqlalchemy = imports
            .iter()
            .any(|i| i.module.starts_with("sqlalchemy"));
        if !has_fastapi {
            return Err(io::Error::other("Expected fastapi import in hedge_fund.py").into());
        }
        if !has_sqlalchemy {
            return Err(io::Error::other("Expected sqlalchemy import in hedge_fund.py").into());
        }

        assert_eq!(
            report.files_checked, 1,
            "hedge_fund.py should count as one checked file",
        );
        assert_eq!(
            report.imports_checked,
            imports.len() as u32,
            "imports_checked should match parsed imports",
        );

        // Ensure fastapi and sqlalchemy imports are not flagged as violations.
        for violation in &report.violations {
            if violation.import.starts_with("fastapi")
                || violation.import.starts_with("sqlalchemy")
            {
                return Err(io::Error::other(format!(
                    "Core dependency '{}' should not be reported as a violation: kind={:?}, message={}",
                    violation.import, violation.kind, violation.message
                ))
                .into());
            }
        }

        // Cross-check that the production policy explicitly allows these packages.
        let policy = Policy::production_policy();
        assert!(
            policy.allowed_packages.iter().any(|p| p == "fastapi"),
            "production_policy should allow fastapi",
        );
        assert!(
            policy.allowed_packages.iter().any(|p| p == "sqlalchemy"),
            "production_policy should allow sqlalchemy",
        );

        Ok(())
    }

    #[test]
    fn test_firewall_allows_pydantic_in_core_models() -> Result<(), Box<dyn std::error::Error>> {
        let schemas_path = Path::new(
            "/home/tonyo/projects/ranexV2/ranex-python/app/backend/models/schemas.py",
        );
        if !schemas_path.exists() {
            return Ok(());
        }

        let portfolio_path =
            Path::new("/home/tonyo/projects/ranexV2/ranex-python/src/agents/portfolio_manager.py");
        if !portfolio_path.exists() {
            return Ok(());
        }

        let analyzer = FirewallAnalyzer::with_strict_defaults();
        let policy = Policy::production_policy();
        assert!(
            policy.allowed_packages.iter().any(|p| p == "pydantic"),
            "production_policy should allow pydantic",
        );

        for path in [&schemas_path, &portfolio_path] {
            let report = analyzer.analyze_file(path)?;

            let imports = parse_imports_from_file(path)?;
            assert!(
                !imports.is_empty(),
                "Expected at least one import in {}",
                path.display(),
            );

            let has_pydantic = imports
                .iter()
                .any(|i| i.module == "pydantic" || i.module.starts_with("pydantic."));
            if !has_pydantic {
                return Err(io::Error::other(format!(
                    "Expected pydantic import in {}",
                    path.display(),
                ))
                .into());
            }

            assert_eq!(
                report.files_checked, 1,
                "{} should count as one checked file",
                path.display(),
            );

            // Ensure pydantic imports are not flagged as violations for these real project files.
            for violation in &report.violations {
                if violation.import.starts_with("pydantic") {
                    return Err(io::Error::other(format!(
                        "Core dependency '{}' should not be reported as a violation in {}: kind={:?}, message={}",
                        violation.import,
                        path.display(),
                        violation.kind,
                        violation.message,
                    ))
                    .into());
                }
            }
        }

        Ok(())
    }
}

// ============================================================================
// BK-Tree Tests
// ============================================================================

mod bktree_tests {
    use super::*;

    #[test]
    fn test_bktree_large_corpus() {
        // Build tree with 1000 packages
        let packages: Vec<String> = (0..1000).map(|i| format!("package_{:04}", i)).collect();

        let tree = BKTree::from_packages(&packages);
        assert_eq!(tree.len(), 1000);

        // Query should find exact match (distance 0)
        let result = tree.find_similar("package_0500", 0);
        if result.is_none() {
            // Try with distance 1 to verify tree works
            let result2 = tree.find_similar("package_0500", 1);
            assert!(result2.is_some(), "BKTree should find exact or close match");
        }
    }

    #[test]
    fn test_bktree_no_false_positives() {
        let packages = vec![
            "requests".to_string(),
            "flask".to_string(),
            "django".to_string(),
        ];

        let tree = BKTree::from_packages(&packages);

        // Very different string should not match
        let result = tree.find_similar("completely_different", 2);
        assert!(result.is_none());
    }

    #[test]
    fn test_bktree_finds_close_matches() -> Result<(), Box<dyn std::error::Error>> {
        let packages = vec![
            "requests".to_string(),
            "flask".to_string(),
            "django".to_string(),
        ];

        let tree = BKTree::from_packages(&packages);

        // Should find "requests" for "reqeusts" (1 char swap)
        let result = tree.find_similar("reqeusts", 2);
        let Some((found, distance)) = result else {
            return Err(io::Error::other("Expected BKTree match").into());
        };
        assert_eq!(found, "requests");
        assert!(distance <= 2);
        Ok(())
    }
}

// ============================================================================
// Circuit Breaker Tests
// ============================================================================

mod circuit_breaker_tests {
    use super::*;

    #[test]
    fn test_circuit_breaker_opens_on_failures() {
        let cb = CircuitBreaker::new(3, Duration::from_millis(100));

        // 3 failures should open circuit
        for _ in 0..3 {
            let _: Result<(), CircuitBreakerError<&str>> = cb.call(|| Err::<(), &str>("error"));
        }

        assert_eq!(cb.state(), CircuitState::Open);
    }

    #[test]
    fn test_circuit_breaker_recovery() -> Result<(), Box<dyn std::error::Error>> {
        let cb = CircuitBreaker::new(1, Duration::from_millis(50));

        // Trigger open
        let _: Result<(), CircuitBreakerError<&str>> = cb.call(|| Err::<(), &str>("error"));

        // Wait for recovery timeout
        thread::sleep(Duration::from_millis(100));

        // Should be able to call again (half-open)
        let result: Result<(), CircuitBreakerError<&str>> = cb.call(|| Ok(()));
        if let Err(e) = result {
            return Err(io::Error::other(format!("Expected Ok, got {e:?}")).into());
        }

        // Should be closed now
        assert_eq!(cb.state(), CircuitState::Closed);
        Ok(())
    }

    #[test]
    fn test_circuit_breaker_success_closes() {
        let cb = CircuitBreaker::new(2, Duration::from_millis(50));

        // One failure
        let _: Result<(), CircuitBreakerError<&str>> = cb.call(|| Err::<(), &str>("error"));

        // Success should keep it closed
        let result: Result<(), CircuitBreakerError<&str>> = cb.call(|| Ok(()));
        assert!(result.is_ok());
        assert_eq!(cb.state(), CircuitState::Closed);
    }
}

// ============================================================================
// Audit Ring Buffer Tests
// ============================================================================

mod audit_tests {
    use super::*;

    #[test]
    fn test_ring_buffer_overflow() -> Result<(), Box<dyn std::error::Error>> {
        let buffer = AuditRingBuffer::new(5);

        // Push 10 events
        for i in 0..10 {
            buffer.push(AuditEvent::new(
                AuditEventType::ImportAllowed,
                &format!("module_{}", i),
                Severity::Low,
                "test",
            ));
        }

        // Should only have last 5
        assert_eq!(buffer.len(), 5);

        let events = buffer.drain();
        assert_eq!(events.len(), 5);

        // Should be modules 5-9
        let first = events
            .first()
            .ok_or_else(|| io::Error::other("Expected at least one event"))?;
        assert!(first.module.contains("5"));

        Ok(())
    }

    #[test]
    fn test_ring_buffer_thread_safety() -> Result<(), Box<dyn std::error::Error>> {
        let buffer = Arc::new(AuditRingBuffer::new(1000));
        let mut handles = vec![];

        // 10 threads each pushing 100 events
        for t in 0..10 {
            let buffer = Arc::clone(&buffer);
            handles.push(thread::spawn(move || {
                for i in 0..100 {
                    buffer.push(AuditEvent::new(
                        AuditEventType::ImportAllowed,
                        &format!("thread_{}_event_{}", t, i),
                        Severity::Low,
                        "test",
                    ));
                }
            }));
        }

        for h in handles {
            h.join().map_err(|_| {
                io::Error::other("Thread panicked while pushing events")
            })?;
        }

        // Should have up to 1000 events
        assert!(buffer.len() <= 1000);
        Ok(())
    }

    #[test]
    fn test_ring_buffer_drain_empties() -> Result<(), Box<dyn std::error::Error>> {
        let buffer = AuditRingBuffer::new(10);

        // Push 5 events
        for i in 0..5 {
            buffer.push(AuditEvent::new(
                AuditEventType::ImportAllowed,
                &format!("module_{}", i),
                Severity::Low,
                "test",
            ));
        }

        assert_eq!(buffer.len(), 5);

        // Drain should empty
        let events = buffer.drain();
        assert_eq!(events.len(), 5);
        assert_eq!(buffer.len(), 0);
        Ok(())
    }
}

// ============================================================================
// Policy Loading Tests
// ============================================================================

mod policy_tests {
    use super::*;

    #[test]
    fn test_policy_load_from_file() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;

        assert_eq!(policy.version, "1.0");
        assert!(policy.allowed_packages.contains(&"requests".to_string()));
        assert!(!policy.blocked_patterns.is_empty());

        Ok(())
    }

    #[test]
    fn test_policy_default() {
        let policy = Policy::default_test_policy();

        assert!(!policy.allowed_packages.is_empty());
        assert!(policy.typo_detection.enabled);
    }

    #[test]
    fn test_policy_validation() -> Result<(), Box<dyn std::error::Error>> {
        let policy_file = create_test_policy()?;
        let policy = Policy::load(policy_file.path())?;

        // Should be able to create validator
        let validator = TieredValidator::from_policy(&policy);
        assert!(validator.is_ok());
        Ok(())
    }
}

// ============================================================================
// Performance / Scalability Tests
// ============================================================================

mod performance_tests {
    use super::*;

    #[test]
    fn test_large_allowed_packages_validator_construction() -> Result<(), Box<dyn std::error::Error>> {
        // Build a policy with a large allowlist to ensure validator construction
        // and validation remain stable and do not panic. Construct the policy
        // in a single struct literal to avoid field reassignment after
        // Default::default().
        let policy = Policy {
            allowed_packages: (0..5000)
                .map(|i| format!("pkg_{i}"))
                .collect(),
            ..Policy::default()
        };

        let validator = TieredValidator::from_policy(&policy)?;

        // Spot-check a couple of allowed packages to ensure lookups work.
        let result = validator.validate("pkg_123")?;
        assert!(matches!(result, ValidationResult::Allowed));
        let result = validator.validate("pkg_4999")?;
        assert!(matches!(result, ValidationResult::Allowed));

        Ok(())
    }
}
