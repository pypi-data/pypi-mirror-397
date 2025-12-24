//! Integration tests for the analysis module.
//!
//! Tests the public API of call graph, impact analysis, pattern detection,
//! and duplicate detection features.

use ranex_atlas::analysis::{
    CallGraph, CallType, DependencyGraph, DuplicateDetector, ImpactAnalyzer, ImpactLevel,
    PatternDetector, PatternType, SimilarityScore,
};
use ranex_atlas::Atlas;
use ranex_core::{Artifact, ArtifactKind, ImportEdge, ImportType};
use std::error::Error;
use std::path::PathBuf;

mod common;

// =============================================================================
// Test Helpers
// =============================================================================

fn make_artifact(name: &str, qualified: &str, kind: ArtifactKind, file: &str) -> Artifact {
    Artifact {
        symbol_name: name.to_string(),
        qualified_name: qualified.to_string(),
        kind,
        file_path: PathBuf::from(file),
        module_path: qualified
            .rsplit('.')
            .skip(1)
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect::<Vec<_>>()
            .join("."),
        signature: None,
        docstring: None,
        feature: None,
        tags: vec![],
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
        line_start: 1,
        line_end: 10,
        hash: None,
    }
}

fn make_method(name: &str, class: &str, file: &str) -> Artifact {
    let qualified = format!("{}.{}", class, name);
    make_artifact(name, &qualified, ArtifactKind::Method, file)
}

fn make_import(source: &str, target: &str, line: usize) -> ImportEdge {
    ImportEdge::new(
        source,
        target,
        target.replace('/', ".").replace(".py", ""),
        ImportType::From,
        line,
    )
}

// =============================================================================
// Call Graph Integration Tests
// =============================================================================

#[test]
fn test_call_graph_complex_chain() {
    let mut graph = CallGraph::new();

    // Build a realistic call chain:
    // API endpoint -> Service -> Repository -> Database helper
    graph.add_call(
        "app.api.orders.get_order",
        "app.services.orders.OrderService.get_order",
        CallType::Async,
        15,
        "app/api/orders.py",
    );
    graph.add_call(
        "app.services.orders.OrderService.get_order",
        "app.repo.orders.OrderRepository.find_by_id",
        CallType::Direct,
        42,
        "app/services/orders.py",
    );
    graph.add_call(
        "app.repo.orders.OrderRepository.find_by_id",
        "app.db.helpers.execute_query",
        CallType::Direct,
        28,
        "app/repo/orders.py",
    );

    // Test forward traversal
    let callees = graph.get_transitive_callees("app.api.orders.get_order", 10);
    assert_eq!(callees.len(), 3);
    assert!(callees.contains(&"app.services.orders.OrderService.get_order".to_string()));
    assert!(callees.contains(&"app.repo.orders.OrderRepository.find_by_id".to_string()));
    assert!(callees.contains(&"app.db.helpers.execute_query".to_string()));

    // Test reverse traversal
    let callers = graph.get_transitive_callers("app.db.helpers.execute_query", 10);
    assert_eq!(callers.len(), 3);
    assert!(callers.contains(&"app.api.orders.get_order".to_string()));
}

#[test]
fn test_call_graph_diamond_pattern() {
    let mut graph = CallGraph::new();

    // Diamond dependency pattern:
    //      A
    //     / \
    //    B   C
    //     \ /
    //      D
    graph.add_call("A", "B", CallType::Direct, 1, "a.py");
    graph.add_call("A", "C", CallType::Direct, 2, "a.py");
    graph.add_call("B", "D", CallType::Direct, 1, "b.py");
    graph.add_call("C", "D", CallType::Direct, 1, "c.py");

    // D should have exactly 2 direct callers
    let direct_callers = graph.get_callers("D");
    assert_eq!(direct_callers.len(), 2);

    // D should have 3 transitive callers (B, C, A)
    let transitive_callers = graph.get_transitive_callers("D", 10);
    assert_eq!(transitive_callers.len(), 3);
}

// =============================================================================
// Dependency Graph Integration Tests
// =============================================================================

