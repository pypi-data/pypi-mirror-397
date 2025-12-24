//! Integration tests for ranex-core configuration.
//!
//! Tests the public API of RanexConfig loading and saving.

use ranex_core::{AtlasConfig, FirewallConfig, LoggingConfig, RanexConfig};
 use std::error::Error;

mod common;

#[test]
fn test_load_default_config_when_missing() -> Result<(), Box<dyn Error>> {
    let temp = common::create_test_project()?;

    // Load config from directory without config file
    let config = RanexConfig::load(temp.path())?;

    // Verify defaults
    assert_eq!(config.atlas.db_filename, "atlas.sqlite");
    assert_eq!(config.logging.level, "info");
    assert!(!config.firewall.enabled);

    Ok(())
}

#[test]
fn test_save_and_load_config() -> Result<(), Box<dyn Error>> {
    let temp = common::create_test_project()?;

    // Create custom config
    let mut config = RanexConfig::default();
    config.atlas.max_file_size = 500_000;
    config.logging.level = "debug".to_string();
    config.firewall.enabled = true;

    // Save config
    config.save(temp.path())?;

    // Load it back
    let loaded = RanexConfig::load(temp.path())?;

    // Verify values persisted
    assert_eq!(loaded.atlas.max_file_size, 500_000);
    assert_eq!(loaded.logging.level, "debug");
    assert!(loaded.firewall.enabled);

    Ok(())
}

#[test]
fn test_load_custom_config_from_toml() -> Result<(), Box<dyn Error>> {
    let config_content = r#"
[atlas]
db_filename = "custom.sqlite"
max_file_size = 2000000
parallel_workers = 8
incremental = false

[logging]
level = "trace"
format = "json"

[firewall]
enabled = true
typosquat_detection = true
typosquat_threshold = 0.9
"#;

    let temp = common::create_project_with_config(config_content)?;

    let config = RanexConfig::load(temp.path())?;

    assert_eq!(config.atlas.db_filename, "custom.sqlite");
    assert_eq!(config.atlas.max_file_size, 2_000_000);
    assert_eq!(config.atlas.parallel_workers, 8);
    assert!(!config.atlas.incremental);
    assert_eq!(config.logging.level, "trace");
    assert_eq!(config.logging.format, "json");
    assert!(config.firewall.enabled);
    assert_eq!(config.firewall.typosquat_threshold, 0.9);

    Ok(())
}

#[test]
fn test_db_path_construction() -> Result<(), Box<dyn Error>> {
    let temp = common::create_test_project()?;
    let config = RanexConfig::default();

    let db_path = config.db_path(temp.path());

    assert!(db_path.ends_with(".ranex/atlas.sqlite"));
    assert!(db_path.starts_with(temp.path()));

    Ok(())
}

#[test]
fn test_atlas_config_defaults() {
    let config = AtlasConfig::default();

    // Check all defaults
    assert_eq!(config.max_file_size, 1_000_000);
    assert_eq!(config.parallel_workers, 4);
    assert_eq!(config.db_filename, "atlas.sqlite");
    assert!(config.incremental);
    assert!(config.extract_docstrings);
    assert!(config.detect_endpoints);
    assert!(config.detect_contracts);

    // Check default ignore patterns
    assert!(config.ignore_patterns.contains(&"__pycache__".to_string()));
    assert!(config.ignore_patterns.contains(&".venv".to_string()));
    assert!(config.ignore_patterns.contains(&".git".to_string()));
}

#[test]
fn test_logging_config_defaults() {
    let config = LoggingConfig::default();

    assert_eq!(config.level, "info");
    assert_eq!(config.format, "pretty");
    assert!(!config.include_location);
    assert!(config.include_target);
}

#[test]
fn test_firewall_config_defaults() {
    let config = FirewallConfig::default();

    assert!(!config.enabled);
    assert!(config.allowed_deps_file.is_none());
    assert!(config.blocked_deps_file.is_none());
    assert!(config.typosquat_detection);
    assert_eq!(config.typosquat_threshold, 0.8);
}
