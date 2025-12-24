use crate::analysis::CallGraph;
use ranex_core::{Artifact, ArtifactKind, AtlasError};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};

/// Request parameters for building a FastAPI Truth Capsule.
///
/// Mirrors the JSON contract described in DOCS/Features/Atlas-System/TO-ADD.md §2.2.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FastapiTruthCapsuleRequest {
    /// HTTP method (e.g., "GET", "POST"). Optional for handler-based resolution.
    pub method: Option<String>,

    /// Concrete request path (e.g., "/v1/refunds/123"). Optional.
    pub path: Option<String>,

    /// FastAPI operation_id, if provided on the route decorator.
    pub operation_id: Option<String>,

    /// Fully qualified handler name (e.g., "app.api.refunds:create_refund").
    pub handler_qualified_name: Option<String>,

    /// Execution mode. For v1 this is always "static".
    pub mode: String,

    /// Strict mode: fail-closed when required edges cannot be proven.
    pub strict: bool,

    /// Maximum total spans to emit across all groups.
    pub max_spans: usize,

    /// Maximum depth when expanding dependency DAGs.
    pub max_dependency_depth: usize,

    /// Maximum depth when expanding call graph from the handler.
    pub max_call_depth: usize,

    /// Maximum number of distinct call graph nodes to include.
    pub max_call_nodes: usize,

    /// Whether to include source snippets for spans.
    pub include_snippets: bool,

    /// Maximum number of lines per snippet when include_snippets is true.
    pub snippet_max_lines: usize,
}

/// A concrete span of code in the project.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TruthCapsuleSpan {
    pub file_path: String,
    pub start_line: usize,
    pub end_line: usize,
    pub kind: String,
    pub symbol: Option<String>,
    pub hash: Option<String>,
    pub snippet: Option<String>,
}

/// A span annotated with evidence and a ranking score.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpanGroupEntry {
    pub span: TruthCapsuleSpan,
    pub evidence: Vec<String>,
    pub score: f32,
}

/// Resolved endpoint descriptor for the capsule.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CapsuleEndpoint {
    pub method: Option<String>,
    pub path_template: Option<String>,
    pub operation_id: Option<String>,
    pub handler_qualified_name: String,
}

/// Capsule statistics and timing information.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CapsuleStats {
    pub elapsed_ms: u64,
    pub db_queries: u64,
    pub files_read: u64,
    pub files_parsed: u64,
    pub cache_hit: bool,
}

/// A graph edge that could not be fully resolved in static mode.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnresolvedEdge {
    pub kind: String,
    pub detail: String,
    pub location: Option<String>,
}

/// Grouped spans by semantic role.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CapsuleGroups {
    pub route_wiring: Vec<SpanGroupEntry>,
    pub handler: Vec<SpanGroupEntry>,
    pub dependencies: Vec<SpanGroupEntry>,
    pub middleware: Vec<SpanGroupEntry>,
    pub exceptions: Vec<SpanGroupEntry>,
    pub schemas: Vec<SpanGroupEntry>,
    pub call_slice: Vec<SpanGroupEntry>,
    pub tests: Vec<SpanGroupEntry>,
}

/// Root Truth Capsule object.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TruthCapsule {
    pub capsule_id: String,
    pub resolved_by: String,
    pub mode: String,
    pub strict: bool,
    pub is_partial: bool,
    pub endpoint: CapsuleEndpoint,
    pub groups: CapsuleGroups,
    pub unresolved: Vec<UnresolvedEdge>,
    pub stats: CapsuleStats,
}

