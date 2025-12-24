//! File discovery subsystem.
//!
//! Provides directory traversal with `.gitignore` and `.ranexignore` support.

mod filter;
mod walker;

pub use filter::IgnoreFilter;
pub use walker::{FileWalker, ScanOptions};
