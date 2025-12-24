use ranex_atlas::Atlas;
use std::error::Error;

mod common;

#[test]
fn test_fastapi_config_env_linkage_defaults() -> Result<(), Box<dyn Error>> {
    // Ensure shared helpers are exercised to avoid dead-code warnings.
    let _ = common::create_sample_project()?;
    let _ = common::create_project_with_error()?;

    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/config.py",
        r#"
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    def db_url(self):
        return os.getenv("DB_URL")
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    assert!(
        !report.config_env_links.is_empty(),
        "expected config_env_links to be populated"
    );

    let hits = &report
        .config_env_links
        .first()
        .ok_or("expected config_env_links to have at least one entry")?
        .env_hits;
    assert!(
        hits.iter()
            .any(|h| h.callee.contains("os.getenv") || h.pattern.contains("os.getenv")),
        "expected env hit to include os.getenv"
    );

    Ok(())
}

#[test]
fn test_fastapi_auth_wiring_jwt_permission_and_exception_handler() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/security.py",
        r#"
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_jwt(token: str):
    return {"sub": token}


def permission_check():
    return True


def exception_handler_logic():
    raise HTTPException(status_code=403, detail="forbidden")
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends
from .security import (
    oauth2_scheme,
    decode_jwt,
    permission_check,
    exception_handler_logic,
)

router = APIRouter()


@router.get("/secure2")
def secure2(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    permission_check()
    try:
        exception_handler_logic()
    except Exception:
        pass
    return payload
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    let auth = report
        .auth_wiring
        .iter()
        .find(|a| a.qualified_name.contains("secure2"))
        .ok_or("secure2 endpoint auth wiring missing")?;

    assert!(
        auth.has_security_dependency,
        "expected has_security_dependency to be true"
    );
    assert!(
        auth.has_oauth2_provider,
        "expected has_oauth2_provider to be true"
    );
    assert!(
        auth.has_jwt,
        "expected has_jwt to be true"
    );
    assert!(
        auth.has_permission_checks,
        "expected has_permission_checks to be true"
    );
    assert!(
        auth.has_custom_exception_handler,
        "expected has_custom_exception_handler to be true"
    );
    assert!(
        auth.jwt_calls
            .iter()
            .any(|c| c.contains("decode_jwt")),
        "expected jwt_calls to include decode_jwt, got {:?}",
        auth.jwt_calls
    );
    assert!(
        auth.permission_dependencies
            .iter()
            .any(|c| c.contains("permission_check")),
        "expected permission_dependencies to include permission_check, got {:?}",
        auth.permission_dependencies
    );

    Ok(())
}

#[test]
fn test_fastapi_test_linkage_maps_tests_to_endpoints() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    return "pong"
"#,
    )?;

    common::create_python_file(
        &project,
        "tests/test_api.py",
        r#"
from app.api import ping


def test_ping():
    ping()
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    assert!(
        !report.test_links.is_empty(),
        "expected test_links to capture test->endpoint linkage"
    );

    let link = report
        .test_links
        .first()
        .ok_or("expected test_links to have at least one entry")?;
    assert!(
        link.test_file.contains("tests/test_api.py"),
        "expected test_file to reference tests/test_api.py, got {}",
        link.test_file
    );
    assert!(
        link.endpoint.contains("ping"),
        "expected endpoint name to contain ping, got {}",
        link.endpoint
    );

    Ok(())
}

#[test]
fn test_fastapi_db_patterns_default_matches() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/run")
def run():
    Session.execute(None, "select 1")
    return "ok"
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    assert!(
        !report.db_patterns.is_empty(),
        "expected db_patterns to flag Session.execute usage"
    );

    let db = report
        .db_patterns
        .first()
        .ok_or("expected db_patterns to have at least one entry")?;
    assert!(
        db.callee.contains("Session.execute"),
        "expected callee to include Session.execute, got {}",
        db.callee
    );

    Ok(())
}

#[test]
fn test_fastapi_db_patterns_pooling_and_commit() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker

router = APIRouter()


@router.get("/db")
def db_handler():
    factory = sessionmaker()
    session = factory()
    session.commit()
    return "done"
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    assert!(
        report.db_patterns.len() >= 2,
        "expected db_patterns to include pooling and commit hits"
    );

    let categories: Vec<String> = report.db_patterns.iter().map(|d| d.category.clone()).collect();

    assert!(
        categories.iter().any(|c| c.contains("db_pooling")),
        "expected db_pooling category in db_patterns, got {:?}",
        categories
    );
    assert!(
        categories.iter().any(|c| c.contains("db_commit")),
        "expected db_commit category in db_patterns, got {:?}",
        categories
    );

    Ok(())
}

#[test]
fn test_fastapi_auth_wiring_oauth_security_dependency() -> Result<(), Box<dyn Error>> {
    let project = common::create_python_project()?;

    common::create_python_file(
        &project,
        "app/security.py",
        r#"
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_token(token: str = Depends(oauth2_scheme)):
    return token
"#,
    )?;

    common::create_python_file(
        &project,
        "app/api.py",
        r#"
from fastapi import APIRouter, Depends
from .security import get_token

router = APIRouter()


@router.get("/secure")
def secure(token: str = Depends(get_token)):
    return {"token": token}
"#,
    )?;

    let mut atlas = Atlas::new(project.path())?;
    atlas.scan()?;

    let report = atlas.analyze_fastapi_scaling()?;

    let auth = report
        .auth_wiring
        .iter()
        .find(|a| a.qualified_name.contains("secure"))
        .ok_or("secure endpoint auth wiring missing")?;

    assert!(
        auth.has_security_dependency,
        "expected has_security_dependency to be true"
    );
    assert_eq!(
        auth.security_dependency_count, 1,
        "expected exactly one security dependency"
    );
    assert!(
        auth.security_dependencies
            .iter()
            .any(|d| d.contains("oauth2_scheme")),
        "expected security_dependencies to include oauth2_scheme"
    );
    assert!(
        auth.has_oauth2_provider,
        "expected has_oauth2_provider to be true"
    );

    Ok(())
}