/// Build a FastAPI Truth Capsule from the current Atlas index.
///
/// This is a Phase 1 implementation stub. The full behavior described in
/// TO-ADD.md will be implemented incrementally.
pub fn build_truth_capsule(
    artifacts: &[Artifact],
    call_graph: &CallGraph,
    request: &FastapiTruthCapsuleRequest,
) -> Result<TruthCapsule, AtlasError> {
    // For Phase 1 we support only static analysis mode.
    if request.mode != "static" {
        return Err(AtlasError::unavailable(
            format!(
                "Unsupported Truth Capsule mode '{}'; only 'static' is implemented",
                request.mode
            ),
            false,
        ));
    }

    // Work with endpoint artifacts only; other kinds are ignored.
    let endpoint_artifacts: Vec<&Artifact> = artifacts
        .iter()
        .filter(|a| a.kind == ArtifactKind::Endpoint)
        .collect();

    if endpoint_artifacts.is_empty() {
        return Err(AtlasError::unavailable(
            "No FastAPI endpoint artifacts found in Atlas index",
            false,
        ));
    }

    let (endpoint, resolved_by) = resolve_endpoint(&endpoint_artifacts, request)?;

    // Build endpoint descriptor from the resolved artifact.
    let endpoint_desc = CapsuleEndpoint {
        method: endpoint
            .http_method
            .as_ref()
            .map(|m| m.to_uppercase()),
        path_template: endpoint.route_path.clone(),
        // Operation IDs are not currently extracted into Artifact; leave unset in v1.
        operation_id: None,
        handler_qualified_name: endpoint.qualified_name.clone(),
    };

    // Minimal handler group: one span covering the endpoint definition.
    let handler_span = TruthCapsuleSpan {
        file_path: endpoint.file_path.to_string_lossy().to_string(),
        start_line: endpoint.line_start,
        end_line: endpoint.line_end,
        kind: "handler".to_string(),
        symbol: Some(endpoint.qualified_name.clone()),
        hash: endpoint.hash.clone(),
        snippet: None,
    };

    let handler_entry = SpanGroupEntry {
        span: handler_span,
        evidence: vec!["ast:def".to_string()],
        score: 1.0,
    };

    let mut groups = CapsuleGroups::default();
    let mut unresolved: Vec<UnresolvedEdge> = Vec::new();

    let mut seen_spans: HashSet<(String, usize, usize, String, Option<String>)> = HashSet::new();
    let handler_key = (
        handler_entry.span.file_path.clone(),
        handler_entry.span.start_line,
        handler_entry.span.end_line,
        handler_entry.span.kind.clone(),
        handler_entry.span.symbol.clone(),
    );
    seen_spans.insert(handler_key);

    groups.handler.push(handler_entry);

    let (dep_entries, dep_unresolved) = build_dependency_group(
        endpoint,
        artifacts,
        request.max_dependency_depth,
        &mut seen_spans,
    );
    if !dep_entries.is_empty() {
        groups.dependencies.extend(dep_entries);
    }

    if !dep_unresolved.is_empty() {
        unresolved.extend(dep_unresolved);
    }

    let (schema_entries, schema_unresolved) = build_schema_group(
        endpoint,
        artifacts,
        &mut seen_spans,
    );
    if !schema_entries.is_empty() {
        groups.schemas.extend(schema_entries);
    }
    if !schema_unresolved.is_empty() {
        unresolved.extend(schema_unresolved);
    }

    let middleware_entries = build_middleware_group(artifacts, &mut seen_spans);
    if !middleware_entries.is_empty() {
        groups.middleware.extend(middleware_entries);
    }

    let mut artifacts_by_qualified: HashMap<String, &Artifact> = HashMap::new();
    let mut artifacts_by_symbol: HashMap<String, Vec<&Artifact>> = HashMap::new();
    for artifact in artifacts {
        artifacts_by_qualified.insert(artifact.qualified_name.clone(), artifact);
        artifacts_by_symbol
            .entry(artifact.symbol_name.clone())
            .or_default()
            .push(artifact);
    }

    let (exception_entries, exception_unresolved) = build_exceptions_group(
        endpoint,
        call_graph,
        &artifacts_by_qualified,
        &artifacts_by_symbol,
        request.max_call_depth,
        request.max_call_nodes,
        &mut seen_spans,
    );
    if !exception_entries.is_empty() {
        groups.exceptions.extend(exception_entries);
    }
    if !exception_unresolved.is_empty() {
        unresolved.extend(exception_unresolved);
    }

    let (call_slice_entries, call_unresolved) = build_call_slice_group(
        endpoint,
        call_graph,
        &artifacts_by_qualified,
        &artifacts_by_symbol,
        request.max_call_depth,
        request.max_call_nodes,
        &mut seen_spans,
    );
    if !call_slice_entries.is_empty() {
        groups.call_slice.extend(call_slice_entries);
    }
    if !call_unresolved.is_empty() {
        unresolved.extend(call_unresolved);
    }

    // Strict vs non-strict semantics for structural graph edges.
    let has_structural_unresolved = unresolved.iter().any(|e| {
        matches!(e.kind.as_str(), "dependency_edge" | "schema_edge" | "router_origin")
    });

    if request.strict && has_structural_unresolved {
        let count = unresolved
            .iter()
            .filter(|e| matches!(e.kind.as_str(), "dependency_edge" | "schema_edge" | "router_origin"))
            .count();

        return Err(AtlasError::unavailable(
            format!(
                "Truth Capsule strict mode failed: {} unresolved structural edges (dependencies/schemas/router). Use strict=false for a partial capsule.",
                count
            ),
            false,
        ));
    }

    let is_partial = !unresolved.is_empty();

    // Deterministic but simple capsule identifier; Phase 2 will
    // replace this with the SHA-based deps_hash/inputs_hash scheme
    // described in TO-ADD.md §8.
    let method_for_id = endpoint_desc
        .method
        .as_deref()
        .unwrap_or("");
    let path_for_id = endpoint_desc
        .path_template
        .as_deref()
        .unwrap_or("");
    let capsule_id = format!(
        "fastapi_capsule:{}:{}:{}",
        method_for_id, path_for_id, endpoint_desc.handler_qualified_name
    );

    let stats = CapsuleStats {
        elapsed_ms: 0,
        db_queries: 0,
        files_read: 0,
        files_parsed: 0,
        cache_hit: false,
    };

    Ok(TruthCapsule {
        capsule_id,
        resolved_by,
        mode: request.mode.clone(),
        strict: request.strict,
        is_partial,
        endpoint: endpoint_desc,
        groups,
        unresolved,
        stats,
    })
}