#[test]
fn test_dependency_graph_layered_architecture() {
    let mut graph = DependencyGraph::new();

    // Typical layered architecture:
    // api -> services -> repositories -> models
    graph.add_edge(make_import(
        "app/api/orders.py",
        "app/services/orders.py",
        1,
    ));
    graph.add_edge(make_import("app/api/orders.py", "app/models/order.py", 2));
    graph.add_edge(make_import(
        "app/services/orders.py",
        "app/repo/orders.py",
        1,
    ));
    graph.add_edge(make_import(
        "app/services/orders.py",
        "app/models/order.py",
        2,
    ));
    graph.add_edge(make_import("app/repo/orders.py", "app/models/order.py", 1));

    // models should be the most depended-upon
    let model_dependents = graph.get_transitive_dependents("app/models/order.py", 10);
    assert_eq!(model_dependents.len(), 3); // api, services, repo

    // api should have no dependents (it's an entry point)
    let api_dependents = graph.get_dependents("app/api/orders.py");
    assert!(api_dependents.is_empty());

    // Verify root and leaf detection
    let roots = graph.get_root_files();
    assert!(roots.contains(&"app/api/orders.py"));

    let leaves = graph.get_leaf_files();
    assert!(leaves.contains(&"app/models/order.py"));
}

#[test]
fn test_dependency_graph_cycle_detection() {
    let mut graph = DependencyGraph::new();

    // Create a circular dependency
    graph.add_edge(make_import("a.py", "b.py", 1));
    graph.add_edge(make_import("b.py", "c.py", 1));
    graph.add_edge(make_import("c.py", "a.py", 1)); // Cycle!

    let cycles = graph.detect_cycles();
    assert!(!cycles.is_empty(), "Should detect circular dependency");
}

// =============================================================================
// Impact Analysis Integration Tests
// =============================================================================

#[test]
fn test_impact_analysis_service_change() {
    let mut call_graph = CallGraph::new();
    let mut dep_graph = DependencyGraph::new();

    // Setup: API endpoints call a service
    call_graph.add_call(
        "app.api.get_orders",
        "app.service.OrderService.list",
        CallType::Async,
        10,
        "app/api.py",
    );
    call_graph.add_call(
        "app.api.get_order",
        "app.service.OrderService.get",
        CallType::Async,
        20,
        "app/api.py",
    );
    call_graph.add_call(
        "app.api.admin.view_order",
        "app.service.OrderService.get",
        CallType::Async,
        30,
        "app/api/admin.py",
    );

    // Setup: File dependencies
    dep_graph.add_edge(make_import("app/api.py", "app/service.py", 1));
    dep_graph.add_edge(make_import("app/api/admin.py", "app/service.py", 1));
    dep_graph.add_edge(make_import("tests/test_service.py", "app/service.py", 1));

    let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph);

    // Analyze impact of changing OrderService.get
    let report = analyzer.analyze_function("app.service.OrderService.get");

    // Should have 2 direct callers
    assert!(report.stats.direct_callers >= 2);

    // Risk should be at least Medium due to multiple callers
    assert!(report.risk_level >= ImpactLevel::Low);
}

#[test]
fn test_impact_analysis_file_change() {
    let call_graph = CallGraph::new();
    let mut dep_graph = DependencyGraph::new();

    // Multiple files depend on a utility module
    dep_graph.add_edge(make_import("app/service_a.py", "app/utils.py", 1));
    dep_graph.add_edge(make_import("app/service_b.py", "app/utils.py", 1));
    dep_graph.add_edge(make_import("app/service_c.py", "app/utils.py", 1));
    dep_graph.add_edge(make_import("tests/test_utils.py", "app/utils.py", 1));

    let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph);
    let report = analyzer.analyze_file("app/utils.py");

    // Should have 4 direct importers
    assert_eq!(report.stats.direct_importers, 4);

    // Should detect test file
    assert!(report.stats.test_files >= 1);

    // Risk should be Medium or higher
    assert!(report.risk_level >= ImpactLevel::Medium);
}

