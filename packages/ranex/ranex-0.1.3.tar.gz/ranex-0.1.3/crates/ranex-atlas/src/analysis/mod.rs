//! Analysis subsystem for Atlas.
//!
//! This module provides advanced code analysis capabilities:
//!
//! - **Call Graph**: Tracks function-to-function call relationships
//! - **Impact Analysis**: Predicts change impact across the codebase
//! - **Pattern Detection**: Identifies common code patterns (CRUD, Repository, etc.)
//! - **Duplicate Detection**: Finds similar code blocks for DRY enforcement
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
//! │  Call Graph │───▶│   Impact    │───▶│  Patterns   │
//! │  Extraction │    │  Analysis   │    │  Detection  │
//! └─────────────┘    └─────────────┘    └─────────────┘
//!       │                   │                  │
//!       ▼                   ▼                  ▼
//!   Parse AST for      Use call graph     Match against
//!   function calls     + imports for      known patterns
//!                      impact scoring
//! ```
//!
//! ## Usage
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::{CallGraph, ImpactAnalyzer, PatternDetector};
//!
//! // Build call graph during scan
//! let mut call_graph = CallGraph::new();
//! call_graph.extract_from_ast(&parsed_ast)?;
//!
//! // Analyze impact of a change
//! let analyzer = ImpactAnalyzer::new(&call_graph, &imports);
//! let impact = analyzer.analyze("app/services/orders.py", "get_order")?;
//!
//! // Detect patterns
//! let detector = PatternDetector::new(&artifacts);
//! let patterns = detector.detect_all()?;
//! ```

pub mod call_graph;
pub mod dependency_graph;
pub mod duplicates;
pub mod fastapi_dependencies;
pub mod fastapi_scaling;
pub mod fastapi_router_topology;
pub mod impact;
pub mod patterns;

// Re-export main types
pub use call_graph::{CallEdge, CallGraph, CallType};
pub use dependency_graph::{DependencyGraph, DependencyNode};
pub use duplicates::{
    DuplicateDetector, DuplicateDetectorConfig, DuplicateMatch, MatchType, SimilarityScore,
};
pub use fastapi_scaling::{
    analyze_definitions, FastapiScalingPolicy, FastapiScalingReport, ParsedDefinition,
    ScalingStats, ScalingViolation, ScopeKind, ScalingSeverity,
};
pub use fastapi_router_topology::{analyze_router_topology, RouterTopologyReport, RouteInfo, RouterInfo};
pub use impact::{AffectedItem, ImpactAnalyzer, ImpactLevel, ImpactReport};
pub use patterns::{DetectedPattern, PatternConfidence, PatternDetector, PatternType};

pub mod fastapi_truth_capsule;
pub use fastapi_truth_capsule::{
    CapsuleEndpoint,
    CapsuleGroups,
    CapsuleStats,
    FastapiTruthCapsuleRequest,
    SpanGroupEntry,
    TruthCapsule,
    TruthCapsuleSpan,
    UnresolvedEdge,
};
