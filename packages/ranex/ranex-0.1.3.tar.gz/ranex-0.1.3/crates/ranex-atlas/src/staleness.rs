//! Staleness detection for zero-config auto-scan.
//!
//! This module implements the staleness detection logic per Engg Tech Spec §3.4.
//! It combines three strategies to detect when the index needs refreshing:
//!
//! 1. **Git HEAD comparison**: Detects branch switches, pulls, commits
//! 2. **Bounded mtime probe**: Detects uncommitted file changes (with budget)
//! 3. **Time-based fallback**: Re-scan if index is older than threshold

use std::path::Path;
use std::process::Command;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tracing::debug;

/// Default maximum age before forcing a re-scan (1 hour)
pub const DEFAULT_MAX_AGE_SECS: u64 = 3600;

/// Default budget for mtime probe in milliseconds
pub const DEFAULT_MTIME_PROBE_BUDGET_MS: u64 = 50;

/// Metadata about the last scan for staleness checking.
#[derive(Debug, Clone, Default)]
pub struct ScanMetadata {
    /// Unix timestamp of last scan completion
    pub last_scan_at: u64,

    /// Git HEAD commit hash at last scan (if available)
    pub git_head: Option<String>,

    /// Git branch name at last scan (if available)
    pub git_branch: Option<String>,

    /// Maximum mtime of .py files during last scan (Unix timestamp)
    pub last_known_latest_mtime: u64,
}

/// Result of staleness check
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StalenessReason {
    /// Index is fresh, no scan needed
    Fresh,

    /// Git HEAD changed (branch switch, pull, commit)
    GitHeadChanged { old: String, new: String },

    /// File mtime is newer than last scan
    FileModified,

    /// Index is older than max age threshold
    MaxAgeExceeded { age_secs: u64, max_secs: u64 },

    /// First scan (no previous metadata)
    NoPreviousScan,
}

impl StalenessReason {
    /// Returns true if index is stale (needs refresh)
    pub fn is_stale(&self) -> bool {
        !matches!(self, StalenessReason::Fresh)
    }
}

/// Get the current git HEAD commit hash.
///
/// Returns None if:
/// - Not a git repository
/// - Git is not installed
/// - Any other git error
pub fn get_git_head(project_root: &Path) -> Option<String> {
    let output = Command::new("git")
        .arg("rev-parse")
        .arg("HEAD")
        .current_dir(project_root)
        .output()
        .ok()?;

    if output.status.success() {
        let hash = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if !hash.is_empty() {
            return Some(hash);
        }
    }

    None
}

/// Get the current git branch name.
pub fn get_git_branch(project_root: &Path) -> Option<String> {
    let output = Command::new("git")
        .arg("rev-parse")
        .arg("--abbrev-ref")
        .arg("HEAD")
        .current_dir(project_root)
        .output()
        .ok()?;

    if output.status.success() {
        let branch = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if !branch.is_empty() {
            return Some(branch);
        }
    }

    None
}

/// Find the newest mtime among .py files, with a time budget.
///
/// This function walks the project directory looking for .py files and
/// tracks the newest modification time. It stops early if:
/// - The budget is exceeded
/// - A file newer than `threshold` is found (early exit optimization)
///
/// # Arguments
/// * `project_root` - Path to scan
/// * `budget_ms` - Maximum time to spend scanning (in milliseconds)
/// * `threshold` - If a file newer than this is found, return early
///
/// # Returns
/// * `Some(mtime)` - Newest mtime found (Unix timestamp)
/// * `None` - No .py files found or error occurred
pub fn find_newest_py_mtime_with_budget(
    project_root: &Path,
    budget_ms: u64,
    threshold: u64,
) -> Option<u64> {
    let start = Instant::now();
    let budget = Duration::from_millis(budget_ms);
    let mut newest_mtime: u64 = 0;
    let mut files_checked: usize = 0;

    // Use walkdir for efficient directory traversal
    let walker = walkdir::WalkDir::new(project_root)
        .follow_links(false)
        .into_iter()
        .filter_entry(|e| {
            // Skip common non-source directories (must match IgnoreFilter defaults)
            let name = e.file_name().to_string_lossy();
            let name_ref = name.as_ref();
            // Basic ignores
            if matches!(
                name_ref,
                ".git"
                    | ".venv"
                    | "venv"
                    | "env"
                    | ".env"
                    | "virtualenv"
                    | ".virtualenv"
                    | "__pycache__"
                    | "node_modules"
                    | ".ranex"
                    | "dist"
                    | "build"
                    | "eggs"
                    | ".eggs"
                    | ".idea"
                    | ".vscode"
                    | ".tox"
                    | ".nox"
                    | ".pytest_cache"
                    | ".mypy_cache"
                    | ".ruff_cache"
                    | "site-packages"
            ) {
                return false;
            }
            // Glob patterns: ranex-* and *.egg-info
            if name_ref.starts_with("ranex-") || name_ref.ends_with(".egg-info") {
                return false;
            }
            true
        });

    for entry in walker.filter_map(|e| e.ok()) {
        // Check budget
        if start.elapsed() > budget {
            debug!(
                files_checked = files_checked,
                elapsed_ms = start.elapsed().as_millis(),
                "mtime probe budget exceeded"
            );
            break;
        }

        // Only check .py files
        let path = entry.path();
        if path.extension().is_none_or(|ext| ext != "py") {
            continue;
        }

        // Get file mtime
        if let Ok(metadata) = path.metadata()
            && let Ok(modified) = metadata.modified()
            && let Ok(duration) = modified.duration_since(UNIX_EPOCH)
        {
            let mtime = duration.as_secs();
            files_checked += 1;

            if mtime > newest_mtime {
                newest_mtime = mtime;

                // Early exit if we found a file newer than threshold
                if mtime > threshold {
                    debug!(
                        path = %path.display(),
                        mtime = mtime,
                        threshold = threshold,
                        "Found file newer than threshold, early exit"
                    );
                    return Some(mtime);
                }
            }
        }
    }

    debug!(
        files_checked = files_checked,
        newest_mtime = newest_mtime,
        elapsed_ms = start.elapsed().as_millis(),
        "mtime probe complete"
    );

    if newest_mtime > 0 {
        Some(newest_mtime)
    } else {
        None
    }
}

