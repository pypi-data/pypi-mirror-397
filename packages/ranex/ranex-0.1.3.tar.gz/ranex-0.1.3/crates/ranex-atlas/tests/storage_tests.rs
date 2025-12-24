//! Integration tests for the storage module.
//!
//! Tests AtlasRepository CRUD operations.

use ranex_atlas::storage::AtlasRepository;
use ranex_atlas::{ArtifactProcessor, PythonParser};
use ranex_core::{Artifact, ArtifactKind};
use std::error::Error;
use tempfile::tempdir;

#[test]
fn test_repository_in_memory() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let count = repo.count_artifacts()?;

    assert_eq!(count, 0);
    Ok(())
}

#[test]
fn test_store_and_retrieve_artifact() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let artifact = Artifact::new(
        "process_payment",
        "app.payment.process_payment",
        ArtifactKind::Function,
        "app/payment.py",
        "app.payment",
        10,
        25,
    )
    .with_signature("process_payment(amount: float) -> bool")
    .with_docstring("Process a payment.")
    .with_feature("payments");

    repo.store_artifacts(&[artifact])?;

    let results = repo.search_by_symbol("process", 10)?;

    assert_eq!(results.len(), 1);
    let first = results
        .first()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
    assert_eq!(first.symbol_name, "process_payment");
    assert_eq!(first.kind, ArtifactKind::Function);
    assert_eq!(first.feature.as_deref(), Some("payments"));
    Ok(())
}

#[test]
fn test_store_and_retrieve_schema_fields_round_trip() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let dir = tempdir()?;
    let project_root = dir.path();

    let app_dir = project_root.join("app");
    std::fs::create_dir_all(&app_dir)?;
    let file_path = app_dir.join("main.py");

    let code = r#"
from fastapi import APIRouter, Body
from pydantic import BaseModel, field_validator, model_validator

router = APIRouter()

class ItemIn(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str

    @field_validator("name")
    def name_non_empty(cls, v):
        return v

    @model_validator(mode="after")
    def validate_model(self):
        return self

@router.post("/items", response_model=ItemOut)
async def create_item(item: ItemIn = Body(embed=True)):
    return {"id": 1, "name": item.name}
"#;

    std::fs::write(&file_path, code)?;

    let mut parser = PythonParser::new()?;
    let parse_result = parser
        .parse_file(&file_path)
        ?;

    let processor = ArtifactProcessor::new(project_root);
    let artifacts = processor
        .process(parse_result, &file_path)
        ?;

    repo.store_artifacts(&artifacts)?;

    let endpoint = repo
        .get_by_qualified_name("app.main.create_item")
        ?
        .ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint should exist")
        })?;

    assert_eq!(endpoint.kind, ArtifactKind::Endpoint);
    assert_eq!(endpoint.request_models, vec!["ItemIn".to_string()]);
    assert_eq!(endpoint.response_models, vec!["ItemOut".to_string()]);
    assert_eq!(endpoint.pydantic_fields_summary, None);
    assert_eq!(endpoint.pydantic_validators_summary, None);

    let model = repo
        .get_by_qualified_name("app.main.ItemOut")
        ?
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "model should exist"))?;

    assert_eq!(model.kind, ArtifactKind::Model);

    let fields_summary = model
        .pydantic_fields_summary
        .as_deref()
        .ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::InvalidData, "pydantic_fields_summary missing")
        })?;
    let validators_summary = model
        .pydantic_validators_summary
        .as_deref()
        .ok_or_else(|| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "pydantic_validators_summary missing",
            )
        })?;

    let fields_json: serde_json::Value = serde_json::from_str(fields_summary)?;
    let validators_json: serde_json::Value = serde_json::from_str(validators_summary)?;

    assert_eq!(
        fields_json,
        serde_json::json!([
            {"name": "id", "type_expr": "int", "has_default": false},
            {"name": "name", "type_expr": "str", "has_default": false}
        ])
    );

    assert_eq!(
        validators_json,
        serde_json::json!([
            {"name": "name_non_empty", "kind": "field_validator", "fields": ["name"], "mode": null},
            {"name": "validate_model", "kind": "model_validator", "fields": [], "mode": "after"}
        ])
    );
    Ok(())
}

#[test]
fn test_search_by_symbol_partial_match() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let artifacts = vec![
        Artifact::new(
            "calculate_tax",
            "utils.calculate_tax",
            ArtifactKind::Function,
            "utils.py",
            "utils",
            1,
            5,
        ),
        Artifact::new(
            "calculate_discount",
            "utils.calculate_discount",
            ArtifactKind::Function,
            "utils.py",
            "utils",
            10,
            15,
        ),
        Artifact::new(
            "get_user",
            "users.get_user",
            ArtifactKind::Function,
            "users.py",
            "users",
            1,
            5,
        ),
    ];

    repo.store_artifacts(&artifacts)?;

    // Search for "calculate" should return 2 results
    let results = repo
        .search_by_symbol("calculate", 10)
        ?;

    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|a| a.symbol_name.contains("calculate")));

    // Search for "tax" should return 1 result
    let results = repo.search_by_symbol("tax", 10)?;

    assert_eq!(results.len(), 1);
    let first = results
        .first()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
    assert_eq!(first.symbol_name, "calculate_tax");
    Ok(())
}

