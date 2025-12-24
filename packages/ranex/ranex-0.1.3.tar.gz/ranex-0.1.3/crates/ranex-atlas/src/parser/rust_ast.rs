//! # Rust AST Parsing
//!
//! Parses Rust source files using tree-sitter-rust to extract artifacts
//! (functions, structs, enums, traits, impl blocks, etc.).
//!
//! This module is used by the Internal Dev Atlas to index the Ranex
//! Rust codebase itself.
//!
//! ## Example
//!
//! ```rust,no_run
//! use ranex_atlas::parser::RustParser;
//! use std::path::Path;
//!
//! let mut parser = RustParser::new()?;
//! let result = parser.parse_file(Path::new("src/lib.rs"))?;
//!
//! for artifact in result.artifacts {
//!     println!("{}: {}", artifact.kind, artifact.name);
//! }
//! # Ok::<(), ranex_core::AtlasError>(())
//! ```

use ranex_core::{Artifact, ArtifactKind, AtlasError};
use std::path::{Path, PathBuf};
use tracing::{debug, instrument};

/// Result of parsing a Rust file.
#[derive(Debug, Default)]
pub struct RustParseResult {
    /// Extracted artifacts (functions, structs, etc.)
    pub artifacts: Vec<RustArtifact>,

    /// Import statements found
    pub imports: Vec<RustImport>,

    /// Module declarations
    pub modules: Vec<RustModule>,

    /// Whether parsing had any errors
    pub had_errors: bool,
}

/// A Rust artifact extracted from source code.
#[derive(Debug, Clone)]
pub struct RustArtifact {
    /// Symbol name (e.g., function name, struct name)
    pub name: String,

    /// Fully qualified name (e.g., `crate::module::function`)
    pub qualified_name: String,

    /// Kind of artifact
    pub kind: RustArtifactKind,

    /// Visibility (pub, pub(crate), private)
    pub visibility: Visibility,

    /// Start line (1-indexed)
    pub line_start: usize,

    /// End line (1-indexed)
    pub line_end: usize,

    /// Documentation comment if present
    pub doc_comment: Option<String>,

    /// Function signature or type definition
    pub signature: Option<String>,

    /// Attributes (e.g., #[test], #[derive(...)])
    pub attributes: Vec<String>,
}

/// Kind of Rust artifact.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RustArtifactKind {
    /// `fn` item
    Function,
    /// `async fn` item
    AsyncFunction,
    /// `struct` item
    Struct,
    /// `enum` item
    Enum,
    /// `trait` item
    Trait,
    /// `impl` block
    Impl,
    /// `type` alias
    TypeAlias,
    /// `const` item
    Const,
    /// `static` item
    Static,
    /// `mod` item
    Module,
    /// `macro_rules!` definition
    Macro,
}

impl std::fmt::Display for RustArtifactKind {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Function => write!(f, "function"),
            Self::AsyncFunction => write!(f, "async_function"),
            Self::Struct => write!(f, "struct"),
            Self::Enum => write!(f, "enum"),
            Self::Trait => write!(f, "trait"),
            Self::Impl => write!(f, "impl"),
            Self::TypeAlias => write!(f, "type_alias"),
            Self::Const => write!(f, "const"),
            Self::Static => write!(f, "static"),
            Self::Module => write!(f, "module"),
            Self::Macro => write!(f, "macro"),
        }
    }
}

/// Visibility of a Rust item.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub enum Visibility {
    /// `pub`
    Public,
    /// `pub(crate)`
    Crate,
    /// `pub(super)`
    Super,
    /// `pub(in path)`
    Restricted(String),
    /// No visibility modifier (private)
    #[default]
    Private,
}

/// A Rust import statement.
#[derive(Debug, Clone)]
pub struct RustImport {
    /// The full use path (e.g., `std::collections::HashMap`)
    pub path: String,

    /// Alias if present (e.g., `use foo as bar`)
    pub alias: Option<String>,

    /// Line number
    pub line: usize,
}

