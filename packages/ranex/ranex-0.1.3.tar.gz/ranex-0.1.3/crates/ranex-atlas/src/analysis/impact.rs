//! Impact analysis for code changes.
//!
//! Predicts the blast radius of changing a specific function, class, or file.
//! Uses both call graph (function-level) and dependency graph (file-level)
//! to provide comprehensive impact assessment.
//!
//! ## Risk Scoring
//!
//! Impact is scored based on:
//! - **Direct callers**: Functions that directly call the changed code
//! - **Transitive callers**: Functions that indirectly depend on it
//! - **API exposure**: Whether the change affects public endpoints
//! - **Test coverage**: Whether affected code has tests
//!
//! ## Example
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::{ImpactAnalyzer, CallGraph, DependencyGraph};
//!
//! let analyzer = ImpactAnalyzer::new(&call_graph, &dependency_graph);
//! let report = analyzer.analyze_function("app.services.orders.get_order")?;
//!
//! println!("Risk level: {:?}", report.risk_level);
//! for affected in &report.affected_items {
//!     println!("  {} ({})", affected.qualified_name, affected.impact_type);
//! }
//! ```

use super::{CallGraph, DependencyGraph};
use ranex_core::Artifact;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// Risk level of a change.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ImpactLevel {
    /// No external impact (internal refactor).
    None,
    /// Low impact (few internal callers).
    Low,
    /// Medium impact (multiple callers or some API exposure).
    Medium,
    /// High impact (public API, many callers, or critical path).
    High,
    /// Critical impact (breaking change to widely-used API).
    Critical,
}

impl ImpactLevel {
    /// Convert to string for display.
    pub fn as_str(&self) -> &'static str {
        match self {
            ImpactLevel::None => "none",
            ImpactLevel::Low => "low",
            ImpactLevel::Medium => "medium",
            ImpactLevel::High => "high",
            ImpactLevel::Critical => "critical",
        }
    }

    /// Parse from string.
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "none" => Some(ImpactLevel::None),
            "low" => Some(ImpactLevel::Low),
            "medium" => Some(ImpactLevel::Medium),
            "high" => Some(ImpactLevel::High),
            "critical" => Some(ImpactLevel::Critical),
            _ => None,
        }
    }
}

impl std::fmt::Display for ImpactLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Type of impact on an affected item.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ImpactType {
    /// Direct caller of the changed function.
    DirectCaller,
    /// Transitive (indirect) caller.
    TransitiveCaller,
    /// File that imports the changed file.
    DirectImporter,
    /// File that transitively depends on the changed file.
    TransitiveImporter,
    /// Test file that covers the changed code.
    TestCoverage,
    /// API endpoint that exposes the changed code.
    ApiExposure,
}

impl ImpactType {
    pub fn as_str(&self) -> &'static str {
        match self {
            ImpactType::DirectCaller => "direct_caller",
            ImpactType::TransitiveCaller => "transitive_caller",
            ImpactType::DirectImporter => "direct_importer",
            ImpactType::TransitiveImporter => "transitive_importer",
            ImpactType::TestCoverage => "test_coverage",
            ImpactType::ApiExposure => "api_exposure",
        }
    }
}

impl std::fmt::Display for ImpactType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// An item affected by a change.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AffectedItem {
    /// Qualified name of the affected function/class, or file path.
    pub qualified_name: String,

    /// File path where this item is defined.
    pub file_path: String,

    /// Type of impact.
    pub impact_type: ImpactType,

    /// Distance from the changed code (1 = direct, 2+ = transitive).
    pub distance: usize,

    /// Line number if applicable.
    pub line_number: Option<usize>,

    /// HTTP method if this affected item is an endpoint.
    #[serde(default)]
    pub http_method: Option<String>,

    /// HTTP route path if this affected item is an endpoint.
    #[serde(default)]
    pub route_path: Option<String>,

    /// Router prefix if known for the endpoint.
    #[serde(default)]
    pub router_prefix: Option<String>,

    /// Tags carried from the artifact (e.g., fastapi_route, http_get).
    #[serde(default)]
    pub tags: Vec<String>,
}

impl AffectedItem {
    pub fn new(
        qualified_name: impl Into<String>,
        file_path: impl Into<String>,
        impact_type: ImpactType,
        distance: usize,
    ) -> Self {
        Self {
            qualified_name: qualified_name.into(),
            file_path: file_path.into(),
            impact_type,
            distance,
            line_number: None,
            http_method: None,
            route_path: None,
            router_prefix: None,
            tags: Vec::new(),
        }
    }

