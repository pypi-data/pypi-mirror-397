//! Core domain types for Ranex.
//!
//! These types represent the fundamental data structures used across
//! all Ranex crates, particularly for Atlas indexing.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Represents a code artifact (function, class, endpoint, etc.) discovered during scanning.
///
/// An artifact is any named entity in the codebase that might be relevant
/// for AI tools to know about - functions to reuse, classes to extend,
/// endpoints to call, contracts to honor.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Artifact {
    /// Simple name of the symbol (e.g., "calculate_tax")
    pub symbol_name: String,

    /// Fully qualified name (e.g., "app.utils.tax.calculate_tax")
    pub qualified_name: String,

    /// Classification of the artifact
    pub kind: ArtifactKind,

    /// File path relative to project root
    pub file_path: PathBuf,

    /// Python import path (e.g., "app.utils.tax")
    pub module_path: String,

    /// Function/method signature (e.g., "(amount: float, rate: float) -> float")
    pub signature: Option<String>,

    /// Extracted docstring
    pub docstring: Option<String>,

    /// Feature name extracted from path (e.g., "payment" from "features/payment/service.py")
    pub feature: Option<String>,

    /// Tags for categorization (e.g., ["fastapi_route", "http_get"])
    #[serde(default)]
    pub tags: Vec<String>,

    /// HTTP method if this artifact is a FastAPI endpoint (e.g., "get", "post").
    #[serde(default)]
    pub http_method: Option<String>,

    /// HTTP route path if this artifact is a FastAPI endpoint (e.g., "/payments/{id}").
    #[serde(default)]
    pub route_path: Option<String>,

    /// Router prefix associated with the endpoint, if known (e.g., "/api/v1").
    #[serde(default)]
    pub router_prefix: Option<String>,

    /// Direct FastAPI dependency callables used by this artifact (if any).
    ///
    /// This is typically populated for endpoint handlers and dependency functions.
    #[serde(default)]
    pub direct_dependencies: Vec<String>,

    /// Transitive dependency chain (expanded from direct_dependencies).
    #[serde(default)]
    pub dependency_chain: Vec<String>,

    /// Dependencies declared via FastAPI `Security(...)` (subset of direct_dependencies).
    #[serde(default)]
    pub security_dependencies: Vec<String>,

    #[serde(default)]
    pub request_models: Vec<String>,

    #[serde(default)]
    pub response_models: Vec<String>,

    #[serde(default)]
    pub pydantic_fields_summary: Option<String>,

    #[serde(default)]
    pub pydantic_validators_summary: Option<String>,

    /// Starting line number (1-indexed)
    pub line_start: usize,

    /// Ending line number (1-indexed)
    pub line_end: usize,

    /// Content hash for change detection
    pub hash: Option<String>,
}

/// Classification of code artifacts.
///
/// Used to distinguish different types of symbols for filtering
/// and presentation to AI tools.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[cfg_attr(test, derive(proptest_derive::Arbitrary))]
#[serde(rename_all = "lowercase")]
pub enum ArtifactKind {
    /// Regular function definition
    Function,

    /// Async function (async def)
    AsyncFunction,

    /// Class definition
    Class,

    /// Class method (inside a class)
    Method,

    /// HTTP endpoint (FastAPI @app.get, @router.post, etc.)
    Endpoint,

    /// Contract-decorated function (@Contract)
    Contract,

    /// Pydantic model (inherits from BaseModel)
    Model,

    /// Module-level constant (SCREAMING_CASE)
    Constant,

    /// Type alias or TypeVar
    TypeAlias,
}

impl ArtifactKind {
    /// Convert to string representation for database storage
    pub fn as_str(&self) -> &'static str {
        match self {
            ArtifactKind::Function => "function",
            ArtifactKind::AsyncFunction => "async_function",
            ArtifactKind::Class => "class",
            ArtifactKind::Method => "method",
            ArtifactKind::Endpoint => "endpoint",
            ArtifactKind::Contract => "contract",
            ArtifactKind::Model => "model",
            ArtifactKind::Constant => "constant",
            ArtifactKind::TypeAlias => "type_alias",
        }
    }

    /// Parse from string (database retrieval)
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "function" => Some(ArtifactKind::Function),
            "async_function" => Some(ArtifactKind::AsyncFunction),
            "class" => Some(ArtifactKind::Class),
            "method" => Some(ArtifactKind::Method),
            "endpoint" => Some(ArtifactKind::Endpoint),
            "contract" => Some(ArtifactKind::Contract),
            "model" => Some(ArtifactKind::Model),
            "constant" => Some(ArtifactKind::Constant),
            "type_alias" | "typealias" => Some(ArtifactKind::TypeAlias),
            _ => None,
        }
    }
}