fn resolve_endpoint<'a>(
    endpoints: &'a [&'a Artifact],
    request: &FastapiTruthCapsuleRequest,
) -> Result<(&'a Artifact, String), AtlasError> {
    // Prefer handler_qualified_name if provided.
    if let Some(ref qname) = request.handler_qualified_name {
        if let Some(artifact) = endpoints
            .iter()
            .copied()
            .find(|a| &a.qualified_name == qname)
        {
            return Ok((artifact, "handler_qualified_name".to_string()));
        }

        return Err(AtlasError::unavailable(
            format!(
                "Handler qualified name '{}' did not resolve to a FastAPI endpoint",
                qname
            ),
            false,
        ));
    }

    // Fallback to (method, path) resolution if both are present.
    if let (Some(method), Some(path)) = (&request.method, &request.path) {
        let resolved = resolve_by_method_path(endpoints, method, path, request.strict)?;
        return Ok((resolved, "method_path".to_string()));
    }

    Err(AtlasError::unavailable(
        "Truth Capsule request must provide either handler_qualified_name or (method, path)",
        false,
    ))
}

fn resolve_by_method_path<'a>(
    endpoints: &'a [&'a Artifact],
    method: &str,
    path: &str,
    strict: bool,
) -> Result<&'a Artifact, AtlasError> {
    let method_lower = method.to_lowercase();

    let scored: Vec<(&Artifact, i32)> = endpoints
        .iter()
        .copied()
        .filter(|a| {
            a.http_method
                .as_ref()
                .map(|m| m.eq_ignore_ascii_case(&method_lower))
                .unwrap_or(false)
                && a.route_path.is_some()
        })
        .map(|a| {
            let score = score_route_candidate(path, a.route_path.as_deref().unwrap_or(""));
            (a, score)
        })
        .filter(|(_, score)| *score > 0)
        .collect();

    if scored.is_empty() {
        return Err(AtlasError::unavailable(
            format!(
                "No FastAPI endpoint matched method='{}' and path='{}'",
                method, path
            ),
            false,
        ));
    }

    // Find maximum score.
    let best_score = scored
        .iter()
        .map(|(_, s)| *s)
        .max()
        .unwrap_or(0);

    const MIN_SCORE_THRESHOLD: i32 = 10;
    if best_score < MIN_SCORE_THRESHOLD {
        return Err(AtlasError::unavailable(
            format!(
                "Best route score {} below threshold for method='{}', path='{}'",
                best_score, method, path
            ),
            false,
        ));
    }

    // Collect all candidates with the best score.
    let mut best: Vec<&Artifact> = scored
        .into_iter()
        .filter(|(_, s)| *s == best_score)
        .map(|(a, _)| a)
        .collect();

    if best.len() > 1 {
        // Tie-breaker: stable ordering by file_path, line_start.
        best.sort_by(|a, b| {
            let fa = a.file_path.to_string_lossy();
            let fb = b.file_path.to_string_lossy();
            fa.cmp(&fb)
                .then_with(|| a.line_start.cmp(&b.line_start))
        });

        if strict {
            return Err(AtlasError::unavailable(
                format!(
                    "Ambiguous route for method='{}', path='{}'. Multiple endpoints share the best score; use handler_qualified_name.",
                    method, path
                ),
                false,
            ));
        }
    }

    best
        .into_iter()
        .next()
        .ok_or_else(|| {
            AtlasError::unavailable(
                format!(
                    "Failed to select a route for method='{}', path='{}' after scoring",
                    method, path
                ),
                false,
            )
        })
}

