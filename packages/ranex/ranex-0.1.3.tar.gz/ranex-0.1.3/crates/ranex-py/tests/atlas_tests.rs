//! Integration tests for the Atlas Python bindings.
//!
//! These tests verify the public API of the ranex-py crate.

mod common;

use pyo3::Python;
use ranex_atlas::Atlas;
use std::sync::Once;

fn ensure_python_initialized() {
    static INIT: Once = Once::new();
    INIT.call_once(Python::initialize);
}

/// Test that Atlas can be created for a valid project.
#[test]
fn test_atlas_creation() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;
    let atlas = Atlas::new(project.path())?;

    assert_eq!(
        atlas.project_root().canonicalize()?,
        project.path().canonicalize()?
    );

    Ok(())
}

/// Test scanning a project with Python files.
#[test]
fn test_atlas_scan() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;
    let result = atlas.scan()?;

    // Should find artifacts from the sample files
    assert!(
        result.stats.files_scanned >= 3,
        "Should scan at least 3 files"
    );
    assert!(result.stats.artifacts_found > 0, "Should find artifacts");

    Ok(())
}

/// Test searching for artifacts by symbol name.
#[test]
fn test_atlas_search() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    // Search for "calculate" should find calculate_tax
    let results = atlas.search("calculate", 10)?;

    assert!(!results.is_empty(), "Should find matching artifacts");
    assert!(
        results.iter().any(|a| a.symbol_name.contains("calculate")),
        "Results should contain 'calculate'"
    );

    Ok(())
}

/// Test searching by feature name.
#[test]
fn test_atlas_search_by_feature() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    // Search for payment feature
    let results = atlas.search_by_feature("payment")?;

    // Should find artifacts from payment feature
    // (This depends on feature extraction working correctly)
    for artifact in &results {
        assert_eq!(
            artifact.feature.as_deref(),
            Some("payment"),
            "All results should be from payment feature"
        );
    }

    Ok(())
}

/// Test artifact count.
#[test]
fn test_atlas_count() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;

    // Before scan, count should be 0
    let count_before = atlas.count()?;
    assert_eq!(count_before, 0, "Count should be 0 before scan");

    // After scan, count should be > 0
    atlas.scan()?;
    let count_after = atlas.count()?;
    assert!(count_after > 0, "Count should be > 0 after scan");

    Ok(())
}

/// Test health check.
#[test]
fn test_atlas_health() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;

    // Before scan
    let health = atlas.health()?;
    assert_eq!(health.artifact_count, 0);

    // After scan
    atlas.scan()?;
    let health = atlas.health()?;
    assert!(health.artifact_count > 0);
    assert!(health.db_path.exists());

    Ok(())
}

/// Test scanning an empty project.
#[test]
fn test_atlas_empty_project() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_empty_project()?;

    let mut atlas = Atlas::new(project.path())?;
    let result = atlas.scan()?;

    assert_eq!(result.stats.files_scanned, 0);
    assert_eq!(result.stats.artifacts_found, 0);

    Ok(())
}

/// Test search with no matches.
#[test]
fn test_atlas_search_no_matches() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let results = atlas
        .search("nonexistent_xyz_123", 10)
        ?;

    assert!(results.is_empty(), "Should find no matches");

    Ok(())
}

/// Test search respects limit.
#[test]
fn test_atlas_search_limit() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    // Search with limit of 1
    let results = atlas.search("", 1)?;

    assert!(results.len() <= 1, "Should respect limit");

    Ok(())
}

/// Test that Atlas fails for non-existent project.
#[test]
fn test_atlas_nonexistent_project() {
    let result = Atlas::new(std::path::Path::new("/nonexistent/path/12345"));

    assert!(result.is_err(), "Should fail for non-existent project");
}

/// Test incremental scan (files are cached).
#[test]
fn test_atlas_incremental_scan() -> Result<(), Box<dyn std::error::Error>> {
    ensure_python_initialized();

    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;

    // First scan
    let result1 = atlas.scan()?;
    let artifacts1 = result1.stats.artifacts_found;

    // Second scan should use cache
    let result2 = atlas.scan()?;
    let artifacts2 = result2.stats.artifacts_found;

    // Should have same number of artifacts
    assert_eq!(
        artifacts1, artifacts2,
        "Artifact count should be consistent"
    );

    Ok(())
}