impl std::fmt::Display for ArtifactKind {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Information about a scanned file.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct FileInfo {
    /// File path relative to project root
    pub path: PathBuf,

    /// Content hash for change detection (Blake3 or SHA256)
    pub hash: String,

    /// File modification timestamp (Unix epoch)
    pub last_modified: u64,

    /// Parse status
    pub status: FileStatus,

    /// Error message if parsing failed
    pub error: Option<String>,

    /// Number of lines in file
    pub line_count: usize,

    /// Number of artifacts found
    pub artifact_count: usize,
}

/// Status of a file after scanning.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum FileStatus {
    /// Successfully parsed
    Success,
    /// Parsing failed (syntax error, encoding, etc.)
    Failed,
    /// Skipped (too large, binary, ignored pattern)
    Skipped,
    /// Cached (unchanged since last scan)
    Cached,
}

impl FileStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            FileStatus::Success => "success",
            FileStatus::Failed => "failed",
            FileStatus::Skipped => "skipped",
            FileStatus::Cached => "cached",
        }
    }
}

/// Result of a complete scan operation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    /// Statistics about the scan
    pub stats: ScanStats,

    /// Files that failed to parse (for error reporting)
    pub failed_files: Vec<FileInfo>,

    /// Scan duration in milliseconds
    pub duration_ms: u64,
}

/// Statistics from a scan operation.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ScanStats {
    /// Total files scanned
    pub files_scanned: usize,

    /// Files successfully parsed
    pub files_parsed: usize,

    /// Files that failed parsing
    pub files_failed: usize,

    /// Files skipped (too large, ignored, etc.)
    pub files_skipped: usize,

    /// Files unchanged (used cache)
    pub files_cached: usize,

    /// Total artifacts found
    pub artifacts_found: usize,

    /// Breakdown by artifact kind
    #[serde(default)]
    pub artifacts_by_kind: std::collections::HashMap<String, usize>,
}

impl ScanStats {
    /// Create new empty stats
    pub fn new() -> Self {
        Self::default()
    }

    /// Increment artifact count for a specific kind
    pub fn add_artifact(&mut self, kind: ArtifactKind) {
        self.artifacts_found += 1;
        *self
            .artifacts_by_kind
            .entry(kind.as_str().to_string())
            .or_insert(0) += 1;
    }
}

// ============================================================================
// Import Edge Types (ADR: ATLAS-ADR-DATABASE.md)
// ============================================================================

/// Represents an import relationship between two files.
///
/// This is an edge in the dependency graph, tracking which files import which.
/// Per ADR ATLAS-ADR-DATABASE.md Option A, each occurrence is stored separately
/// (using line_number as part of the key) to ensure 100% accuracy.
///
/// # Example
///
/// ```
/// use ranex_core::{ImportEdge, ImportType};
///
/// // app/main.py imports app/commons/database on line 5
/// let edge = ImportEdge::new(
///     "app/main.py",
///     "app/commons/database.py",
///     "app.commons.database",
///     ImportType::Module,
///     5,
/// );
/// ```
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ImportEdge {
    /// Source file containing the import statement
    pub source_file: String,

    /// Target file being imported (resolved path)
    pub target_file: String,

    /// Full import name (e.g., "app.commons.database")
    pub import_name: String,

    /// Type of import
    pub import_type: ImportType,

    /// Line number of the import statement (1-indexed)
    pub line_number: usize,

    /// Import alias if any (e.g., "db" for "import database as db")
    pub alias: Option<String>,

    /// Whether this is a wildcard import (from x import *)
    pub is_wildcard: bool,
}

/// Type of import statement.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[cfg_attr(test, derive(proptest_derive::Arbitrary))]
#[serde(rename_all = "lowercase")]
pub enum ImportType {
    /// `import module` - full module import
    Module,
    /// `from module import symbol` - specific symbol import
    From,
    /// `from module import *` - wildcard import
    Wildcard,
    /// `from . import x` or `from .. import y` - relative import
    Relative,
}