fn score_route_candidate(input_path: &str, template: &str) -> i32 {
    let mut score = 0i32;

    let norm_input = trim_slashes(input_path);
    let norm_template = trim_slashes(template);

    if norm_template == norm_input {
        score += 100;
    }

    let input_segments: Vec<&str> = norm_input
        .split('/')
        .filter(|s| !s.is_empty())
        .collect();
    let tmpl_segments: Vec<&str> = norm_template
        .split('/')
        .filter(|s| !s.is_empty())
        .collect();

    if input_segments.len() == tmpl_segments.len() {
        score += 50;
    }

    for (seg_input, seg_tmpl) in input_segments.iter().zip(tmpl_segments.iter()) {
        if let Some((_name, converter)) = parse_param_segment(seg_tmpl) {
            // Wildcard / parameter segment: small penalty, optional converter bonus.
            score -= 5;
            if converter.is_some() {
                score += 5;
            }
        } else if seg_input == seg_tmpl {
            score += 10;
        }
    }

    score
}

fn trim_slashes(path: &str) -> &str {
    // Safe std helper that trims leading and trailing '/' without manual indexing.
    path.trim_matches('/')
}

fn parse_param_segment(segment: &str) -> Option<(&str, Option<&str>)> {
    if !segment.starts_with('{') || !segment.ends_with('}') || segment.len() < 3 {
        return None;
    }

    let inner = &segment[1..segment.len() - 1];
    if inner.is_empty() {
        return None;
    }

    if let Some((name, ty)) = inner.split_once(':') {
        if name.is_empty() || ty.is_empty() {
            return None;
        }
        Some((name, Some(ty)))
    } else {
        Some((inner, None))
    }
}

