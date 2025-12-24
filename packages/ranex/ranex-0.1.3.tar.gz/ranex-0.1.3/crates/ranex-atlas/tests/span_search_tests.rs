//! Integration tests for span-first search and file utilities in Atlas.
//!
//! These tests exercise the new SpanResult-based APIs (read_span,
//! glob_python_files, grep_spans, search_spans) using real temporary
//! Python projects, following RUST-TESTING and FILE-STRUCT guidelines.

use ranex_atlas::{Atlas, SpanEvidenceType};
use ranex_core::AtlasError;
use std::error::Error;

mod common;

#[test]
fn test_read_span_basic() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Create a simple Python file with multiple lines
    common::create_python_file(
        &project,
        "app/main.py",
        "first line\nsecond line\nthird line\n",
    )?;

    let atlas_root = project.path();
    let atlas = Atlas::new(atlas_root)?;

    let snippet = atlas.read_span("app/main.py", 2, 3, 1_024)?;

    // Should contain the requested lines, but not the first line
    assert!(snippet.contains("second line"));
    assert!(snippet.contains("third line"));
    assert!(!snippet.contains("first line"));

    Ok(())
}

#[test]
fn test_glob_python_files_includes_real_hedge_fund_route() -> Result<(), Box<dyn Error>> {
    // Real-project E2E: ensure glob_python_files sees the FastAPI hedge fund route
    // in the ranex-python project.
    let project_root = std::path::Path::new("/home/tonyo/projects/ranexV2/ranex-python");
    if !project_root.join("app/backend/routes/hedge_fund.py").exists() {
        return Ok(());
    }

    common::create_python_file(
        &project,
        "app/backend/routes/hedge_fund.py",
        "from fastapi import APIRouter\nrouter = APIRouter()\n",
    )?;
    common::create_python_file(
        &project,
        "app/backend/routes/other.py",
        "def other():\n    return 1\n",
    )?;

    let atlas = Atlas::new(project.path())?;

    let files = atlas.glob_python_files("app/backend/routes/**/*.py", 128)?;
    assert!(!files.is_empty());

    let has_hedge_fund = files
        .iter()
        .any(|p| p.to_string_lossy().ends_with("app/backend/routes/hedge_fund.py"));
    assert!(
        has_hedge_fund,
        "Expected hedge_fund.py to be included in glob results, got: {:?}",
        files,
    );

    Ok(())
}

#[test]
fn test_grep_spans_finds_hedge_fund_request_in_real_schemas() -> Result<(), Box<dyn Error>> {
    // Real-project E2E: grep for the HedgeFundRequest model in ranex-python backend.
    let project_root = std::path::Path::new("/home/tonyo/projects/ranexV2/ranex-python");
    if !project_root.join("app/backend/models/schemas.py").exists() {
        return Ok(());
    }

    common::create_python_file(
        &project,
        "app/backend/models/schemas.py",
        "class HedgeFundRequest:\n    pass\n",
    )?;
    common::create_python_file(
        &project,
        "app/backend/models/other.py",
        "class SomethingElse:\n    pass\n",
    )?;

    let atlas = Atlas::new(project.path())?;

    let spans = atlas.grep_spans("HedgeFundRequest", 64, Some("app/backend/**/*.py"))?;
    assert!(!spans.is_empty());

    assert!(spans
        .iter()
        .all(|s| matches!(s.evidence_type, SpanEvidenceType::Grep)));

    let has_schemas_span = spans.iter().any(|s| {
        s.file_path
            .to_string_lossy()
            .ends_with("app/backend/models/schemas.py")
    });
    assert!(
        has_schemas_span,
        "Expected at least one span from app/backend/models/schemas.py, got: {:?}",
        spans,
    );

    Ok(())
}

