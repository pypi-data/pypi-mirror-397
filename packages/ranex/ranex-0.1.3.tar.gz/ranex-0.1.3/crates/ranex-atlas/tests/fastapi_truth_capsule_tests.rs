use ranex_atlas::{analysis::FastapiTruthCapsuleRequest, Atlas};
use std::error::Error;

mod common;

#[test]
fn test_truth_capsule_basic_endpoint_groups() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/deps.py",
        r#"
from fastapi import Depends


def get_db():
    return None


def get_current_user(db = Depends(get_db)):
    return {"id": 1}
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .deps import get_current_user


class ItemIn(BaseModel):
    name: str


class ItemOut(BaseModel):
    id: int
    name: str


router = APIRouter()


@router.post("/items")
async def create_item(payload: ItemIn, user = Depends(get_current_user)) -> ItemOut:
    return ItemOut(id=1, name=payload.name)
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let capsule = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("POST".to_string()),
        path: Some("/items".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.api.create_item".to_string()),
        mode: "static".to_string(),
        strict: false,
        max_spans: 256,
        max_dependency_depth: 8,
        max_call_depth: 4,
        max_call_nodes: 64,
        include_snippets: false,
        snippet_max_lines: 0,
    })?;

    assert_eq!(capsule.endpoint.handler_qualified_name, "app.api.create_item");
    assert_eq!(capsule.endpoint.method.as_deref(), Some("POST"));
    assert_eq!(capsule.endpoint.path_template.as_deref(), Some("/items"));

    assert_eq!(capsule.groups.handler.len(), 1, "expected one handler span");
    assert!(
        capsule
            .groups
            .dependencies
            .iter()
            .any(|e| e
                .span
                .symbol
                .as_deref()
                .map(|s| s.ends_with("get_current_user"))
                .unwrap_or(false)),
        "expected dependency span for get_current_user",
    );

    assert!(
        capsule
            .groups
            .schemas
            .iter()
            .any(|e| e
                .span
                .symbol
                .as_deref()
                .map(|s| s.ends_with("ItemIn") || s.ends_with("ItemOut"))
                .unwrap_or(false)),
        "expected schema spans for ItemIn/ItemOut",
    );

    Ok(())
}

#[test]
fn test_truth_capsule_hedge_fund_run_endpoint_in_temp_project() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    // Sanity check that we are pointing at the expected project.
    if !project_root.join("app/backend/routes/hedge_fund.py").exists() {
        return Ok(());
    }


@router.post("/run")
async def run(user = Depends(get_current_user)):
    return {"value": compute(), "user": user}
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let capsule = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("POST".to_string()),
        path: Some("/run".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.backend.routes.hedge_fund.run".to_string()),
        mode: "static".to_string(),
        strict: false,
        max_spans: 1024,
        max_dependency_depth: 8,
        max_call_depth: 6,
        max_call_nodes: 256,
        include_snippets: false,
        snippet_max_lines: 0,
    })?;

    // Endpoint resolution should match the real route definition.
    assert_eq!(
        capsule.endpoint.handler_qualified_name,
        "app.backend.routes.hedge_fund.run",
    );
    assert_eq!(capsule.endpoint.method.as_deref(), Some("POST"));

    // Verify that core groups are populated for this real endpoint.
    assert_eq!(
        capsule.groups.handler.len(),
        1,
        "expected exactly one handler span for hedge_fund.run",
    );

    assert!(
        !capsule.groups.dependencies.is_empty(),
        "expected at least one dependency span for hedge_fund.run",
    );

    assert!(
        !capsule.groups.call_slice.is_empty(),
        "expected call_slice group to be populated for hedge_fund.run",
    );

    // The handler span should originate from the real hedge_fund.py route file.
    let handler_span = capsule
        .groups
        .handler
        .first()
        .ok_or("expected handler group to contain at least one span")?
        .span
        .clone();
    assert!(
        handler_span
            .file_path
            .ends_with("app/backend/routes/hedge_fund.py"),
        "handler span should come from hedge_fund.py, got {}",
        handler_span.file_path,
    );

    Ok(())
}

#[test]
fn test_common_helpers_exercised_in_truth_capsule_binary() -> Result<(), Box<dyn Error>> {
    let sample = common::create_sample_project()?;
    assert!(sample.path().join("app/main.py").exists());

    let with_error = common::create_project_with_error()?;
    assert!(with_error.path().join("app/bad.py").exists());

    Ok(())
}

#[test]
fn test_truth_capsule_strict_mode_errors_on_unresolved_dependency() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/items")
async def read_items(user = Depends(unknown_dep)):
    return []
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let result = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("GET".to_string()),
        path: Some("/items".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.api.read_items".to_string()),
        mode: "static".to_string(),
        strict: true,
        max_spans: 256,
        max_dependency_depth: 8,
        max_call_depth: 4,
        max_call_nodes: 64,
        include_snippets: false,
        snippet_max_lines: 0,
    });

    let err = match result {
        Ok(_) => {
            return Err("expected strict capsule build to fail".into());
        }
        Err(err) => err,
    };
    let msg = format!("{err}");
    assert!(
        msg.contains("Truth Capsule strict mode failed"),
        "unexpected error message: {}",
        msg
    );

    Ok(())
}