/// A Rust module declaration.
#[derive(Debug, Clone)]
pub struct RustModule {
    /// Module name
    pub name: String,

    /// Whether it's an inline module (has body) or file module
    pub is_inline: bool,

    /// Line number
    pub line: usize,
}

/// Rust source code parser using tree-sitter.
pub struct RustParser {
    /// The tree-sitter parser instance
    parser: tree_sitter::Parser,
}

impl RustParser {
    /// Create a new Rust parser.
    ///
    /// # Errors
    ///
    /// Returns error if the Rust grammar fails to load.
    pub fn new() -> Result<Self, AtlasError> {
        let mut parser = tree_sitter::Parser::new();

        parser
            .set_language(&tree_sitter_rust::LANGUAGE.into())
            .map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to load Rust grammar: {}", e),
            })?;

        Ok(Self { parser })
    }

    /// Parse a Rust source file.
    ///
    /// # Arguments
    ///
    /// * `file_path` - Path to the Rust source file
    ///
    /// # Returns
    ///
    /// Parse result containing extracted artifacts.
    #[instrument(skip(self), fields(file = %file_path.display()))]
    pub fn parse_file(&mut self, file_path: &Path) -> Result<RustParseResult, AtlasError> {
        let source = std::fs::read_to_string(file_path).map_err(|e| AtlasError::Parse {
            path: file_path.to_path_buf(),
            message: format!("Failed to read file: {}", e),
        })?;

        self.parse_source(&source, file_path)
    }

    /// Parse Rust source code from a string.
    ///
    /// # Arguments
    ///
    /// * `source` - The Rust source code
    /// * `file_path` - Path for error messages
    #[instrument(skip(self, source), fields(file = %file_path.display()))]
    pub fn parse_source(
        &mut self,
        source: &str,
        file_path: &Path,
    ) -> Result<RustParseResult, AtlasError> {
        let tree = self
            .parser
            .parse(source, None)
            .ok_or_else(|| AtlasError::Parse {
                path: file_path.to_path_buf(),
                message: "Failed to parse Rust file".to_string(),
            })?;

        let root = tree.root_node();
        let mut result = RustParseResult::default();

        // Check for syntax errors
        if root.has_error() {
            debug!(file = %file_path.display(), "Rust file parsed with syntax errors (tree-sitter)");
            result.had_errors = true;
        }

        // Extract artifacts from the syntax tree
        self.extract_artifacts(&root, source, file_path, &mut result)?;

        debug!(
            artifacts = result.artifacts.len(),
            imports = result.imports.len(),
            "Parsed Rust file"
        );

        Ok(result)
    }

    /// Extract artifacts from a tree-sitter node.
    fn extract_artifacts(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
        result: &mut RustParseResult,
    ) -> Result<(), AtlasError> {
        let mut cursor = node.walk();

        for child in node.children(&mut cursor) {
            match child.kind() {
                "function_item" => {
                    if let Some(artifact) = self.extract_function(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "struct_item" => {
                    if let Some(artifact) = self.extract_struct(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "enum_item" => {
                    if let Some(artifact) = self.extract_enum(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "trait_item" => {
                    if let Some(artifact) = self.extract_trait(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                    // Also extract method signatures INSIDE the trait
                    self.extract_artifacts(&child, source, file_path, result)?;
                }
                "impl_item" => {
                    if let Some(artifact) = self.extract_impl(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                    // Also extract methods INSIDE the impl block
                    self.extract_artifacts(&child, source, file_path, result)?;
                }
                "type_item" => {
                    if let Some(artifact) = self.extract_type_alias(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "const_item" => {
                    if let Some(artifact) = self.extract_const(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "static_item" => {
                    if let Some(artifact) = self.extract_static(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                "mod_item" => {
                    if let Some(module) = self.extract_module(&child, source)? {
                        result.modules.push(module);
                    }
                    // Also extract items INSIDE inline modules
                    self.extract_artifacts(&child, source, file_path, result)?;
                }
                "use_declaration" => {
                    if let Some(import) = self.extract_import(&child, source)? {
                        result.imports.push(import);
                    }
                }
                "macro_definition" => {
                    if let Some(artifact) = self.extract_macro(&child, source, file_path)? {
                        result.artifacts.push(artifact);
                    }
                }
                _ => {
                    // Recurse into other nodes
                    self.extract_artifacts(&child, source, file_path, result)?;
                }
            }
        }

        Ok(())
    }

    /// Extract a function artifact.
    fn extract_function(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);

        // Check if this is an async function by looking at the function modifiers
        // tree-sitter uses "function_modifiers" which contains "async"
        let is_async = node.children(&mut node.walk()).any(|c| {
            c.kind() == "function_modifiers"
                && self
                    .get_node_text(&c, source)
                    .map(|t| t.contains("async"))
                    .unwrap_or(false)
        });

        let kind = if is_async {
            RustArtifactKind::AsyncFunction
        } else {
            RustArtifactKind::Function
        };

        let signature = self.extract_signature(node, source);
        let doc_comment = self.extract_doc_comment(node, source);
        let attributes = self.extract_attributes(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature,
            attributes,
        }))
    }

    /// Extract a struct artifact.
    fn extract_struct(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "type_identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);
        let attributes = self.extract_attributes(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Struct,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes,
        }))
    }

    /// Extract an enum artifact.
    fn extract_enum(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "type_identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);
        let attributes = self.extract_attributes(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Enum,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes,
        }))
    }

    /// Extract a trait artifact.
    fn extract_trait(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "type_identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);
        let attributes = self.extract_attributes(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Trait,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes,
        }))
    }

    /// Extract an impl block artifact.
    fn extract_impl(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        // Get the type being implemented
        let type_name = self
            .get_child_text(node, "type_identifier", source)
            .or_else(|| self.get_child_text(node, "type", source))
            .unwrap_or_else(|| "unknown".to_string());

        // Check if it's a trait impl
        let trait_name = node
            .children(&mut node.walk())
            .find(|c| c.kind() == "trait")
            .and_then(|n| self.get_node_text(&n, source));

        let name = if let Some(trait_name) = &trait_name {
            format!("impl {} for {}", trait_name, type_name)
        } else {
            format!("impl {}", type_name)
        };

        let doc_comment = self.extract_doc_comment(node, source);
        let attributes = self.extract_attributes(node, source);

        Ok(Some(RustArtifact {
            qualified_name: format!("{}::{}", file_path.display(), name),
            name,
            kind: RustArtifactKind::Impl,
            visibility: Visibility::Private, // impl blocks don't have visibility
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes,
        }))
    }

    /// Extract a type alias artifact.
    fn extract_type_alias(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "type_identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::TypeAlias,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes: vec![],
        }))
    }

    /// Extract a const artifact.
    fn extract_const(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Const,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes: vec![],
        }))
    }

    /// Extract a static artifact.
    fn extract_static(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let visibility = self.extract_visibility(node, source);
        let doc_comment = self.extract_doc_comment(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Static,
            visibility,
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes: vec![],
        }))
    }

    /// Extract a macro definition artifact.
    fn extract_macro(
        &self,
        node: &tree_sitter::Node,
        source: &str,
        file_path: &Path,
    ) -> Result<Option<RustArtifact>, AtlasError> {
        let name = self
            .get_child_text(node, "identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        let doc_comment = self.extract_doc_comment(node, source);

        Ok(Some(RustArtifact {
            name: name.clone(),
            qualified_name: format!("{}::{}", file_path.display(), name),
            kind: RustArtifactKind::Macro,
            visibility: Visibility::Public, // macros are effectively public
            line_start: node.start_position().row + 1,
            line_end: node.end_position().row + 1,
            doc_comment,
            signature: None,
            attributes: vec![],
        }))
    }

    /// Extract a module declaration.
    fn extract_module(
        &self,
        node: &tree_sitter::Node,
        source: &str,
    ) -> Result<Option<RustModule>, AtlasError> {
        let name = self
            .get_child_text(node, "identifier", source)
            .or_else(|| self.get_child_text(node, "name", source));

        let Some(name) = name else {
            return Ok(None);
        };

        // Check if it has a body (inline module) or not (file module)
        let is_inline = node
            .children(&mut node.walk())
            .any(|c| c.kind() == "declaration_list");

        Ok(Some(RustModule {
            name,
            is_inline,
            line: node.start_position().row + 1,
        }))
    }

    /// Extract a use/import statement.
    fn extract_import(
        &self,
        node: &tree_sitter::Node,
        source: &str,
    ) -> Result<Option<RustImport>, AtlasError> {
        // Get the full path from the use declaration
        let path = self.get_node_text(node, source).map(|s| {
            s.trim_start_matches("use ")
                .trim_end_matches(';')
                .to_string()
        });

        let Some(path) = path else {
            return Ok(None);
        };

        Ok(Some(RustImport {
            path,
            alias: None, // TODO: Extract alias
            line: node.start_position().row + 1,
        }))
    }

    /// Extract visibility modifier from a node.
    fn extract_visibility(&self, node: &tree_sitter::Node, source: &str) -> Visibility {
        for child in node.children(&mut node.walk()) {
            if child.kind() == "visibility_modifier" {
                let text = self.get_node_text(&child, source).unwrap_or_default();
                return match text.as_str() {
                    "pub" => Visibility::Public,
                    s if s.starts_with("pub(crate)") => Visibility::Crate,
                    s if s.starts_with("pub(super)") => Visibility::Super,
                    s if s.starts_with("pub(in") => {
                        let path = s.trim_start_matches("pub(in ").trim_end_matches(')');
                        Visibility::Restricted(path.to_string())
                    }
                    _ => Visibility::Public,
                };
            }
        }
        Visibility::Private
    }

    /// Extract function signature.
    fn extract_signature(&self, node: &tree_sitter::Node, source: &str) -> Option<String> {
        // Get the text up to the block
        let start = node.start_byte();
        let end = node
            .children(&mut node.walk())
            .find(|c| c.kind() == "block")
            .map(|c| c.start_byte())
            .unwrap_or(node.end_byte());

        source.get(start..end).map(|s| s.trim().to_string())
    }

    /// Extract doc comment from preceding siblings.
    fn extract_doc_comment(&self, node: &tree_sitter::Node, source: &str) -> Option<String> {
        let mut prev = node.prev_sibling();
        let mut doc_lines = Vec::new();

        while let Some(sibling) = prev {
            if sibling.kind() == "line_comment" {
                let text = self.get_node_text(&sibling, source)?;
                if text.starts_with("///") || text.starts_with("//!") {
                    doc_lines.push(
                        text.trim_start_matches("///")
                            .trim_start_matches("//!")
                            .trim()
                            .to_string(),
                    );
                } else {
                    break;
                }
            } else if sibling.kind() != "attribute_item" {
                break;
            }
            prev = sibling.prev_sibling();
        }

        if doc_lines.is_empty() {
            None
        } else {
            doc_lines.reverse();
            Some(doc_lines.join("\n"))
        }
    }

    /// Extract attributes from a node.
    fn extract_attributes(&self, node: &tree_sitter::Node, source: &str) -> Vec<String> {
        let mut attributes = Vec::new();
        let mut prev = node.prev_sibling();

        while let Some(sibling) = prev {
            if sibling.kind() == "attribute_item" {
                if let Some(text) = self.get_node_text(&sibling, source) {
                    attributes.push(text);
                }
            } else if sibling.kind() != "line_comment" {
                break;
            }
            prev = sibling.prev_sibling();
        }

        attributes.reverse();
        attributes
    }

    /// Get text of a child node by kind.
    fn get_child_text(&self, node: &tree_sitter::Node, kind: &str, source: &str) -> Option<String> {
        node.children(&mut node.walk())
            .find(|c| c.kind() == kind)
            .and_then(|n| self.get_node_text(&n, source))
    }

    /// Get text of a node.
    fn get_node_text(&self, node: &tree_sitter::Node, source: &str) -> Option<String> {
        source
            .get(node.start_byte()..node.end_byte())
            .map(|s| s.to_string())
    }
}
// CONVERSION TO RANEX ARTIFACT
// ============================================================================

