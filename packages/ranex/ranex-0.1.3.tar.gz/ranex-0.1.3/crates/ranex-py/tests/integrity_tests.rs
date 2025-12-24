mod common;

use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

fn build_ranex_rust_module<'py>(py: Python<'py>) -> PyResult<Bound<'py, pyo3::types::PyModule>> {
    let m = pyo3::types::PyModule::new(py, "ranex_rust")?;
    ranex_rust::ranex_rust(py, &m)?;
    Ok(m)
}

#[test]
fn test_verify_cli_integrity_placeholder_behavior_matches_mode() -> PyResult<()> {
    let _empty_project = common::create_empty_project().map_err(PyErr::from)?;
    let project = common::create_sample_project().map_err(PyErr::from)?;
    let package_dir = project.path().to_string_lossy().to_string();

    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;

        let is_strict: bool = m
            .getattr("is_strict_integrity_mode")?
            .call0()?
            .extract()?;

        let verify = m.getattr("verify_cli_integrity")?;

        let result_any = verify.call1((package_dir.clone(),))?;
        let result: &Bound<'_, PyDict> = result_any.cast()?;

        let cli_entry_any = result
            .get_item("ranex/cli.py")?
            .ok_or_else(|| PyKeyError::new_err("missing ranex/cli.py entry"))?;
        let cli_dict: &Bound<'_, PyDict> = cli_entry_any.cast()?;

        let verified_any = cli_dict
            .get_item("verified")?
            .ok_or_else(|| PyKeyError::new_err("missing verified"))?;
        let verified: bool = verified_any.extract()?;

        let reason_any = cli_dict
            .get_item("reason")?
            .ok_or_else(|| PyKeyError::new_err("missing reason"))?;
        let reason: String = reason_any.extract()?;

        if is_strict {
            assert!(!verified, "strict must fail closed on placeholder hashes");
            assert_eq!(reason, "placeholder_hash");
        } else {
            assert!(verified, "non-strict should mark placeholder as verified");
            assert_eq!(reason, "development_mode");
        }

        Ok(())
    })
}

#[test]
fn test_common_empty_project_helper_is_exercised() -> std::io::Result<()> {
    let project = common::create_empty_project()?;
    assert!(project.path().exists());
    Ok(())
}