#[test]
fn test_truth_capsule_includes_middleware_group() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/main.py",
        r#"
from fastapi import FastAPI


app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request, call_next):
    response = await call_next(request)
    return response
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"status": "ok"}
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let capsule = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("GET".to_string()),
        path: Some("/ping".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.api.ping".to_string()),
        mode: "static".to_string(),
        strict: false,
        max_spans: 256,
        max_dependency_depth: 8,
        max_call_depth: 4,
        max_call_nodes: 64,
        include_snippets: false,
        snippet_max_lines: 0,
    })?;

    assert_eq!(capsule.endpoint.handler_qualified_name, "app.api.ping");

    assert!(
        !capsule.groups.middleware.is_empty(),
        "expected middleware group to be populated",
    );

    let middleware = capsule
        .groups
        .middleware
        .iter()
        .find(|e| {
            e.span
                .symbol
                .as_deref()
                .map(|s| s.contains("add_process_time_header"))
                .unwrap_or(false)
        })
        .ok_or("expected middleware span for add_process_time_header")?;

    assert!(
        middleware
            .span
            .file_path
            .ends_with("app/main.py"),
        "middleware span should originate from app/main.py, got {}",
        middleware.span.file_path,
    );

    Ok(())
}

#[test]
fn test_truth_capsule_exceptions_group_from_call_graph() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/security.py",
        r#"
from fastapi import HTTPException


def exception_handler_logic():
    raise HTTPException(status_code=403, detail="forbidden")
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter
from .security import exception_handler_logic


router = APIRouter()


@router.get("/secure")
async def secure():
    try:
        exception_handler_logic()
    except Exception:
        pass
    return {"ok": True}
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let capsule = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("GET".to_string()),
        path: Some("/secure".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.api.secure".to_string()),
        mode: "static".to_string(),
        strict: false,
        max_spans: 256,
        max_dependency_depth: 8,
        max_call_depth: 8,
        max_call_nodes: 64,
        include_snippets: false,
        snippet_max_lines: 0,
    })?;

    assert_eq!(capsule.endpoint.handler_qualified_name, "app.api.secure");

    assert!(
        !capsule.groups.exceptions.is_empty(),
        "expected exceptions group to be populated",
    );

    let exception_span = capsule
        .groups
        .exceptions
        .iter()
        .find(|e| {
            e.span
                .symbol
                .as_deref()
                .map(|s| s.ends_with("exception_handler_logic"))
                .unwrap_or(false)
        })
        .ok_or("expected exception span for exception_handler_logic")?;

    assert!(
        exception_span
            .span
            .file_path
            .ends_with("app/security.py"),
        "exception span should originate from app/security.py, got {}",
        exception_span.span.file_path,
    );

    Ok(())
}

#[test]
fn test_truth_capsule_call_slice_group_tracks_transitive_callees() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/workflows.py",
        r#"
def step_one():
    return 1


def step_two():
    return 2


def orchestrate():
    a = step_one()
    b = step_two()
    return a + b
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter
from .workflows import orchestrate


router = APIRouter()


@router.get("/run")
async def run():
    return {"value": orchestrate()}
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let capsule = atlas.fastapi_truth_capsule(FastapiTruthCapsuleRequest {
        method: Some("GET".to_string()),
        path: Some("/run".to_string()),
        operation_id: None,
        handler_qualified_name: Some("app.api.run".to_string()),
        mode: "static".to_string(),
        strict: false,
        max_spans: 256,
        max_dependency_depth: 8,
        max_call_depth: 4,
        max_call_nodes: 64,
        include_snippets: false,
        snippet_max_lines: 0,
    })?;

    assert_eq!(capsule.endpoint.handler_qualified_name, "app.api.run");

    assert!(
        !capsule.groups.call_slice.is_empty(),
        "expected call_slice group to be populated",
    );

    let mut symbols: Vec<String> = capsule
        .groups
        .call_slice
        .iter()
        .filter_map(|e| e.span.symbol.clone())
        .collect();
    symbols.sort();

    assert!(
        symbols
            .iter()
            .any(|s| s.ends_with("workflows.orchestrate")),
        "expected call_slice to include orchestrate, got {:?}",
        symbols,
    );
    assert!(
        symbols
            .iter()
            .any(|s| s.ends_with("workflows.step_one")),
        "expected call_slice to include step_one, got {:?}",
        symbols,
    );
    assert!(
        symbols
            .iter()
            .any(|s| s.ends_with("workflows.step_two")),
        "expected call_slice to include step_two, got {:?}",
        symbols,
    );

    Ok(())
}