impl RustArtifact {
    /// Convert to a ranex-core Artifact.
    pub fn to_artifact(&self, file_path: &Path, module_path: &str) -> Artifact {
        Artifact {
            symbol_name: self.name.clone(),
            qualified_name: self.qualified_name.clone(),
            kind: self.kind.into(),
            file_path: file_path.to_path_buf(),
            module_path: module_path.to_string(),
            signature: self.signature.clone(),
            docstring: self.doc_comment.clone(),
            feature: None,
            tags: self.attributes.clone(),
            http_method: None,
            route_path: None,
            router_prefix: None,
            direct_dependencies: Vec::new(),
            dependency_chain: Vec::new(),
            security_dependencies: Vec::new(),
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
            line_start: self.line_start,
            line_end: self.line_end,
            hash: None,
        }
    }
}

impl From<RustArtifactKind> for ArtifactKind {
    fn from(kind: RustArtifactKind) -> Self {
        match kind {
            RustArtifactKind::Function => ArtifactKind::Function,
            RustArtifactKind::AsyncFunction => ArtifactKind::AsyncFunction,
            RustArtifactKind::Struct => ArtifactKind::Class, // Map struct to class
            RustArtifactKind::Enum => ArtifactKind::Class,   // Map enum to class
            RustArtifactKind::Trait => ArtifactKind::Class,  // Map trait to class
            RustArtifactKind::Impl => ArtifactKind::Method,  // Map impl to method
            RustArtifactKind::TypeAlias => ArtifactKind::TypeAlias,
            RustArtifactKind::Const => ArtifactKind::Constant,
            RustArtifactKind::Static => ArtifactKind::Constant,
            RustArtifactKind::Module => ArtifactKind::Function, // Fallback
            RustArtifactKind::Macro => ArtifactKind::Function,  // Fallback
        }
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;
    use rstest::*;
    use std::path::PathBuf;

    fn single_artifact(result: &RustParseResult) -> Result<&RustArtifact, AtlasError> {
        match result.artifacts.as_slice() {
            [artifact] => Ok(artifact),
            other => Err(AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("expected exactly 1 artifact, got {}", other.len()),
            }),
        }
    }