    /// Builder method to add line number.
    pub fn with_line(mut self, line: usize) -> Self {
        self.line_number = Some(line);
        self
    }
}

/// Complete impact analysis report.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImpactReport {
    /// The function or file being analyzed.
    pub target: String,

    /// Overall risk level.
    pub risk_level: ImpactLevel,

    /// All affected items.
    pub affected_items: Vec<AffectedItem>,

    /// Summary statistics.
    pub stats: ImpactStats,

    /// Human-readable summary.
    pub summary: String,
}

/// Statistics from impact analysis.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ImpactStats {
    /// Number of direct callers.
    pub direct_callers: usize,

    /// Number of transitive callers.
    pub transitive_callers: usize,

    /// Number of direct importers (file level).
    pub direct_importers: usize,

    /// Number of transitive importers.
    pub transitive_importers: usize,

    /// Number of test files affected.
    pub test_files: usize,

    /// Number of API endpoints affected.
    pub api_endpoints: usize,
}

/// Analyzer for change impact.
pub struct ImpactAnalyzer<'a> {
    call_graph: &'a CallGraph,
    dependency_graph: &'a DependencyGraph,
    artifacts: Option<&'a [Artifact]>,
    max_depth: usize,
}

impl<'a> ImpactAnalyzer<'a> {
    /// Create a new impact analyzer.
    pub fn new(call_graph: &'a CallGraph, dependency_graph: &'a DependencyGraph) -> Self {
        Self {
            call_graph,
            dependency_graph,
            artifacts: None,
            max_depth: 10,
        }
    }

    /// Set artifacts for enhanced analysis (endpoint detection, etc.).
    pub fn with_artifacts(mut self, artifacts: &'a [Artifact]) -> Self {
        self.artifacts = Some(artifacts);
        self
    }

    /// Set maximum traversal depth.
    pub fn with_max_depth(mut self, depth: usize) -> Self {
        self.max_depth = depth;
        self
    }

    /// Analyze impact of changing a specific function.
    pub fn analyze_function(&self, qualified_name: &str) -> ImpactReport {
        let mut affected_items = Vec::new();
        let mut stats = ImpactStats::default();

        // Get direct callers
        let direct_callers = self.call_graph.get_callers(qualified_name);
        for caller in &direct_callers {
            let file_path = self.find_file_for_function(caller).unwrap_or_default();
            affected_items.push(AffectedItem::new(
                *caller,
                file_path,
                ImpactType::DirectCaller,
                1,
            ));
            stats.direct_callers += 1;
        }

        // Get transitive callers
        let transitive = self
            .call_graph
            .get_transitive_callers(qualified_name, self.max_depth);
        let direct_set: HashSet<&str> = direct_callers.into_iter().collect();

        for caller in transitive {
            if !direct_set.contains(caller.as_str()) {
                let file_path = self.find_file_for_function(&caller).unwrap_or_default();
                affected_items.push(AffectedItem::new(
                    caller,
                    file_path,
                    ImpactType::TransitiveCaller,
                    2, // Simplified - could calculate actual distance
                ));
                stats.transitive_callers += 1;
            }
        }

        // Check for test coverage
        if let Some(artifacts) = self.artifacts {
            for item in &affected_items {
                if item.file_path.contains("test_") || item.file_path.contains("_test.py") {
                    stats.test_files += 1;
                }
            }

            // Check for API endpoint exposure
            for artifact in artifacts.iter() {
                if artifact.kind == ranex_core::ArtifactKind::Endpoint {
                    // Check if this endpoint calls the target
                    if self
                        .call_graph
                        .get_transitive_callees(&artifact.qualified_name, self.max_depth)
                        .contains(&qualified_name.to_string())
                    {
                        let mut item = AffectedItem::new(
                            &artifact.qualified_name,
                            artifact.file_path.to_string_lossy(),
                            ImpactType::ApiExposure,
                            0,
                        );
                        item.http_method = artifact.http_method.clone();
                        item.route_path = artifact.route_path.clone();
                        item.router_prefix = artifact.router_prefix.clone();
                        item.tags = artifact.tags.clone();
                        affected_items.push(item);
                        stats.api_endpoints += 1;
                    }
                }
            }
        }

        // Calculate risk level
        let risk_level = self.calculate_risk_level(&stats);

        // Generate summary
        let summary = self.generate_summary(qualified_name, &stats, risk_level);

        ImpactReport {
            target: qualified_name.to_string(),
            risk_level,
            affected_items,
            stats,
            summary,
        }
    }

