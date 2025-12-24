use ranex_atlas::Atlas;
use std::error::Error;

mod common;

#[test]
fn test_fastapi_dependency_chain_expansion_basic() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/deps.py",
        r#"
from fastapi import Depends, HTTPException


def get_db():
    return None


def get_current_user(db = Depends(get_db)):
    raise HTTPException(status_code=401, detail="Unauthorized")
    return {"id": 1}
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends
from .deps import get_current_user

router = APIRouter()


@router.get("/items")
async def read_items(user = Depends(get_current_user)):
    return []
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let endpoint = atlas
        .get_by_qualified_name("app.api.read_items")?
        .ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint should exist")
        })?;

    assert_eq!(endpoint.kind.as_str(), "endpoint");

    assert_eq!(endpoint.direct_dependencies, vec!["get_current_user".to_string()]);

    assert_eq!(
        endpoint.dependency_chain,
        vec!["get_current_user".to_string(), "get_db".to_string()]
    );

    assert!(endpoint.tags.contains(&"auth_enforced".to_string()));
    assert!(endpoint
        .tags
        .contains(&"auth_http_exception".to_string()));
    assert!(endpoint
        .tags
        .contains(&"auth_enforced_by:get_current_user".to_string()));
    Ok(())
}

#[test]
fn test_common_helpers_build_projects() -> Result<(), Box<dyn Error>> {
    let sample = common::create_sample_project()?;
    assert!(sample.path().join("app/main.py").exists());
    assert!(sample.path().join("app/utils.py").exists());
    assert!(sample
        .path()
        .join("app/features/payment/service.py")
        .exists());

    let with_error = common::create_project_with_error()?;
    assert!(with_error.path().join("app/good.py").exists());
    assert!(with_error.path().join("app/bad.py").exists());

    Ok(())
}

#[test]
fn test_fastapi_dependency_chain_expansion_handles_cycles() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/cycle.py",
        r#"
from fastapi import Depends


def dep_a(x = Depends(dep_b)):
    return 1


def dep_b(y = Depends(dep_a)):
    return 2
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends
from .cycle import dep_a

router = APIRouter()


@router.get("/cycle")
async def read_cycle(v = Depends(dep_a)):
    return v
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let endpoint = atlas
        .get_by_qualified_name("app.api.read_cycle")?
        .ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint should exist")
        })?;

    assert_eq!(endpoint.direct_dependencies, vec!["dep_a".to_string()]);

    assert_eq!(endpoint.dependency_chain, vec!["dep_a".to_string(), "dep_b".to_string()]);
    Ok(())
}

#[test]
fn test_fastapi_security_dependency_is_highlighted() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/security.py",
        r#"
from fastapi import HTTPException


def get_current_user():
    raise HTTPException(status_code=403, detail="Forbidden")
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Security
from .security import get_current_user

router = APIRouter()


@router.get("/secure")
async def read_secure(user = Security(get_current_user, scopes=["items"])):
    return []
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let endpoint = atlas
        .get_by_qualified_name("app.api.read_secure")?
        .ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint should exist")
        })?;

    assert_eq!(endpoint.direct_dependencies, vec!["get_current_user".to_string()]);
    assert_eq!(endpoint.security_dependencies, vec!["get_current_user".to_string()]);

    assert!(endpoint.tags.contains(&"auth_enforced".to_string()));
    assert!(endpoint.tags.contains(&"auth_security".to_string()));
    assert!(endpoint
        .tags
        .contains(&"auth_http_exception".to_string()));
    assert!(endpoint
        .tags
        .contains(&"auth_enforced_by:get_current_user".to_string()));

    Ok(())
}