    fn single_module(result: &RustParseResult) -> Result<&RustModule, AtlasError> {
        match result.modules.as_slice() {
            [m] => Ok(m),
            other => Err(AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("expected exactly 1 module, got {}", other.len()),
            }),
        }
    }

    // ========================================================================
    // Unit Tests - Parser Creation
    // ========================================================================

    #[test]
    fn test_parser_creation_succeeds() -> Result<(), AtlasError> {
        let _parser = RustParser::new()?;
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Function Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_simple_function() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
fn hello() {
    println!("Hello");
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.name, "hello");
        assert_eq!(artifact.kind, RustArtifactKind::Function);
        Ok(())
    }

    #[rstest]
    fn test_parse_async_function() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
async fn fetch_data() -> String {
    "data".to_string()
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.name, "fetch_data");
        assert_eq!(artifact.kind, RustArtifactKind::AsyncFunction);
        Ok(())
    }

    #[rstest]
    fn test_parse_pub_function() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
pub fn public_fn() {}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.visibility, Visibility::Public);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Struct Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_struct() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
pub struct MyStruct {
    field: i32,
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.name, "MyStruct");
        assert_eq!(artifact.kind, RustArtifactKind::Struct);
        assert_eq!(artifact.visibility, Visibility::Public);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Enum Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_enum() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