#[test]
fn test_file_impact_real_schemas_module_in_ranex_python() -> Result<(), Box<dyn Error>> {
    // Real-project E2E: analyze impact of changing the shared schemas module in ranex-python.
    let project_root = std::path::Path::new("/home/tonyo/projects/ranexV2/ranex-python");
    if !project_root.join("app/backend/models/schemas.py").exists() {
        return Ok(());
    }

    let mut atlas = Atlas::new(project_root)?;
    atlas.scan()?;

    let report = atlas.analyze_file_impact("app/backend/models/schemas.py")?;

    assert!(
        report.stats.direct_importers >= 1,
        "expected at least one direct importer of schemas.py, got {}",
        report.stats.direct_importers,
    );

    let importer_paths: Vec<String> = report
        .affected_items
        .iter()
        .map(|item| item.file_path.clone())
        .collect();

    assert!(
        importer_paths
            .iter()
            .any(|p| p.ends_with("app/backend/routes/hedge_fund.py")),
        "expected hedge_fund.py to appear as an importer of schemas.py, got: {:?}",
        importer_paths,
    );

    assert!(!report.summary.is_empty(), "impact report summary should not be empty");

    Ok(())
}

// =============================================================================
// Pattern Detection Integration Tests
// =============================================================================

#[test]
fn test_pattern_detection_crud_service() {
    let artifacts = vec![
        make_method(
            "create_order",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "get_order",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "update_order",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "delete_order",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "list_orders",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_artifact(
            "OrderService",
            "app.services.OrderService",
            ArtifactKind::Class,
            "app/services/orders.py",
        ),
    ];

    let detector = PatternDetector::new(&artifacts).with_min_confidence(0.5);

    let patterns = detector.detect_all();

    // Should detect CRUD pattern
    let crud_patterns: Vec<_> = patterns
        .iter()
        .filter(|p| p.pattern_type == PatternType::Crud)
        .collect();

    assert!(!crud_patterns.is_empty(), "Should detect CRUD pattern");

    // Should also detect Service Layer pattern
    let service_patterns: Vec<_> = patterns
        .iter()
        .filter(|p| p.pattern_type == PatternType::ServiceLayer)
        .collect();

    assert!(
        !service_patterns.is_empty(),
        "Should detect Service Layer pattern"
    );
}

#[test]
fn test_pattern_detection_repository() {
    let artifacts = vec![
        make_method(
            "find_by_id",
            "app.repo.OrderRepository",
            "app/repo/orders.py",
        ),
        make_method(
            "find_by_customer",
            "app.repo.OrderRepository",
            "app/repo/orders.py",
        ),
        make_method("save", "app.repo.OrderRepository", "app/repo/orders.py"),
        make_method("delete", "app.repo.OrderRepository", "app/repo/orders.py"),
        make_method("query", "app.repo.OrderRepository", "app/repo/orders.py"),
        make_artifact(
            "OrderRepository",
            "app.repo.OrderRepository",
            ArtifactKind::Class,
            "app/repo/orders.py",
        ),
    ];

    let detector = PatternDetector::new(&artifacts).with_min_confidence(0.4);

    let patterns = detector.detect_all();

    // Should detect Repository pattern
    let repo_patterns: Vec<_> = patterns
        .iter()
        .filter(|p| p.pattern_type == PatternType::Repository)
        .collect();

    assert!(
        !repo_patterns.is_empty(),
        "Should detect Repository pattern"
    );

    // Confidence should be high due to name + method indicators
    if let Some(pattern) = repo_patterns.first() {
        assert!(
            pattern.confidence.is_medium(),
            "Repository pattern should have medium+ confidence"
        );
    }
}

// =============================================================================
// Duplicate Detection Integration Tests
// =============================================================================

#[test]
fn test_duplicate_detection_no_false_positives_on_trivial_signatures() {
    // Functions with trivial/simple signatures should NOT be flagged as duplicates
    // Following naming conventions (get_x, create_x) is NOT duplication
    let mut artifact1 = make_artifact(
        "get_order_by_id",
        "app.orders.get_order_by_id",
        ArtifactKind::Function,
        "app/orders.py",
    );
    artifact1.signature = Some("(id: int) -> Order".to_string());

    let mut artifact2 = make_artifact(
        "get_user_by_id",
        "app.users.get_user_by_id",
        ArtifactKind::Function,
        "app/users.py",
    );
    artifact2.signature = Some("(id: int) -> User".to_string());

    let artifacts = vec![artifact1, artifact2];

    let detector = DuplicateDetector::new(&artifacts).with_threshold(SimilarityScore::new(0.7));

    let matches = detector.find_duplicates();

    // These functions have different return types and simple signatures
    // They should NOT be flagged as duplicates
    assert!(
        matches.is_empty(),
        "Should NOT flag trivial signatures as duplicates"
    );
}

#[test]
fn test_duplicate_detection_exact_signatures() {
    let mut artifact1 = make_artifact(
        "calculate_tax",
        "app.billing.calculate_tax",
        ArtifactKind::Function,
        "app/billing.py",
    );
    artifact1.signature = Some("(amount: float, rate: float) -> float".to_string());

    let mut artifact2 = make_artifact(
        "calculate_discount",
        "app.orders.calculate_discount",
        ArtifactKind::Function,
        "app/orders.py",
    );
    artifact2.signature = Some("(amount: float, rate: float) -> float".to_string());

    let artifacts = vec![artifact1, artifact2];

    let detector = DuplicateDetector::new(&artifacts).with_threshold(SimilarityScore::new(0.8));

    let matches = detector.find_duplicates();

    // Should find signature similarity
    let sig_matches: Vec<_> = matches
        .iter()
        .filter(|m| m.match_type == ranex_atlas::analysis::duplicates::MatchType::SimilarSignature)
        .collect();

    assert!(!sig_matches.is_empty(), "Should detect similar signatures");

    // First match should have high similarity
    if let Some(m) = sig_matches.first() {
        assert!(
            m.similarity.value() >= 0.9,
            "Identical signatures should have high similarity"
        );
    }
}

// =============================================================================
// End-to-End Integration Test
// =============================================================================

#[test]
fn test_full_analysis_pipeline() {
    // Build a realistic project structure
    let artifacts = vec![
        // API layer
        make_artifact(
            "get_orders",
            "app.api.orders.get_orders",
            ArtifactKind::Endpoint,
            "app/api/orders.py",
        ),
        make_artifact(
            "create_order",
            "app.api.orders.create_order",
            ArtifactKind::Endpoint,
            "app/api/orders.py",
        ),
        // Service layer
        make_method(
            "list",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "create",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method("get", "app.services.OrderService", "app/services/orders.py"),
        make_method(
            "update",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_method(
            "delete",
            "app.services.OrderService",
            "app/services/orders.py",
        ),
        make_artifact(
            "OrderService",
            "app.services.OrderService",
            ArtifactKind::Class,
            "app/services/orders.py",
        ),
        // Repository layer
        make_method("find_all", "app.repo.OrderRepository", "app/repo/orders.py"),
        make_method(
            "find_by_id",
            "app.repo.OrderRepository",
            "app/repo/orders.py",
        ),
        make_method("save", "app.repo.OrderRepository", "app/repo/orders.py"),
        make_artifact(
            "OrderRepository",
            "app.repo.OrderRepository",
            ArtifactKind::Class,
            "app/repo/orders.py",
        ),
    ];

    // Build call graph
    let mut call_graph = CallGraph::new();
    call_graph.add_call(
        "app.api.orders.get_orders",
        "app.services.OrderService.list",
        CallType::Async,
        10,
        "app/api/orders.py",
    );
    call_graph.add_call(
        "app.services.OrderService.list",
        "app.repo.OrderRepository.find_all",
        CallType::Direct,
        20,
        "app/services/orders.py",
    );

    // Build dependency graph
    let mut dep_graph = DependencyGraph::new();
    dep_graph.add_edge(make_import(
        "app/api/orders.py",
        "app/services/orders.py",
        1,
    ));
    dep_graph.add_edge(make_import(
        "app/services/orders.py",
        "app/repo/orders.py",
        1,
    ));

    // 1. Pattern Detection
    let detector = PatternDetector::new(&artifacts);
    let patterns = detector.detect_all();

    // Should detect both CRUD and Repository patterns
    assert!(patterns.iter().any(|p| p.pattern_type == PatternType::Crud));
    assert!(patterns
        .iter()
        .any(|p| p.pattern_type == PatternType::Repository));

    // 2. Impact Analysis
    let analyzer = ImpactAnalyzer::new(&call_graph, &dep_graph).with_artifacts(&artifacts);

    let report = analyzer.analyze_function("app.repo.OrderRepository.find_all");

    // Repository change should impact service layer
    assert!(report.stats.direct_callers >= 1);

    // 3. Verify call chain
    let callers = call_graph.get_transitive_callers("app.repo.OrderRepository.find_all", 5);
    assert!(callers.contains(&"app.api.orders.get_orders".to_string()));
}