fn build_schema_group(
    endpoint: &Artifact,
    artifacts: &[Artifact],
    seen_spans: &mut HashSet<(String, usize, usize, String, Option<String>)>,
) -> (Vec<SpanGroupEntry>, Vec<UnresolvedEdge>) {
    let mut model_names: Vec<String> = Vec::new();
    model_names.extend(endpoint.request_models.clone());
    model_names.extend(endpoint.response_models.clone());

    if model_names.is_empty() {
        return (Vec::new(), Vec::new());
    }

    let mut unique = HashSet::new();
    model_names.retain(|n| unique.insert(n.clone()));

    let models: Vec<&Artifact> = artifacts
        .iter()
        .filter(|a| a.kind == ArtifactKind::Model)
        .collect();

    if models.is_empty() {
        let unresolved: Vec<UnresolvedEdge> = model_names
            .into_iter()
            .map(|name| UnresolvedEdge {
                kind: "schema_edge".to_string(),
                detail: name,
                location: None,
            })
            .collect();
        return (Vec::new(), unresolved);
    }

    let mut by_symbol: HashMap<String, Vec<&Artifact>> = HashMap::new();
    let mut by_qualified: HashMap<String, &Artifact> = HashMap::new();

    for artifact in models {
        by_symbol
            .entry(artifact.symbol_name.clone())
            .or_default()
            .push(artifact);
        by_qualified.insert(artifact.qualified_name.clone(), artifact);
    }

    let mut spans: Vec<SpanGroupEntry> = Vec::new();
    let mut unresolved: Vec<UnresolvedEdge> = Vec::new();

    let root_module = endpoint.module_path.clone();

    for (idx, name) in model_names.iter().enumerate() {
        match resolve_schema_target(&root_module, name, &by_qualified, &by_symbol) {
            Some(artifact) => {
                let key = (
                    artifact.file_path.to_string_lossy().to_string(),
                    artifact.line_start,
                    artifact.line_end,
                    "model".to_string(),
                    Some(artifact.qualified_name.clone()),
                );

                if seen_spans.insert((
                    key.0.clone(),
                    key.1,
                    key.2,
                    key.3.clone(),
                    key.4.clone(),
                )) {
                    let depth_factor = (idx + 1) as f32;
                    let score = 0.8f32 / depth_factor;

                    let span = TruthCapsuleSpan {
                        file_path: key.0,
                        start_line: key.1,
                        end_line: key.2,
                        kind: key.3,
                        symbol: key.4,
                        hash: artifact.hash.clone(),
                        snippet: None,
                    };

                    spans.push(SpanGroupEntry {
                        span,
                        evidence: vec!["ast:def".to_string()],
                        score,
                    });
                }
            }
            None => {
                unresolved.push(UnresolvedEdge {
                    kind: "schema_edge".to_string(),
                    detail: name.clone(),
                    location: None,
                });
            }
        }
    }

    (spans, unresolved)
}

fn resolve_schema_target<'a>(
    root_module: &str,
    target: &str,
    by_qualified: &HashMap<String, &'a Artifact>,
    by_symbol: &HashMap<String, Vec<&'a Artifact>>,
) -> Option<&'a Artifact> {
    if let Some(&artifact) = by_qualified.get(target) {
        return Some(artifact);
    }

    let candidates = by_symbol.get(target)?;

    if candidates.len() == 1 {
        return candidates.first().copied();
    }

    let mut ordered: Vec<&Artifact> = candidates.clone();
    ordered.sort_by(|a, b| {
        let sa = common_prefix_len(root_module, &a.module_path);
        let sb = common_prefix_len(root_module, &b.module_path);

        sb.cmp(&sa)
            .then_with(|| a.qualified_name.cmp(&b.qualified_name))
    });

    ordered.first().copied()
}

fn build_dependency_group(
    endpoint: &Artifact,
    artifacts: &[Artifact],
    max_depth: usize,
    seen_spans: &mut HashSet<(String, usize, usize, String, Option<String>)>,
) -> (Vec<SpanGroupEntry>, Vec<UnresolvedEdge>) {
    if max_depth == 0 {
        return (Vec::new(), Vec::new());
    }

    if endpoint.dependency_chain.is_empty() {
        return (Vec::new(), Vec::new());
    }

    let mut by_symbol: HashMap<String, Vec<&Artifact>> = HashMap::new();
    let mut by_qualified: HashMap<String, &Artifact> = HashMap::new();

    for artifact in artifacts {
        by_symbol
            .entry(artifact.symbol_name.clone())
            .or_default()
            .push(artifact);
        by_qualified.insert(artifact.qualified_name.clone(), artifact);
    }

    let mut spans: Vec<SpanGroupEntry> = Vec::new();
    let mut unresolved: Vec<UnresolvedEdge> = Vec::new();

    let root_module = endpoint.module_path.clone();

    for (idx, dep) in endpoint
        .dependency_chain
        .iter()
        .take(max_depth)
        .enumerate()
    {
        let target = normalize_dependency_target(dep);

        match resolve_dependency_target(
            &root_module,
            &target,
            &by_qualified,
            &by_symbol,
        ) {
            Some(artifact) => {
                let key = (
                    artifact.file_path.to_string_lossy().to_string(),
                    artifact.line_start,
                    artifact.line_end,
                    "dependency".to_string(),
                    Some(artifact.qualified_name.clone()),
                );

                if seen_spans.insert((
                    key.0.clone(),
                    key.1,
                    key.2,
                    key.3.clone(),
                    key.4.clone(),
                )) {
                    let depth_factor = (idx + 1) as f32;
                    let score = 0.9f32 / depth_factor;

                    let span = TruthCapsuleSpan {
                        file_path: key.0,
                        start_line: key.1,
                        end_line: key.2,
                        kind: key.3,
                        symbol: key.4,
                        hash: artifact.hash.clone(),
                        snippet: None,
                    };

                    spans.push(SpanGroupEntry {
                        span,
                        evidence: vec!["ast:depends".to_string()],
                        score,
                    });
                }
            }
            None => {
                unresolved.push(UnresolvedEdge {
                    kind: "dependency_edge".to_string(),
                    detail: target,
                    location: None,
                });
            }
        }
    }

    (spans, unresolved)
}