pub enum MyEnum {
    Variant1,
    Variant2(i32),
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.name, "MyEnum");
        assert_eq!(artifact.kind, RustArtifactKind::Enum);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Trait Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_trait() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
pub trait MyTrait {
    fn method(&self);
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        // Should find trait and the method signature
        let trait_artifact = result
            .artifacts
            .iter()
            .find(|a| a.kind == RustArtifactKind::Trait)
            .ok_or_else(|| AtlasError::Parse {
                path: PathBuf::new(),
                message: "expected to find trait artifact".to_string(),
            })?;

        assert_eq!(trait_artifact.name, "MyTrait");
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Impl Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_impl_block() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
struct Foo;

impl Foo {
    fn new() -> Self {
        Foo
    }
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let impl_artifact = result
            .artifacts
            .iter()
            .find(|a| a.kind == RustArtifactKind::Impl)
            .ok_or_else(|| AtlasError::Parse {
                path: PathBuf::new(),
                message: "expected to find impl block".to_string(),
            })?;

        assert_eq!(impl_artifact.kind, RustArtifactKind::Impl);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Import Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_imports() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
use std::collections::HashMap;
use crate::module::Item;
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        assert_eq!(result.imports.len(), 2);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Module Parsing
    // ========================================================================

    #[rstest]
    fn test_parse_inline_module() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
mod inner {
    fn inner_fn() {}
}
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let module = single_module(&result)?;
        assert_eq!(module.name, "inner");
        assert!(module.is_inline);
        Ok(())
    }

