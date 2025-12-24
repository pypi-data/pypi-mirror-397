//! Integration tests for error handling.

use ranex_atlas::Atlas;
use std::path::Path;

/// Test that creating Atlas for non-existent path returns error.
#[test]
fn test_nonexistent_path_error() {
    let result = Atlas::new(Path::new("/this/path/does/not/exist/at/all"));

    assert!(result.is_err());

    // Get the error without requiring Debug trait
    if let Err(err) = result {
        let msg = err.to_string();

        // Should mention the path or indicate not found
        assert!(
            msg.contains("path")
                || msg.contains("not")
                || msg.contains("exist")
                || msg.contains("Not found"),
            "Error should indicate path issue: {}",
            msg
        );
    }
}

/// Test error on invalid project structure.
#[test]
fn test_invalid_project_structure() -> Result<(), Box<dyn std::error::Error>> {
    use tempfile::TempDir;

    // Create a temp dir but don't set up proper structure
    let temp = TempDir::new()?;

    // Atlas should still be creatable (it creates .ranex dir)
    let result = Atlas::new(temp.path());
    assert!(result.is_ok(), "Atlas should handle empty directories");

    Ok(())
}
