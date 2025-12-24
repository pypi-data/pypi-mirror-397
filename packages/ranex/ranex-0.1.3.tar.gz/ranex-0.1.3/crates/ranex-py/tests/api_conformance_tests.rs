mod common;

use pyo3::exceptions::{PyAssertionError, PyKeyError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};

fn build_ranex_rust_module<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyModule>> {
    let m = PyModule::new(py, "ranex_rust")?;
    ranex_rust::ranex_rust(py, &m)?;
    Ok(m)
}

#[test]
fn test_module_exports_exist() -> PyResult<()> {
    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;
        let d = m.dict();

        assert!(d.contains("__version__")?, "missing __version__");

        assert!(d.contains("Atlas")?, "missing Atlas");
        assert!(d.contains("ArtifactKind")?, "missing ArtifactKind");
        assert!(d.contains("Firewall")?, "missing Firewall");

        assert!(d.contains("version")?, "missing version()");
        assert!(d.contains("init_logging")?, "missing init_logging()");

        assert!(d.contains("compute_file_hash")?, "missing compute_file_hash()");
        assert!(
            d.contains("verify_file_integrity")?,
            "missing verify_file_integrity()"
        );
        assert!(
            d.contains("verify_cli_integrity")?,
            "missing verify_cli_integrity()"
        );
        assert!(
            d.contains("is_strict_integrity_mode")?,
            "missing is_strict_integrity_mode()"
        );

        Ok(())
    })
}

#[test]
fn test_atlas_scan_return_schema() -> PyResult<()> {
    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;

        let _empty_project = common::create_empty_project()?;

        let project = common::create_sample_project()?;
        let atlas_type = m.getattr("Atlas")?;
        let atlas = atlas_type.call1((project.path().to_string_lossy().to_string(),))?;

        let scan_any = atlas.call_method0("scan")?;
        let scan_dict: &Bound<'_, PyDict> = scan_any.cast()?;

        assert!(scan_dict.contains("artifacts_found")?, "missing artifacts_found");
        assert!(scan_dict.contains("files_scanned")?, "missing files_scanned");
        assert!(scan_dict.contains("files_parsed")?, "missing files_parsed");
        assert!(scan_dict.contains("files_failed")?, "missing files_failed");
        assert!(scan_dict.contains("duration_ms")?, "missing duration_ms");
        assert!(scan_dict.contains("stats")?, "missing stats");
        assert!(scan_dict.contains("failed_files")?, "missing failed_files");

        let files_scanned_any = scan_dict
            .get_item("files_scanned")?
            .ok_or_else(|| PyKeyError::new_err("files_scanned missing"))?;
        let files_scanned: u64 = files_scanned_any.extract()?;
        assert!(files_scanned >= 3, "expected >=3 files scanned");

        let artifacts_found_any = scan_dict
            .get_item("artifacts_found")?
            .ok_or_else(|| PyKeyError::new_err("artifacts_found missing"))?;
        let artifacts_found: u64 = artifacts_found_any.extract()?;
        assert!(artifacts_found > 0, "expected >0 artifacts found");

        Ok(())
    })
}

#[test]
fn test_atlas_health_return_schema() -> PyResult<()> {
    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;

        let project = common::create_sample_project()?;
        let atlas_type = m.getattr("Atlas")?;
        let atlas = atlas_type.call1((project.path().to_string_lossy().to_string(),))?;

        // Before scan
        let health_any = atlas.call_method0("health")?;
        let health_dict: &Bound<'_, PyDict> = health_any.cast()?;

        assert!(health_dict.contains("artifact_count")?, "missing artifact_count");
        assert!(health_dict.contains("last_scan")?, "missing last_scan");
        assert!(health_dict.contains("db_path")?, "missing db_path");
        assert!(health_dict.contains("status")?, "missing status");

        let artifact_count_any = health_dict
            .get_item("artifact_count")?
            .ok_or_else(|| PyKeyError::new_err("artifact_count missing"))?;
        let artifact_count: u64 = artifact_count_any.extract()?;
        assert_eq!(artifact_count, 0, "expected 0 artifact_count before scan");

        // After scan
        atlas.call_method0("scan")?;
        let health_any = atlas.call_method0("health")?;
        let health_dict: &Bound<'_, PyDict> = health_any.cast()?;

        let artifact_count_any = health_dict
            .get_item("artifact_count")?
            .ok_or_else(|| PyKeyError::new_err("artifact_count missing"))?;
        let artifact_count: u64 = artifact_count_any.extract()?;
        assert!(artifact_count > 0, "expected >0 artifact_count after scan");

        Ok(())
    })
}

#[test]
fn test_firewall_check_import_schema() -> PyResult<()> {
    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;

        let project = common::create_sample_project()?;
        let firewall_type = m.getattr("Firewall")?;
        let fw = firewall_type.call1((project.path().to_string_lossy().to_string(),))?;

        let res_any = fw.call_method1("check_import", ("os",))?;
        let res: &Bound<'_, PyDict> = res_any.cast()?;

        assert!(res.contains("allowed")?, "missing allowed");
        assert!(res.contains("status")?, "missing status");
        assert!(res.contains("reason")?, "missing reason");
        assert!(res.contains("suggestion")?, "missing suggestion");

        let allowed_any = res
            .get_item("allowed")?
            .ok_or_else(|| PyKeyError::new_err("allowed missing"))?;
        let allowed: bool = allowed_any.extract()?;
        assert!(allowed, "expected stdlib import os to be allowed");

        let res_any = fw.call_method1("check_import", ("os.system",))?;
        let res: &Bound<'_, PyDict> = res_any.cast()?;
        let allowed_any = res
            .get_item("allowed")?
            .ok_or_else(|| PyKeyError::new_err("allowed missing"))?;
        let allowed: bool = allowed_any.extract()?;
        assert!(!allowed, "expected os.system to be blocked");

        let status_any = res
            .get_item("status")?
            .ok_or_else(|| PyKeyError::new_err("status missing"))?;
        let status: String = status_any.extract()?;
        assert_eq!(status, "blocked", "expected status=blocked");

        Ok(())
    })
}

#[test]
fn test_atlas_new_nonexistent_path_raises_filenotfounderror() -> PyResult<()> {
    Python::initialize();

    Python::attach(|py| {
        let m = build_ranex_rust_module(py)?;

        let atlas_type = m.getattr("Atlas")?;
        let result = atlas_type.call1(("/this/path/does/not/exist/at/all",));

        match result {
            Ok(_) => {
                return Err(PyAssertionError::new_err(
                    "expected Atlas(...) to raise for nonexistent path",
                ));
            }
            Err(err) => {
                assert!(
                    err.is_instance_of::<pyo3::exceptions::PyFileNotFoundError>(py),
                    "expected FileNotFoundError, got: {}",
                    err
                );

                let msg = err.to_string();
                assert!(
                    msg.contains("Project not found"),
                    "unexpected error message: {}",
                    msg
                );
            }
        }

        Ok(())
    })
}
