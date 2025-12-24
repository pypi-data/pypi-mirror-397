//! Integration tests for ranex-core error types.
//!
//! Tests error creation, display, and conversion.

use ranex_core::{AtlasError, ConfigError, RanexError};
use std::path::PathBuf;

#[test]
fn test_atlas_error_walk() {
    let err = AtlasError::walk("/some/path", "permission denied");
    let msg = err.to_string();

    assert!(msg.contains("/some/path"));
    assert!(msg.contains("permission denied"));
}

#[test]
fn test_atlas_error_parse() {
    let err = AtlasError::parse("/bad/file.py", "unexpected token");
    let msg = err.to_string();

    assert!(msg.contains("/bad/file.py"));
    assert!(msg.contains("unexpected token"));
}

#[test]
fn test_atlas_error_database() {
    let err = AtlasError::database("insert", "table not found");
    let msg = err.to_string();

    assert!(msg.contains("insert"));
    assert!(msg.contains("table not found"));
}

#[test]
fn test_atlas_error_syntax() {
    let err = AtlasError::Syntax {
        path: PathBuf::from("broken.py"),
        line: 42,
        message: "invalid syntax".to_string(),
    };
    let msg = err.to_string();

    assert!(msg.contains("broken.py"));
    assert!(msg.contains("42"));
    assert!(msg.contains("invalid syntax"));
}

#[test]
fn test_atlas_error_not_found() {
    let err = AtlasError::NotFound(PathBuf::from("/missing/file.py"));
    let msg = err.to_string();

    assert!(msg.contains("/missing/file.py"));
}

#[test]
fn test_atlas_error_file_too_large() {
    let err = AtlasError::FileTooLarge {
        path: PathBuf::from("huge.py"),
        size: 5_000_000,
        max_size: 1_000_000,
    };
    let msg = err.to_string();

    assert!(msg.contains("huge.py"));
    assert!(msg.contains("5000000"));
    assert!(msg.contains("1000000"));
}

#[test]
fn test_config_error_not_found() {
    let err = ConfigError::NotFound(PathBuf::from("/missing/config.toml"));
    let msg = err.to_string();

    assert!(msg.contains("/missing/config.toml"));
}

#[test]
fn test_config_error_invalid_value() {
    let err = ConfigError::InvalidValue {
        key: "max_file_size".to_string(),
        message: "must be positive".to_string(),
    };
    let msg = err.to_string();

    assert!(msg.contains("max_file_size"));
    assert!(msg.contains("must be positive"));
}

#[test]
fn test_ranex_error_from_atlas() {
    let atlas_err = AtlasError::NotFound(PathBuf::from("test.py"));
    let ranex_err: RanexError = atlas_err.into();
    let msg = ranex_err.to_string();

    assert!(msg.contains("Atlas error"));
    assert!(msg.contains("test.py"));
}

#[test]
fn test_ranex_error_from_config() {
    let config_err = ConfigError::Missing("database_url".to_string());
    let ranex_err: RanexError = config_err.into();
    let msg = ranex_err.to_string();

    assert!(msg.contains("Configuration error"));
    assert!(msg.contains("database_url"));
}

#[test]
fn test_ranex_error_generic() {
    let err = RanexError::generic("Something went wrong");
    let msg = err.to_string();

    assert_eq!(msg, "Something went wrong");
}

#[test]
fn test_ranex_error_validation() {
    let err = RanexError::Validation {
        rule: "no_utils_folder".to_string(),
        message: "utils/ folder is not allowed".to_string(),
    };
    let msg = err.to_string();

    assert!(msg.contains("no_utils_folder"));
    assert!(msg.contains("utils/ folder is not allowed"));
}

#[test]
fn test_ranex_error_import_validation() {
    let err = RanexError::ImportValidation {
        package: "requests-unofficial".to_string(),
        reason: "potential typosquat".to_string(),
        alternatives: vec!["requests".to_string()],
    };
    let msg = err.to_string();

    assert!(msg.contains("requests-unofficial"));
    assert!(msg.contains("potential typosquat"));
}

#[test]
fn test_ranex_error_security_violation() {
    let err = RanexError::SecurityViolation {
        severity: "high".to_string(),
        file_path: PathBuf::from("app/auth.py"),
        line: 100,
        message: "hardcoded password detected".to_string(),
    };
    let msg = err.to_string();

    assert!(msg.contains("high"));
    assert!(msg.contains("app/auth.py"));
    assert!(msg.contains("100"));
    assert!(msg.contains("hardcoded password"));
}