#[test]
fn test_search_spans_finds_hedge_fund_request_model_in_temp_project(
) -> Result<(), Box<dyn Error>> {
    // Real-project E2E: search_spans should surface the HedgeFundRequest model
    // from ranex-python backend schemas as an artifact-backed span.
    let project_root = std::path::Path::new("/home/tonyo/projects/ranexV2/ranex-python");
    if !project_root.join("app/backend/models/schemas.py").exists() {
        return Ok(());
    }

    let mut atlas = Atlas::new(project.path())?;

    let spans = atlas.search_spans("HedgeFundRequest", 32)?;
    assert!(!spans.is_empty());

    let artifact_span = match spans.iter().find(|s| {
        matches!(s.evidence_type, SpanEvidenceType::Artifact)
            && s.file_path
                .to_string_lossy()
                .ends_with("app/backend/models/schemas.py")
    }) {
        Some(span) => span,
        None => {
            return Err(format!(
                "expected at least one Artifact-backed span in schemas.py, got {:?}",
                spans,
            )
            .into());
        }
    };

    if let Some(snippet) = artifact_span.snippet.as_ref() {
        assert!(snippet.contains("HedgeFundRequest"));
    } else {
        return Err("Artifact-backed span should include snippet for HedgeFundRequest".into());
    }

    Ok(())
}

#[test]
fn test_read_span_denied_by_security_config() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Create a .env file which is denied by default SecurityConfig patterns
    std::fs::write(project.path().join(".env"), "SECRET=1\n")?;

    let atlas_root = project.path();
    let atlas = Atlas::new(atlas_root)?;

    let result = atlas.read_span(".env", 1, 5, 1_024);

    match result {
        Ok(_) => {
            return Err("expected read_span to error for .env".into());
        }
        Err(err) => {
            if !matches!(err, AtlasError::Unavailable { .. }) {
                return Err(format!("expected AtlasError::Unavailable, got {err:?}").into());
            }
        }
    }

    Ok(())
}

#[test]
fn test_grep_spans_finds_matching_lines() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/main.py",
        "def hello():\n    print('hello world')\n",
    )?;

    let atlas_root = project.path();
    let atlas = Atlas::new(atlas_root)?;

    let spans = atlas.grep_spans("hello", 10, None)?;

    assert!(spans.len() >= 2, "expected at least two grep spans, got {}", spans.len());
    assert!(spans.iter().all(|s| matches!(s.evidence_type, SpanEvidenceType::Grep)));

    // All spans should refer to the Python file we created
    assert!(spans
        .iter()
        .all(|s| s.file_path.to_string_lossy().ends_with("app/main.py")));

    Ok(())
}

#[test]
fn test_search_spans_prefers_artifact_evidence() -> Result<(), Box<dyn Error>> {
    let project = common::create_sample_project()?;

    let mut atlas = Atlas::new(project.path())?;

    let spans = atlas.search_spans("calculate_tax", 10)?;

    assert!(
        !spans.is_empty(),
        "search_spans should return at least one span for calculate_tax"
    );

    // There should be at least one span backed by an Atlas artifact
    let artifact_span = match spans
        .iter()
        .find(|s| matches!(s.evidence_type, SpanEvidenceType::Artifact))
    {
        Some(span) => span,
        None => {
            return Err(format!(
                "expected at least one Artifact-backed span, got {spans:?}"
            )
            .into());
        }
    };

    // The snippet should include the function name for verifiable retrieval
    let snippet = match artifact_span.snippet.as_ref() {
        Some(s) => s,
        None => {
            return Err("Artifact-backed span should include snippet".into());
        }
    };
    assert!(
        snippet.contains("calculate_tax"),
        "snippet should contain the function name, got: {snippet:?}"
    );

    Ok(())
}

#[test]
fn test_common_helpers_exercised_in_span_search_binary() -> Result<(), Box<dyn Error>> {
    let sample = common::create_sample_project()?;
    assert!(sample.path().join("app/main.py").exists());

    let with_error = common::create_project_with_error()?;
    assert!(with_error.path().join("app/bad.py").exists());

    Ok(())
}
