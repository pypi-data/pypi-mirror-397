//! Shared test utilities for ranex-core integration tests.

use tempfile::TempDir;

/// Create a temporary project directory with a .ranex folder.
pub fn create_test_project() -> std::io::Result<TempDir> {
    let temp = TempDir::new()?;

    // Create .ranex directory
    let ranex_dir = temp.path().join(".ranex");
    std::fs::create_dir_all(&ranex_dir)?;

    Ok(temp)
}

/// Create a test project with a config file.
pub fn create_project_with_config(config_content: &str) -> std::io::Result<TempDir> {
    let temp = create_test_project()?;

    let config_path = temp.path().join(".ranex").join("config.toml");
    std::fs::write(&config_path, config_content)?;

    Ok(temp)
}