fn normalize_dependency_target(target: &str) -> String {
    if let Some(rest) = target.strip_prefix("Name(id='")
        && let Some(end) = rest.find('\'')
    {
        return rest[..end].to_string();
    }

    if let Some(rest) = target.strip_prefix("Name(id=\"")
        && let Some(end) = rest.find('"')
    {
        return rest[..end].to_string();
    }

    target.to_string()
}

fn resolve_dependency_target<'a>(
    root_module: &str,
    target: &str,
    by_qualified: &HashMap<String, &'a Artifact>,
    by_symbol: &HashMap<String, Vec<&'a Artifact>>,
) -> Option<&'a Artifact> {
    let target = normalize_dependency_target(target);

    if target.contains('.') {
        if let Some(&artifact) = by_qualified.get(&target) {
            return Some(artifact);
        }

        let last = target.rsplit('.').next()?;
        let candidates = by_symbol.get(last)?;

        let mut filtered: Vec<&Artifact> = candidates
            .iter()
            .copied()
            .filter(|a| a.qualified_name.ends_with(&target))
            .collect();

        if filtered.is_empty() {
            return None;
        }

        filtered.sort_by(|a, b| {
            let sa = common_prefix_len(root_module, &a.module_path);
            let sb = common_prefix_len(root_module, &b.module_path);

            sb.cmp(&sa)
                .then_with(|| a.qualified_name.cmp(&b.qualified_name))
        });

        return filtered.first().copied();
    }

    let candidates = by_symbol.get(&target)?;

    if candidates.len() == 1 {
        return candidates.first().copied();
    }

    let mut ordered: Vec<&Artifact> = candidates.clone();
    ordered.sort_by(|a, b| {
        let sa = common_prefix_len(root_module, &a.module_path);
        let sb = common_prefix_len(root_module, &b.module_path);

        sb.cmp(&sa)
            .then_with(|| a.qualified_name.cmp(&b.qualified_name))
    });

    ordered.first().copied()
}

fn resolve_callee_artifact<'a>(
    root_module: &str,
    callee: &str,
    by_qualified: &HashMap<String, &'a Artifact>,
    by_symbol: &HashMap<String, Vec<&'a Artifact>>,
) -> Option<&'a Artifact> {
    if let Some(&artifact) = by_qualified.get(callee) {
        return Some(artifact);
    }

    if callee.contains('.') {
        let last = callee.rsplit('.').next().unwrap_or(callee);
        let candidates = by_symbol.get(last)?;
        let mut filtered: Vec<&Artifact> = candidates
            .iter()
            .copied()
            .filter(|a| a.qualified_name.ends_with(callee))
            .collect();

        if filtered.is_empty() {
            filtered = candidates.clone();
        }

        filtered.sort_by(|a, b| {
            let sa = common_prefix_len(root_module, &a.module_path);
            let sb = common_prefix_len(root_module, &b.module_path);

            sb.cmp(&sa)
                .then_with(|| a.qualified_name.cmp(&b.qualified_name))
        });

        return filtered.first().copied();
    }

    let candidates = by_symbol.get(callee)?;

    if candidates.len() == 1 {
        return candidates.first().copied();
    }

    let mut ordered: Vec<&Artifact> = candidates.clone();
    ordered.sort_by(|a, b| {
        let sa = common_prefix_len(root_module, &a.module_path);
        let sb = common_prefix_len(root_module, &b.module_path);

        sb.cmp(&sa)
            .then_with(|| a.qualified_name.cmp(&b.qualified_name))
    });

    ordered.first().copied()
}