    #[rstest]
    fn test_parse_file_module() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
mod other;
"#;

        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let module = single_module(&result)?;
        assert_eq!(module.name, "other");
        assert!(!module.is_inline);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Visibility
    // ========================================================================

    #[rstest]
    #[case("pub fn f() {}", Visibility::Public)]
    #[case("pub(crate) fn f() {}", Visibility::Crate)]
    #[case("pub(super) fn f() {}", Visibility::Super)]
    #[case("fn f() {}", Visibility::Private)]
    fn test_visibility_parsing(
        #[case] source: &str,
        #[case] expected: Visibility,
    ) -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let result = parser
            .parse_source(source, Path::new("test.rs"))
            ?;

        let artifact = single_artifact(&result)?;
        assert_eq!(artifact.visibility, expected);
        Ok(())
    }

    // ========================================================================
    // Unit Tests - Artifact Kind Display
    // ========================================================================

    #[rstest]
    #[case(RustArtifactKind::Function, "function")]
    #[case(RustArtifactKind::AsyncFunction, "async_function")]
    #[case(RustArtifactKind::Struct, "struct")]
    #[case(RustArtifactKind::Enum, "enum")]
    #[case(RustArtifactKind::Trait, "trait")]
    fn test_artifact_kind_display(#[case] kind: RustArtifactKind, #[case] expected: &str) {
        assert_eq!(kind.to_string(), expected);
    }

    // ========================================================================
    // Unit Tests - Complex File
    // ========================================================================

    #[rstest]
    fn test_parse_complex_file() -> Result<(), AtlasError> {
        let mut parser = RustParser::new()?;
        let source = r#"
//! Module documentation

use std::collections::HashMap;

/// A test struct
#[derive(Debug)]
pub struct Config {
    name: String,
}

impl Config {
    /// Create new config
    pub fn new(name: &str) -> Self {
        Self { name: name.to_string() }
    }
}

/// Error type
pub enum Error {
    NotFound,
    Invalid(String),
}

pub trait Configurable {
    fn configure(&mut self);
}

pub const VERSION: &str = "1.0.0";

pub type Result<T> = std::result::Result<T, Error>;

async fn async_helper() {}
"#;

        let result = parser
            .parse_source(source, Path::new("lib.rs"))
            ?;

        // Should find multiple artifacts
        assert!(
            result.artifacts.len() >= 5,
            "Should find at least struct, impl, enum, trait, const. Found: {}",
            result.artifacts.len()
        );

        // Check imports
        assert_eq!(result.imports.len(), 1);
        Ok(())
    }
}