    /// Analyze impact of changing a file.
    pub fn analyze_file(&self, file_path: &str) -> ImpactReport {
        let mut affected_items = Vec::new();
        let mut stats = ImpactStats::default();

        // Get direct importers
        let direct_importers = self.dependency_graph.get_dependents(file_path);
        for importer in &direct_importers {
            affected_items.push(AffectedItem::new(
                *importer,
                *importer,
                ImpactType::DirectImporter,
                1,
            ));
            stats.direct_importers += 1;

            // Check if it's a test file
            if importer.contains("test_") || importer.contains("_test.py") {
                stats.test_files += 1;
            }
        }

        // Get transitive importers
        let transitive = self
            .dependency_graph
            .get_transitive_dependents(file_path, self.max_depth);
        let direct_set: HashSet<&str> = direct_importers.into_iter().collect();

        for importer in transitive {
            if !direct_set.contains(importer.as_str()) {
                if importer.contains("test_") || importer.contains("_test.py") {
                    stats.test_files += 1;
                }
                affected_items.push(AffectedItem::new(
                    &importer,
                    &importer,
                    ImpactType::TransitiveImporter,
                    2,
                ));
                stats.transitive_importers += 1;
            }
        }

        // Calculate risk level
        let risk_level = self.calculate_risk_level(&stats);

        // Generate summary
        let summary = self.generate_file_summary(file_path, &stats, risk_level);

        ImpactReport {
            target: file_path.to_string(),
            risk_level,
            affected_items,
            stats,
            summary,
        }
    }

    /// Find the file path for a function by its qualified name.
    fn find_file_for_function(&self, qualified_name: &str) -> Option<String> {
        // Try to get from call graph edges
        for edge in self.call_graph.edges() {
            if edge.caller == qualified_name || edge.callee == qualified_name {
                return Some(edge.file_path.clone());
            }
        }

        // Try artifacts if available
        if let Some(artifacts) = self.artifacts {
            for artifact in artifacts {
                if artifact.qualified_name == qualified_name {
                    return Some(artifact.file_path.to_string_lossy().to_string());
                }
            }
        }

        None
    }

    /// Calculate risk level based on statistics.
    fn calculate_risk_level(&self, stats: &ImpactStats) -> ImpactLevel {
        let total_callers = stats.direct_callers + stats.transitive_callers;
        let total_importers = stats.direct_importers + stats.transitive_importers;

        // Critical: affects API endpoints
        if stats.api_endpoints > 0 {
            return ImpactLevel::Critical;
        }

        // High: many callers or importers
        if total_callers >= 10 || total_importers >= 10 {
            return ImpactLevel::High;
        }

        // Medium: some callers/importers
        if total_callers >= 3 || total_importers >= 3 {
            return ImpactLevel::Medium;
        }

        // Low: few callers
        if total_callers >= 1 || total_importers >= 1 {
            return ImpactLevel::Low;
        }

        ImpactLevel::None
    }

    /// Generate human-readable summary for function analysis.
    fn generate_summary(
        &self,
        target: &str,
        stats: &ImpactStats,
        risk_level: ImpactLevel,
    ) -> String {
        let mut parts = Vec::new();

        if stats.direct_callers > 0 {
            parts.push(format!("{} direct caller(s)", stats.direct_callers));
        }
        if stats.transitive_callers > 0 {
            parts.push(format!("{} transitive caller(s)", stats.transitive_callers));
        }
        if stats.test_files > 0 {
            parts.push(format!("{} test file(s)", stats.test_files));
        }
        if stats.api_endpoints > 0 {
            parts.push(format!("{} API endpoint(s)", stats.api_endpoints));
        }

        if parts.is_empty() {
            format!(
                "Change to '{}' has no detected impact ({})",
                target, risk_level
            )
        } else {
            format!(
                "Change to '{}' affects: {} [Risk: {}]",
                target,
                parts.join(", "),
                risk_level
            )
        }
    }