#[test]
fn test_search_by_feature() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let artifacts = vec![
        Artifact::new(
            "process",
            "payment.process",
            ArtifactKind::Function,
            "payment.py",
            "payment",
            1,
            5,
        )
        .with_feature("payments"),
        Artifact::new(
            "refund",
            "payment.refund",
            ArtifactKind::Function,
            "payment.py",
            "payment",
            10,
            15,
        )
        .with_feature("payments"),
        Artifact::new(
            "get_user",
            "users.get_user",
            ArtifactKind::Function,
            "users.py",
            "users",
            1,
            5,
        )
        .with_feature("users"),
    ];

    repo.store_artifacts(&artifacts)?;

    let results = repo
        .search_by_feature("payments")
        ?;

    assert_eq!(results.len(), 2);
    assert!(results
        .iter()
        .all(|a| a.feature.as_deref() == Some("payments")));
    Ok(())
}

#[test]
fn test_search_respects_limit() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    // Create 10 artifacts with similar names
    let artifacts: Vec<Artifact> = (0..10)
        .map(|i| {
            Artifact::new(
                format!("func_{}", i),
                format!("mod.func_{}", i),
                ArtifactKind::Function,
                "mod.py",
                "mod",
                i * 10,
                i * 10 + 5,
            )
        })
        .collect();

    repo.store_artifacts(&artifacts)?;

    // Search with limit of 3
    let results = repo
        .search_by_symbol("func", 3)
        ?;

    assert_eq!(results.len(), 3);
    Ok(())
}

#[test]
fn test_count_artifacts() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    assert_eq!(repo.count_artifacts()?, 0);

    let artifacts = vec![
        Artifact::new("a", "m.a", ArtifactKind::Function, "m.py", "m", 1, 2),
        Artifact::new("b", "m.b", ArtifactKind::Function, "m.py", "m", 3, 4),
        Artifact::new("C", "m.C", ArtifactKind::Class, "m.py", "m", 5, 10),
    ];

    repo.store_artifacts(&artifacts)?;

    assert_eq!(repo.count_artifacts()?, 3);
    Ok(())
}

#[test]
fn test_upsert_updates_existing() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    // Store initial artifact
    let artifact_v1 = Artifact::new(
        "process",
        "app.process",
        ArtifactKind::Function,
        "app.py",
        "app",
        10,
        20,
    )
    .with_docstring("Version 1");

    repo.store_artifacts(&[artifact_v1])?;

    // Store updated artifact (same qualified_name)
    let artifact_v2 = Artifact::new(
        "process",
        "app.process",               // Same qualified name
        ArtifactKind::AsyncFunction, // Changed kind
        "app.py",
        "app",
        10,
        30, // Changed line_end
    )
    .with_docstring("Version 2"); // Changed docstring

    repo.store_artifacts(&[artifact_v2])?;

    // Should still have only 1 artifact
    assert_eq!(repo.count_artifacts()?, 1);

    // Should have updated values
    let results = repo.search_by_symbol("process", 10)?;

    assert_eq!(results.len(), 1);
    let first = results
        .first()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
    assert_eq!(first.kind, ArtifactKind::AsyncFunction);
    assert_eq!(first.docstring.as_deref(), Some("Version 2"));
    assert_eq!(first.line_end, 30);
    Ok(())
}

#[test]
fn test_delete_file_artifacts() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let artifacts = vec![
        Artifact::new(
            "a",
            "file1.a",
            ArtifactKind::Function,
            "file1.py",
            "file1",
            1,
            2,
        ),
        Artifact::new(
            "b",
            "file1.b",
            ArtifactKind::Function,
            "file1.py",
            "file1",
            3,
            4,
        ),
        Artifact::new(
            "c",
            "file2.c",
            ArtifactKind::Function,
            "file2.py",
            "file2",
            1,
            2,
        ),
    ];

    repo.store_artifacts(&artifacts)?;

    assert_eq!(repo.count_artifacts()?, 3);

    // Delete artifacts from file1.py
    let deleted = repo
        .delete_file_artifacts("file1.py")
        ?;

    assert_eq!(deleted, 2);
    assert_eq!(repo.count_artifacts()?, 1);

    // Only file2.c should remain
    let results = repo.search_by_symbol("", 10)?;

    assert_eq!(results.len(), 1);
    let first = results
        .first()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
    assert_eq!(first.symbol_name, "c");
    Ok(())
}

#[test]
fn test_artifact_with_tags() -> Result<(), Box<dyn Error>> {
    let repo = AtlasRepository::in_memory()?;

    let artifact = Artifact::new(
        "endpoint",
        "api.endpoint",
        ArtifactKind::Endpoint,
        "api.py",
        "api",
        1,
        10,
    )
    .with_tags(vec![
        "http_get".to_string(),
        "fastapi_route".to_string(),
        "authenticated".to_string(),
    ]);

    repo.store_artifacts(&[artifact])?;

    let results = repo
        .search_by_symbol("endpoint", 10)
        ?;

    assert_eq!(results.len(), 1);
    let first = results
        .first()
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "missing result"))?;
    assert_eq!(first.tags.len(), 3);
    assert!(first.tags.contains(&"http_get".to_string()));
    assert!(first.tags.contains(&"fastapi_route".to_string()));
    Ok(())
}
