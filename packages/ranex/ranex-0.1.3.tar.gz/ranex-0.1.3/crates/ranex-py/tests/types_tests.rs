//! Integration tests for type conversions.
//!
//! Note: Tests that require Python GIL are separate.

use ranex_core::{Artifact, ArtifactKind, ScanStats};

/// Test ArtifactKind string conversion roundtrip.
#[test]
fn test_artifact_kind_roundtrip() {
    let kinds = [
        ArtifactKind::Function,
        ArtifactKind::AsyncFunction,
        ArtifactKind::Class,
        ArtifactKind::Method,
        ArtifactKind::Endpoint,
        ArtifactKind::Contract,
        ArtifactKind::Model,
        ArtifactKind::Constant,
    ];

    for kind in kinds {
        let s = kind.as_str();
        let parsed = ArtifactKind::parse(s);
        assert_eq!(parsed, Some(kind), "Roundtrip failed for {:?}", kind);
    }
}

/// Test Artifact serialization.
#[test]
fn test_artifact_to_json() -> Result<(), Box<dyn std::error::Error>> {
    let artifact = Artifact::new(
        "test_func",
        "app.test.test_func",
        ArtifactKind::Function,
        "app/test.py",
        "app.test",
        10,
        20,
    )
    .with_signature("test_func(x: int)")
    .with_docstring("A test function")
    .with_feature("testing");

    let json = serde_json::to_string(&artifact)?;

    assert!(json.contains("test_func"));
    assert!(json.contains("function"));
    assert!(json.contains("app/test.py"));

    Ok(())
}

/// Test ScanStats tracking.
#[test]
fn test_scan_stats_counting() {
    let mut stats = ScanStats::new();

    stats.files_scanned = 10;
    stats.files_parsed = 8;
    stats.files_failed = 2;

    stats.add_artifact(ArtifactKind::Function);
    stats.add_artifact(ArtifactKind::Function);
    stats.add_artifact(ArtifactKind::Class);

    assert_eq!(stats.artifacts_found, 3);
    assert_eq!(stats.artifacts_by_kind.get("function"), Some(&2));
    assert_eq!(stats.artifacts_by_kind.get("class"), Some(&1));
}