impl ImportType {
    /// Convert to string for database storage
    pub fn as_str(&self) -> &'static str {
        match self {
            ImportType::Module => "module",
            ImportType::From => "from",
            ImportType::Wildcard => "wildcard",
            ImportType::Relative => "relative",
        }
    }

    /// Parse from string
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "module" => Some(ImportType::Module),
            "from" => Some(ImportType::From),
            "wildcard" | "star" => Some(ImportType::Wildcard),
            "relative" => Some(ImportType::Relative),
            _ => None,
        }
    }
}

impl std::fmt::Display for ImportType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl ImportEdge {
    /// Create a new import edge
    ///
    /// # Example
    ///
    /// ```
    /// use ranex_core::{ImportEdge, ImportType};
    ///
    /// let edge = ImportEdge::new(
    ///     "app/main.py",
    ///     "app/utils.py",
    ///     "calculate_total",
    ///     ImportType::From,
    ///     10,
    /// );
    ///
    /// assert_eq!(edge.source_file, "app/main.py");
    /// assert_eq!(edge.import_name, "calculate_total");
    /// ```
    pub fn new(
        source_file: impl Into<String>,
        target_file: impl Into<String>,
        import_name: impl Into<String>,
        import_type: ImportType,
        line_number: usize,
    ) -> Self {
        Self {
            source_file: source_file.into(),
            target_file: target_file.into(),
            import_name: import_name.into(),
            import_type,
            line_number,
            alias: None,
            is_wildcard: matches!(import_type, ImportType::Wildcard),
        }
    }

    /// Builder method to add alias
    pub fn with_alias(mut self, alias: impl Into<String>) -> Self {
        self.alias = Some(alias.into());
        self
    }

    /// Create a wildcard import edge
    pub fn wildcard(
        source_file: impl Into<String>,
        target_file: impl Into<String>,
        import_name: impl Into<String>,
        line_number: usize,
    ) -> Self {
        Self {
            source_file: source_file.into(),
            target_file: target_file.into(),
            import_name: import_name.into(),
            import_type: ImportType::Wildcard,
            line_number,
            alias: None,
            is_wildcard: true,
        }
    }
}

impl Artifact {
    /// Create a new artifact with required fields
    ///
    /// # Example
    ///
    /// ```
    /// use ranex_core::{Artifact, ArtifactKind};
    ///
    /// let artifact = Artifact::new(
    ///     "calculate_tax",
    ///     "app.utils.tax.calculate_tax",
    ///     ArtifactKind::Function,
    ///     "app/utils/tax.py",
    ///     "app.utils.tax",
    ///     10,
    ///     25,
    /// )
    /// .with_signature("(amount: float) -> float")
    /// .with_docstring("Calculate tax on amount")
    /// .with_tag("billing");
    ///
    /// assert_eq!(artifact.symbol_name, "calculate_tax");
    /// assert_eq!(artifact.kind, ArtifactKind::Function);
    /// assert!(artifact.signature.is_some());
    /// ```
    pub fn new(
        symbol_name: impl Into<String>,
        qualified_name: impl Into<String>,
        kind: ArtifactKind,
        file_path: impl Into<PathBuf>,
        module_path: impl Into<String>,
        line_start: usize,
        line_end: usize,
    ) -> Self {
        Self {
            symbol_name: symbol_name.into(),
            qualified_name: qualified_name.into(),
            kind,
            file_path: file_path.into(),
            module_path: module_path.into(),
            signature: None,
            docstring: None,
            feature: None,
            tags: Vec::new(),
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
            line_start,
            line_end,
            hash: None,
        }
    }

    /// Builder method to add signature
    pub fn with_signature(mut self, signature: impl Into<String>) -> Self {
        self.signature = Some(signature.into());
        self
    }

    /// Builder method to add docstring
    pub fn with_docstring(mut self, docstring: impl Into<String>) -> Self {
        self.docstring = Some(docstring.into());
        self
    }

    /// Builder method to add feature
    pub fn with_feature(mut self, feature: impl Into<String>) -> Self {
        self.feature = Some(feature.into());
        self
    }