fn common_prefix_len(a: &str, b: &str) -> usize {
    let a_parts: Vec<&str> = a.split('.').collect();
    let b_parts: Vec<&str> = b.split('.').collect();

    let mut count = 0;
    for (x, y) in a_parts.iter().zip(b_parts.iter()) {
        if x != y {
            break;
        }
        count += 1;
    }

    count
}

fn build_middleware_group(
    artifacts: &[Artifact],
    seen_spans: &mut HashSet<(String, usize, usize, String, Option<String>)>,
) -> Vec<SpanGroupEntry> {
    let mut spans: Vec<SpanGroupEntry> = Vec::new();

    for artifact in artifacts
        .iter()
        .filter(|a| a.tags.iter().any(|t| t == "fastapi_middleware"))
    {
        let key = (
            artifact.file_path.to_string_lossy().to_string(),
            artifact.line_start,
            artifact.line_end,
            "middleware".to_string(),
            Some(artifact.qualified_name.clone()),
        );

        if seen_spans.insert((
            key.0.clone(),
            key.1,
            key.2,
            key.3.clone(),
            key.4.clone(),
        )) {
            let span = TruthCapsuleSpan {
                file_path: key.0,
                start_line: key.1,
                end_line: key.2,
                kind: key.3,
                symbol: key.4,
                hash: artifact.hash.clone(),
                snippet: None,
            };

            spans.push(SpanGroupEntry {
                span,
                evidence: vec!["ast:middleware".to_string()],
                score: 0.6,
            });
        }
    }

    spans
}

fn build_exceptions_group(
    endpoint: &Artifact,
    call_graph: &CallGraph,
    artifacts_by_qualified: &HashMap<String, &Artifact>,
    artifacts_by_symbol: &HashMap<String, Vec<&Artifact>>,
    max_depth: usize,
    max_nodes: usize,
    seen_spans: &mut HashSet<(String, usize, usize, String, Option<String>)>,
) -> (Vec<SpanGroupEntry>, Vec<UnresolvedEdge>) {
    if max_depth == 0 || max_nodes == 0 {
        return (Vec::new(), Vec::new());
    }

    let mut spans: Vec<SpanGroupEntry> = Vec::new();
    let mut unresolved: Vec<UnresolvedEdge> = Vec::new();

    let root_module = endpoint.module_path.clone();

    let mut visited: HashSet<String> = HashSet::new();
    let mut queue: VecDeque<(String, usize)> = VecDeque::new();

    visited.insert(endpoint.qualified_name.clone());
    queue.push_back((endpoint.qualified_name.clone(), 0));

    let mut nodes_examined: usize = 0;

    while let Some((current, depth)) = queue.pop_front() {
        if depth >= max_depth {
            continue;
        }

        for callee in call_graph.get_callees(&current) {
            if visited.contains(callee) {
                continue;
            }

            let callee_str = callee.to_string();
            visited.insert(callee_str.clone());

            if nodes_examined >= max_nodes {
                return (spans, unresolved);
            }

            nodes_examined += 1;

            let callee_lc = callee_str.to_lowercase();
            let is_exception_related = callee_lc.contains("exception_handler");

            if !is_exception_related {
                queue.push_back((callee_str, depth + 1));
                continue;
            }

            if let Some(artifact) = resolve_callee_artifact(
                &root_module,
                &callee_str,
                artifacts_by_qualified,
                artifacts_by_symbol,
            ) {
                let key = (
                    artifact.file_path.to_string_lossy().to_string(),
                    artifact.line_start,
                    artifact.line_end,
                    "exception".to_string(),
                    Some(artifact.qualified_name.clone()),
                );

                if seen_spans.insert((
                    key.0.clone(),
                    key.1,
                    key.2,
                    key.3.clone(),
                    key.4.clone(),
                )) {
                    let depth_factor = (depth + 1) as f32;
                    let score = 0.7f32 / depth_factor;

                    let span = TruthCapsuleSpan {
                        file_path: key.0,
                        start_line: key.1,
                        end_line: key.2,
                        kind: key.3,
                        symbol: key.4,
                        hash: artifact.hash.clone(),
                        snippet: None,
                    };

                    spans.push(SpanGroupEntry {
                        span,
                        evidence: vec!["graph:calls".to_string()],
                        score,
                    });
                }

                queue.push_back((callee_str, depth + 1));
            } else {
                unresolved.push(UnresolvedEdge {
                    kind: "exception_edge".to_string(),
                    detail: callee_str,
                    location: None,
                });
            }
        }
    }

    (spans, unresolved)
}

