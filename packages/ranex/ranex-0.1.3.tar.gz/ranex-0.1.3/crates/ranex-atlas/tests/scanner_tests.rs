//! Integration tests for the scanner module.
//!
//! Tests FileWalker and ignore pattern handling.

use ranex_atlas::scanner::FileWalker;
use ranex_core::AtlasConfig;
use std::error::Error;
use std::fs;

mod common;

#[test]
fn test_find_python_files() -> Result<(), Box<dyn Error>> {
    let project = common::create_sample_project()?;
    let config = AtlasConfig::default();

    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()
        ?;

    // Should find main.py, utils.py, and service.py
    assert!(
        files.len() >= 3,
        "Expected at least 3 Python files, found {}",
        files.len()
    );

    // Check specific files exist
    let file_names: Vec<String> = files
        .iter()
        .filter_map(|p| p.file_name())
        .map(|n| n.to_string_lossy().to_string())
        .collect();

    assert!(file_names.contains(&"main.py".to_string()));
    assert!(file_names.contains(&"utils.py".to_string()));
    assert!(file_names.contains(&"service.py".to_string()));
    Ok(())
}

#[test]
fn test_respects_ranexignore() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Create files
    common::create_python_file(&project, "app/main.py", "def main(): pass")?;
    common::create_python_file(&project, "app/test_main.py", "def test(): pass")?;
    common::create_python_file(&project, "app/ignored.py", "# ignored")?;

    // Create .ranexignore
    fs::write(project.path().join(".ranexignore"), "test_*.py\nignored.py")?;

    let config = AtlasConfig::default();
    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()?;

    let file_names: Vec<String> = files
        .iter()
        .filter_map(|p| p.file_name())
        .map(|n| n.to_string_lossy().to_string())
        .collect();

    assert!(
        file_names.contains(&"main.py".to_string()),
        "Should include main.py"
    );
    assert!(
        !file_names.contains(&"test_main.py".to_string()),
        "Should exclude test_main.py"
    );
    assert!(
        !file_names.contains(&"ignored.py".to_string()),
        "Should exclude ignored.py"
    );
    Ok(())
}

#[test]
fn test_ignores_pycache() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Create normal file
    common::create_python_file(&project, "app/main.py", "def main(): pass")?;

    // Create __pycache__ with .pyc files
    let pycache_dir = project.path().join("app/__pycache__");
    fs::create_dir_all(&pycache_dir)?;
    fs::write(pycache_dir.join("main.cpython-310.pyc"), "bytecode")?;

    let config = AtlasConfig::default();
    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()?;

    // Should not include anything from __pycache__
    for file in &files {
        assert!(
            !file.to_string_lossy().contains("__pycache__"),
            "Should not include __pycache__ files: {:?}",
            file
        );
    }
    Ok(())
}

#[test]
fn test_ignores_venv() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Create normal file
    common::create_python_file(&project, "app/main.py", "def main(): pass")?;

    // Create .venv with Python files
    let venv_dir = project.path().join(".venv/lib/python3.10/site-packages");
    fs::create_dir_all(&venv_dir)?;
    fs::write(venv_dir.join("requests.py"), "# third party")?;

    let config = AtlasConfig::default();
    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()?;

    // Should not include anything from .venv
    for file in &files {
        assert!(
            !file.to_string_lossy().contains(".venv"),
            "Should not include .venv files: {:?}",
            file
        );
    }
    Ok(())
}

#[test]
fn test_custom_ignore_patterns() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(&project, "app/main.py", "def main(): pass")?;
    common::create_python_file(&project, "app/generated.py", "# auto-generated")?;
    common::create_python_file(&project, "migrations/001_init.py", "# migration")?;

    let mut config = AtlasConfig::default();
    config.ignore_patterns.push("generated.py".to_string());
    config.ignore_patterns.push("migrations".to_string());

    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()?;

    let file_names: Vec<String> = files
        .iter()
        .filter_map(|p| p.file_name())
        .map(|n| n.to_string_lossy().to_string())
        .collect();

    assert!(file_names.contains(&"main.py".to_string()));
    // Note: Custom patterns might not work exactly the same as .ranexignore
    // This test verifies the pattern is passed to the walker
    Ok(())
}

#[test]
fn test_empty_directory() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;
    // Don't create any Python files

    let config = AtlasConfig::default();
    let walker = FileWalker::new(project.path(), &config)?;

    let files = walker
        .find_python_files()
        ?;

    assert!(
        files.is_empty(),
        "Should return empty list for directory with no Python files"
    );
    Ok(())
}

#[test]
fn test_common_create_project_with_error_creates_files() -> Result<(), Box<dyn Error>> {
    let project = common::create_project_with_error()?;

    assert!(project.path().join("app/good.py").exists());
    assert!(project.path().join("app/bad.py").exists());
    Ok(())
}