    /// Generate human-readable summary for file analysis.
    fn generate_file_summary(
        &self,
        target: &str,
        stats: &ImpactStats,
        risk_level: ImpactLevel,
    ) -> String {
        let mut parts = Vec::new();

        if stats.direct_importers > 0 {
            parts.push(format!("{} direct importer(s)", stats.direct_importers));
        }
        if stats.transitive_importers > 0 {
            parts.push(format!(
                "{} transitive importer(s)",
                stats.transitive_importers
            ));
        }
        if stats.test_files > 0 {
            parts.push(format!("{} test file(s)", stats.test_files));
        }

        if parts.is_empty() {
            format!(
                "Change to '{}' has no detected impact ({})",
                target, risk_level
            )
        } else {
            format!(
                "Change to '{}' affects: {} [Risk: {}]",
                target,
                parts.join(", "),
                risk_level
            )
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;

    fn build_test_graphs() -> (CallGraph, DependencyGraph) {
        let mut call_graph = CallGraph::new();
        let mut dep_graph = DependencyGraph::new();

        // Call graph: endpoint -> service -> repository
        call_graph.add_call(
            "app.api.get_order",
            "app.service.OrderService.get_order",
            super::super::CallType::Direct,
            10,
            "app/api.py",
        );
        call_graph.add_call(
            "app.service.OrderService.get_order",
            "app.repo.OrderRepo.find",
            super::super::CallType::Direct,
            20,
            "app/service.py",
        );

        // Dependency graph
        use ranex_core::{ImportEdge, ImportType};
        dep_graph.add_edge(ImportEdge::new(
            "app/api.py",
            "app/service.py",
            "app.service",
            ImportType::From,
            1,
        ));
        dep_graph.add_edge(ImportEdge::new(
            "app/service.py",
            "app/repo.py",
            "app.repo",
            ImportType::From,
            1,
        ));
        dep_graph.add_edge(ImportEdge::new(
            "tests/test_service.py",
            "app/service.py",
            "app.service",
            ImportType::From,
            1,
        ));

        (call_graph, dep_graph)
    }

    #[test]
    fn test_analyze_function() {
        let (call_graph, dep_graph) = build_test_graphs();
        let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph);

        let report = analyzer.analyze_function("app.repo.OrderRepo.find");

        assert!(report.stats.direct_callers >= 1);
        assert!(!report.affected_items.is_empty());
    }

    #[test]
    fn test_analyze_file() {
        let (call_graph, dep_graph) = build_test_graphs();
        let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph);

        let report = analyzer.analyze_file("app/service.py");

        // api.py and tests/test_service.py import service.py
        assert!(report.stats.direct_importers >= 1);
        assert!(report.stats.test_files >= 1);
    }

    #[test]
    fn test_risk_level_calculation() {
        let (call_graph, dep_graph) = build_test_graphs();
        let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph);

        // Low risk - few callers
        let report = analyzer.analyze_function("app.repo.OrderRepo.find");
        assert!(report.risk_level <= ImpactLevel::Medium);
    }

    #[test]
    fn test_impact_level_ordering() {
        assert!(ImpactLevel::None < ImpactLevel::Low);
        assert!(ImpactLevel::Low < ImpactLevel::Medium);
        assert!(ImpactLevel::Medium < ImpactLevel::High);
        assert!(ImpactLevel::High < ImpactLevel::Critical);
    }

    #[test]
    fn test_api_exposure_carries_http_metadata() -> Result<(), Box<dyn Error>> {
        let (call_graph, dep_graph) = build_test_graphs();
        // Create a fake endpoint artifact with HTTP metadata
        let endpoint_artifact = ranex_core::Artifact::new(
            "get_order",
            "app.api.get_order",
            ranex_core::ArtifactKind::Endpoint,
            "app/api.py",
            "app.api",
            5,
            15,
        )
        .with_http_method("get")
        .with_route_path("/orders/{order_id}")
        .with_router_prefix("/api/v1")
        .with_tag("fastapi_route")
        .with_tag("http_get");

        let artifacts = [endpoint_artifact];

        // Analyzer with artifacts containing the endpoint
        let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph)
            .with_artifacts(&artifacts)
            .with_max_depth(5);

        // Target is the repository function; endpoint calls it transitively
        let report = analyzer.analyze_function("app.repo.OrderRepo.find");

        let api_item = report
            .affected_items
            .iter()
            .find(|i| i.impact_type == ImpactType::ApiExposure)
            .ok_or_else(|| {
                std::io::Error::new(std::io::ErrorKind::NotFound, "expected ApiExposure item")
            })?;

        assert_eq!(api_item.http_method.as_deref(), Some("get"));
        assert_eq!(api_item.route_path.as_deref(), Some("/orders/{order_id}"));
        assert_eq!(api_item.router_prefix.as_deref(), Some("/api/v1"));
        assert!(api_item.tags.contains(&"fastapi_route".to_string()));
        assert!(api_item.tags.contains(&"http_get".to_string()));
        Ok(())
    }
}