/// Check if the index is stale and needs refreshing.
///
/// Implements the three-strategy approach from Engg Tech Spec §3.4.3:
/// 1. Git HEAD comparison
/// 2. Bounded mtime probe
/// 3. Time-based fallback
pub fn check_staleness(
    project_root: &Path,
    metadata: &ScanMetadata,
    max_age_secs: u64,
    mtime_probe_budget_ms: u64,
) -> StalenessReason {
    // 0. No previous scan means definitely stale
    if metadata.last_scan_at == 0 {
        return StalenessReason::NoPreviousScan;
    }

    // 1. Git HEAD comparison (~1ms)
    if let Some(ref stored_head) = metadata.git_head
        && let Some(current_head) = get_git_head(project_root)
        && stored_head != &current_head
    {
        debug!(
            stored = %stored_head,
            current = %current_head,
            "Git HEAD changed"
        );
        return StalenessReason::GitHeadChanged {
            old: stored_head.clone(),
            new: current_head,
        };
    }
    // If git is unavailable now but was available before, don't fail
    // Fall through to other checks

    // 2. Bounded mtime probe (catches uncommitted edits)
    if let Some(newest_mtime) = find_newest_py_mtime_with_budget(
        project_root,
        mtime_probe_budget_ms,
        metadata.last_known_latest_mtime,
    ) && newest_mtime > metadata.last_known_latest_mtime
    {
        debug!(
            newest = newest_mtime,
            last_known = metadata.last_known_latest_mtime,
            "File modified since last scan"
        );
        return StalenessReason::FileModified;
    }

    // 3. Time-based fallback
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);

    if metadata.last_scan_at > 0 {
        let age = now.saturating_sub(metadata.last_scan_at);
        if age > max_age_secs {
            debug!(
                age_secs = age,
                max_secs = max_age_secs,
                "Index exceeded max age"
            );
            return StalenessReason::MaxAgeExceeded {
                age_secs: age,
                max_secs: max_age_secs,
            };
        }
    }

    StalenessReason::Fresh
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::TempDir;

    #[test]
    fn test_staleness_no_previous_scan() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;
        let metadata = ScanMetadata::default();

        let result = check_staleness(temp.path(), &metadata, 3600, 50);
        assert_eq!(result, StalenessReason::NoPreviousScan);
        assert!(result.is_stale());
        Ok(())
    }

    #[test]
    fn test_staleness_fresh() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;

        // Create a .py file
        let py_file = temp.path().join("test.py");
        let mut f = File::create(&py_file)?;
        f.write_all(b"# test")?;

        let now = match SystemTime::now().duration_since(UNIX_EPOCH) {
            Ok(d) => d.as_secs(),
            Err(_) => 0,
        };

        let metadata = ScanMetadata {
            last_scan_at: now,
            git_head: None,
            git_branch: None,
            last_known_latest_mtime: now + 1, // Future mtime ensures fresh
        };

        let result = check_staleness(temp.path(), &metadata, 3600, 50);
        assert_eq!(result, StalenessReason::Fresh);
        assert!(!result.is_stale());
        Ok(())
    }

    #[test]
    fn test_staleness_max_age_exceeded() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;

        let now = match SystemTime::now().duration_since(UNIX_EPOCH) {
            Ok(d) => d.as_secs(),
            Err(_) => 0,
        };

        let metadata = ScanMetadata {
            last_scan_at: now - 7200, // 2 hours ago
            git_head: None,
            git_branch: None,
            last_known_latest_mtime: now + 1, // Future mtime to skip mtime check
        };

        let result = check_staleness(temp.path(), &metadata, 3600, 50); // 1 hour max
        assert!(matches!(result, StalenessReason::MaxAgeExceeded { .. }));
        assert!(result.is_stale());
        Ok(())
    }

    #[test]
    fn test_find_newest_mtime_empty_dir() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;
        let result = find_newest_py_mtime_with_budget(temp.path(), 100, 0);
        assert!(result.is_none());
        Ok(())
    }

    #[test]
    fn test_find_newest_mtime_with_py_files() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;

        // Create some .py files
        let file1 = temp.path().join("test1.py");
        let file2 = temp.path().join("test2.py");
        let mut f1 = File::create(&file1)?;
        f1.write_all(b"# test1")?;
        std::thread::sleep(std::time::Duration::from_millis(10));
        let mut f2 = File::create(&file2)?;
        f2.write_all(b"# test2")?;

        let result = find_newest_py_mtime_with_budget(temp.path(), 100, 0);
        assert!(result.is_some());
        Ok(())
    }

    #[test]
    fn test_get_git_head_non_repo() -> Result<(), Box<dyn std::error::Error>> {
        let temp = TempDir::new()?;
        let result = get_git_head(temp.path());
        assert!(result.is_none());
        Ok(())
    }
}