fn build_call_slice_group(
    endpoint: &Artifact,
    call_graph: &CallGraph,
    artifacts_by_qualified: &HashMap<String, &Artifact>,
    artifacts_by_symbol: &HashMap<String, Vec<&Artifact>>,
    max_depth: usize,
    max_nodes: usize,
    seen_spans: &mut HashSet<(String, usize, usize, String, Option<String>)>,
) -> (Vec<SpanGroupEntry>, Vec<UnresolvedEdge>) {
    if max_depth == 0 || max_nodes == 0 {
        return (Vec::new(), Vec::new());
    }

    let mut spans: Vec<SpanGroupEntry> = Vec::new();
    let mut unresolved: Vec<UnresolvedEdge> = Vec::new();

    // Use the endpoint's module as the root for resolving relative/short callee names.
    let root_module = endpoint.module_path.clone();

    // BFS over qualified function names, starting from the endpoint handler.
    let mut visited: HashSet<String> = HashSet::new();
    let mut queue: VecDeque<(String, usize)> = VecDeque::new();

    visited.insert(endpoint.qualified_name.clone());
    queue.push_back((endpoint.qualified_name.clone(), 0));

    let mut nodes_added: usize = 0;

    while let Some((current_qn, depth)) = queue.pop_front() {
        if depth >= max_depth {
            continue;
        }

        for callee in call_graph.get_callees(&current_qn) {
            let callee_str = callee.to_string();

            // Resolve the callee into an artifact so we can both attach spans
            // and get a stable qualified name for further traversal.
            if let Some(artifact) = resolve_callee_artifact(
                &root_module,
                &callee_str,
                artifacts_by_qualified,
                artifacts_by_symbol,
            ) {
                let callee_qn = artifact.qualified_name.clone();

                if visited.contains(&callee_qn) {
                    continue;
                }

                visited.insert(callee_qn.clone());

                if nodes_added >= max_nodes {
                    return (spans, unresolved);
                }

                nodes_added += 1;

                let key = (
                    artifact.file_path.to_string_lossy().to_string(),
                    artifact.line_start,
                    artifact.line_end,
                    "call_slice".to_string(),
                    Some(artifact.qualified_name.clone()),
                );

                if seen_spans.insert((
                    key.0.clone(),
                    key.1,
                    key.2,
                    key.3.clone(),
                    key.4.clone(),
                )) {
                    let depth_factor = (depth + 1) as f32;
                    let score = 0.75f32 / depth_factor;

                    let span = TruthCapsuleSpan {
                        file_path: key.0,
                        start_line: key.1,
                        end_line: key.2,
                        kind: key.3,
                        symbol: key.4,
                        hash: artifact.hash.clone(),
                        snippet: None,
                    };

                    spans.push(SpanGroupEntry {
                        span,
                        evidence: vec!["graph:calls".to_string()],
                        score,
                    });
                }

                // Traverse further from the resolved qualified callee.
                queue.push_back((callee_qn, depth + 1));
            } else {
                // We couldn't map this callee string to a known artifact; record it
                // as an unresolved call edge but do not attempt to traverse further.
                unresolved.push(UnresolvedEdge {
                    kind: "call_edge".to_string(),
                    detail: callee_str,
                    location: None,
                });
            }
        }
    }

    (spans, unresolved)
}