    /// Builder method to add tags
    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }

    /// Builder method to add a single tag
    pub fn with_tag(mut self, tag: impl Into<String>) -> Self {
        self.tags.push(tag.into());
        self
    }

    /// Builder method to set HTTP method.
    pub fn with_http_method(mut self, method: impl Into<String>) -> Self {
        self.http_method = Some(method.into());
        self
    }

    /// Builder method to set route path.
    pub fn with_route_path(mut self, route: impl Into<String>) -> Self {
        self.route_path = Some(route.into());
        self
    }

    /// Builder method to set router prefix.
    pub fn with_router_prefix(mut self, prefix: impl Into<String>) -> Self {
        self.router_prefix = Some(prefix.into());
        self
    }

    /// Builder method to set direct dependencies.
    pub fn with_direct_dependencies(mut self, deps: Vec<String>) -> Self {
        self.direct_dependencies = deps;
        self
    }

    /// Builder method to set dependency chain.
    pub fn with_dependency_chain(mut self, chain: Vec<String>) -> Self {
        self.dependency_chain = chain;
        self
    }

    /// Builder method to set security dependencies.
    pub fn with_security_dependencies(mut self, deps: Vec<String>) -> Self {
        self.security_dependencies = deps;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_artifact_builder() {
        let artifact = Artifact::new(
            "calculate_tax",
            "app.utils.tax.calculate_tax",
            ArtifactKind::Function,
            "app/utils/tax.py",
            "app.utils.tax",
            10,
            25,
        )
        .with_signature("(amount: float, rate: float) -> float")
        .with_docstring("Calculate tax on an amount")
        .with_feature("billing")
        .with_tag("utility");

        assert_eq!(artifact.symbol_name, "calculate_tax");
        assert_eq!(artifact.kind, ArtifactKind::Function);
        assert!(artifact.signature.is_some());
        assert_eq!(artifact.tags, vec!["utility"]);
    }

    #[test]
    fn test_artifact_kind_roundtrip() {
        for kind in [
            ArtifactKind::Function,
            ArtifactKind::Class,
            ArtifactKind::Endpoint,
            ArtifactKind::Contract,
        ] {
            let s = kind.as_str();
            let parsed = ArtifactKind::parse(s);
            assert_eq!(parsed, Some(kind));
        }
    }

    #[test]
    fn test_scan_stats() {
        let mut stats = ScanStats::new();
        stats.add_artifact(ArtifactKind::Function);
        stats.add_artifact(ArtifactKind::Function);
        stats.add_artifact(ArtifactKind::Class);

        assert_eq!(stats.artifacts_found, 3);
        assert_eq!(stats.artifacts_by_kind.get("function"), Some(&2));
        assert_eq!(stats.artifacts_by_kind.get("class"), Some(&1));
    }

    #[test]
    fn test_import_edge_builder() {
        let edge = ImportEdge::new(
            "app/main.py",
            "app/utils.py",
            "calculate_total",
            ImportType::From,
            10,
        )
        .with_alias("calc");

        assert_eq!(edge.source_file, "app/main.py");
        assert_eq!(edge.target_file, "app/utils.py");
        assert_eq!(edge.import_name, "calculate_total");
        assert_eq!(edge.alias, Some("calc".to_string()));
        assert!(!edge.is_wildcard);
    }

    #[test]
    fn test_import_edge_wildcard() {
        let edge = ImportEdge::wildcard("app/main.py", "app/utils.py", "*", 15);

        assert!(edge.is_wildcard);
        assert_eq!(edge.import_name, "*");
        assert_eq!(edge.import_type, ImportType::Wildcard);
    }

    #[test]
    fn test_import_type_roundtrip() {
        for import_type in [ImportType::Module, ImportType::From] {
            let s = import_type.as_str();
            let parsed = ImportType::parse(s);
            assert_eq!(parsed, Some(import_type));
        }
    }

    #[test]
    fn test_import_type_parse_invalid() {
        assert_eq!(ImportType::parse("invalid"), None);
        assert_eq!(ImportType::parse(""), None);
    }

    #[test]
    fn test_file_status_as_str() {
        assert_eq!(FileStatus::Success.as_str(), "success");
        assert_eq!(FileStatus::Failed.as_str(), "failed");
        assert_eq!(FileStatus::Skipped.as_str(), "skipped");
    }

    #[test]
    fn test_artifact_kind_parse_case_insensitive() {
        assert_eq!(
            ArtifactKind::parse("FUNCTION"),
            Some(ArtifactKind::Function)
        );
        assert_eq!(ArtifactKind::parse("Class"), Some(ArtifactKind::Class));
        assert_eq!(
            ArtifactKind::parse("endpoint"),
            Some(ArtifactKind::Endpoint)
        );
    }

    #[test]
    fn test_artifact_kind_parse_invalid() {
        assert_eq!(ArtifactKind::parse("invalid"), None);
        assert_eq!(ArtifactKind::parse(""), None);
    }

    #[test]
    fn test_artifact_with_multiple_tags() {
        let artifact = Artifact::new(
            "process_payment",
            "app.billing.process_payment",
            ArtifactKind::Function,
            "app/billing.py",
            "app.billing",
            10,
            30,
        )
        .with_tag("billing")
        .with_tag("payment")
        .with_tag("critical");

        assert_eq!(artifact.tags, vec!["billing", "payment", "critical"]);
    }

    #[test]
    fn test_artifact_with_tags_batch() {
        let artifact = Artifact::new(
            "validate_user",
            "app.auth.validate_user",
            ArtifactKind::Function,
            "app/auth.py",
            "app.auth",
            5,
            15,
        )
        .with_tags(vec!["auth".to_string(), "security".to_string()]);

        assert_eq!(artifact.tags, vec!["auth", "security"]);
    }

    #[test]
    fn test_scan_stats_default() {
        let stats = ScanStats::default();
        assert_eq!(stats.artifacts_found, 0);
        assert_eq!(stats.files_scanned, 0);
        assert_eq!(stats.files_parsed, 0);
    }

    // =========================================================================
    // Property-Based Tests (RUST-TESTING.md Section 7)
    // =========================================================================

    #[cfg(test)]
    mod property_tests {
        use super::*;
        use proptest::prelude::*;

        proptest! {
            /// Property: ArtifactKind serialization roundtrip always succeeds
            #[test]
            fn artifact_kind_roundtrip(kind in any::<ArtifactKind>()) {
                let serialized = kind.as_str();
                let deserialized = ArtifactKind::parse(serialized);
                prop_assert_eq!(deserialized, Some(kind));
            }

            /// Property: ImportType serialization roundtrip always succeeds
            #[test]
            fn import_type_roundtrip(import_type in any::<ImportType>()) {
                let serialized = import_type.as_str();
                let deserialized = ImportType::parse(serialized);
                prop_assert_eq!(deserialized, Some(import_type));
            }

            /// Property: Artifact builder never panics with any valid inputs
            #[test]
            fn artifact_builder_never_panics(
                name in "[a-z_][a-z0-9_]{0,50}",
                line_start in 1usize..1000,
                line_end in 1usize..1000,
            ) {
                let artifact = Artifact::new(
                    &name,
                    format!("module.{}", name),
                    ArtifactKind::Function,
                    "test.py",
                    "module",
                    line_start,
                    line_end.max(line_start), // Ensure line_end >= line_start
                );

                prop_assert_eq!(artifact.symbol_name, name);
                prop_assert!(artifact.line_start <= artifact.line_end);
            }

            /// Property: ImportEdge creation never panics with any inputs
            #[test]
            fn import_edge_never_panics(
                source in "[a-z/._]{1,50}",
                target in "[a-z/._]{1,50}",
                name in "[a-z_][a-z0-9_]{0,30}",
                line in 1usize..10000,
            ) {
                let edge = ImportEdge::new(
                    &source,
                    &target,
                    &name,
                    ImportType::From,
                    line,
                );

                prop_assert_eq!(edge.source_file, source);
                prop_assert_eq!(edge.target_file, target);
                prop_assert_eq!(edge.import_name, name);
            }

            /// Property: Adding artifacts to stats always increases count
            #[test]
            fn scan_stats_always_increases(kinds in prop::collection::vec(any::<ArtifactKind>(), 0..100)) {
                let mut stats = ScanStats::new();
                let initial_count = stats.artifacts_found;

                for kind in &kinds {
                    stats.add_artifact(*kind);
                }

                prop_assert_eq!(stats.artifacts_found, initial_count + kinds.len());
            }
        }
    }
}
