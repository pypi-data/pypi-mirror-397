//! Source code parsing module.
//!
//! This module provides parsers for different programming languages:
//!
//! - **Python**: Uses PyO3 to call Python's built-in `ast` module for parsing,
//!   ensuring 100% compatibility with all Python syntax.
//! - **Rust** (optional): Uses tree-sitter-rust for parsing Rust source code.
//!   Only available when the `rust-parsing` feature is enabled.
//!   This is for internal Dev Atlas use only - NOT shipped to end users.

mod extractor;
mod python_ast;

// Rust parser module - ONLY available with rust-parsing feature
#[cfg(feature = "rust-parsing")]
pub mod rust_ast;

// Python parser exports (always available for end users)
pub use extractor::{
    CallInfo, DefinitionInfo, DefinitionType, FastapiRole, ImportInfo, ParameterInfo,
    SymbolExtractor,
};
pub use python_ast::{ParseResult, PythonParser};

// Rust parser exports - ONLY available with rust-parsing feature
// This is NEVER shipped to end-user ranex-py package
#[cfg(feature = "rust-parsing")]
pub use rust_ast::{
    RustArtifact, RustArtifactKind, RustImport, RustModule, RustParseResult, RustParser, Visibility,
};
