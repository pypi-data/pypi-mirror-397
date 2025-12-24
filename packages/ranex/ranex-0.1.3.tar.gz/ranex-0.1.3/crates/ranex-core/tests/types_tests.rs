//! Integration tests for ranex-core types.
//!
//! Tests the public API of Artifact, ArtifactKind, and related types.

use ranex_core::{Artifact, ArtifactKind, FileStatus, ScanStats};
use std::path::PathBuf;

#[test]
fn test_artifact_creation() {
    let artifact = Artifact::new(
        "process_payment",
        "app.services.payment.process_payment",
        ArtifactKind::Function,
        "app/services/payment.py",
        "app.services.payment",
        10,
        35,
    );

    assert_eq!(artifact.symbol_name, "process_payment");
    assert_eq!(
        artifact.qualified_name,
        "app.services.payment.process_payment"
    );
    assert_eq!(artifact.kind, ArtifactKind::Function);
    assert_eq!(artifact.file_path, PathBuf::from("app/services/payment.py"));
    assert_eq!(artifact.module_path, "app.services.payment");
    assert_eq!(artifact.line_start, 10);
    assert_eq!(artifact.line_end, 35);
    assert!(artifact.signature.is_none());
    assert!(artifact.docstring.is_none());
    assert!(artifact.feature.is_none());
    assert!(artifact.tags.is_empty());
}

#[test]
fn test_artifact_builder_methods() {
    let artifact = Artifact::new(
        "calculate_tax",
        "utils.tax.calculate_tax",
        ArtifactKind::Function,
        "utils/tax.py",
        "utils.tax",
        5,
        15,
    )
    .with_signature("calculate_tax(amount: float, rate: float) -> float")
    .with_docstring("Calculate tax on the given amount.")
    .with_feature("billing")
    .with_tag("utility")
    .with_tag("pure_function");

    assert_eq!(
        artifact.signature.as_deref(),
        Some("calculate_tax(amount: float, rate: float) -> float")
    );
    assert_eq!(
        artifact.docstring.as_deref(),
        Some("Calculate tax on the given amount.")
    );
    assert_eq!(artifact.feature.as_deref(), Some("billing"));
    assert_eq!(artifact.tags.len(), 2);
    assert!(artifact.tags.contains(&"utility".to_string()));
    assert!(artifact.tags.contains(&"pure_function".to_string()));
}

#[test]
fn test_artifact_kind_as_str() {
    assert_eq!(ArtifactKind::Function.as_str(), "function");
    assert_eq!(ArtifactKind::AsyncFunction.as_str(), "async_function");
    assert_eq!(ArtifactKind::Class.as_str(), "class");
    assert_eq!(ArtifactKind::Method.as_str(), "method");
    assert_eq!(ArtifactKind::Endpoint.as_str(), "endpoint");
    assert_eq!(ArtifactKind::Contract.as_str(), "contract");
    assert_eq!(ArtifactKind::Model.as_str(), "model");
    assert_eq!(ArtifactKind::Constant.as_str(), "constant");
    assert_eq!(ArtifactKind::TypeAlias.as_str(), "type_alias");
}

#[test]
fn test_artifact_kind_from_str() {
    assert_eq!(
        ArtifactKind::parse("function"),
        Some(ArtifactKind::Function)
    );
    assert_eq!(
        ArtifactKind::parse("FUNCTION"),
        Some(ArtifactKind::Function)
    );
    assert_eq!(
        ArtifactKind::parse("async_function"),
        Some(ArtifactKind::AsyncFunction)
    );
    assert_eq!(ArtifactKind::parse("class"), Some(ArtifactKind::Class));
    assert_eq!(
        ArtifactKind::parse("endpoint"),
        Some(ArtifactKind::Endpoint)
    );
    assert_eq!(
        ArtifactKind::parse("contract"),
        Some(ArtifactKind::Contract)
    );
    assert_eq!(ArtifactKind::parse("invalid"), None);
}

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
        ArtifactKind::TypeAlias,
    ];

    for kind in kinds {
        let s = kind.as_str();
        let parsed = ArtifactKind::parse(s);
        assert_eq!(parsed, Some(kind), "Roundtrip failed for {:?}", kind);
    }
}

#[test]
fn test_scan_stats_new() {
    let stats = ScanStats::new();

    assert_eq!(stats.files_scanned, 0);
    assert_eq!(stats.files_parsed, 0);
    assert_eq!(stats.files_failed, 0);
    assert_eq!(stats.files_skipped, 0);
    assert_eq!(stats.files_cached, 0);
    assert_eq!(stats.artifacts_found, 0);
    assert!(stats.artifacts_by_kind.is_empty());
}

#[test]
fn test_scan_stats_add_artifact() {
    let mut stats = ScanStats::new();

    stats.add_artifact(ArtifactKind::Function);
    stats.add_artifact(ArtifactKind::Function);
    stats.add_artifact(ArtifactKind::Class);
    stats.add_artifact(ArtifactKind::Endpoint);

    assert_eq!(stats.artifacts_found, 4);
    assert_eq!(stats.artifacts_by_kind.get("function"), Some(&2));
    assert_eq!(stats.artifacts_by_kind.get("class"), Some(&1));
    assert_eq!(stats.artifacts_by_kind.get("endpoint"), Some(&1));
    assert_eq!(stats.artifacts_by_kind.get("method"), None);
}

#[test]
fn test_file_status_as_str() {
    assert_eq!(FileStatus::Success.as_str(), "success");
    assert_eq!(FileStatus::Failed.as_str(), "failed");
    assert_eq!(FileStatus::Skipped.as_str(), "skipped");
    assert_eq!(FileStatus::Cached.as_str(), "cached");
}

#[test]
fn test_artifact_serialization() {
    let artifact = Artifact::new(
        "test_func",
        "test.test_func",
        ArtifactKind::Function,
        "test.py",
        "test",
        1,
        5,
    )
    .with_tags(vec!["tag1".to_string(), "tag2".to_string()]);

    // Serialize to JSON
    let json_res = serde_json::to_string(&artifact);
    assert!(json_res.is_ok(), "Expected JSON serialization to succeed");
    let Ok(json) = json_res else {
        return;
    };

    // Deserialize back
    let deserialized_res: Result<Artifact, _> = serde_json::from_str(&json);
    assert!(deserialized_res.is_ok(), "Expected JSON deserialization to succeed");
    let Ok(deserialized) = deserialized_res else {
        return;
    };

    assert_eq!(deserialized.symbol_name, artifact.symbol_name);
    assert_eq!(deserialized.kind, artifact.kind);
    assert_eq!(deserialized.tags, artifact.tags);
}
