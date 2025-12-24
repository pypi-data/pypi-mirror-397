use crate::analysis::call_graph::{CallEdge, CallGraph};
use crate::parser::{DefinitionInfo, FastapiRole, DefinitionType};
use ranex_core::AtlasError;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

fn default_true() -> bool {
    true
}

fn default_medium() -> ScalingSeverity {
    ScalingSeverity::Medium
}

fn default_high() -> ScalingSeverity {
    ScalingSeverity::High
}

fn default_external_patterns() -> Vec<CallPattern> {
    vec![
        CallPattern {
            pattern: "requests.".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("external_http".to_string()),
            suggestion: Some(
                "Perform external HTTP work asynchronously or via background jobs where possible"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "httpx.".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("external_http".to_string()),
            suggestion: Some(
                "Ensure outbound HTTP calls are awaited and consider timeouts/retries".to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "session.commit".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_commit".to_string()),
            suggestion: Some(
                "Prefer transactional dependencies and avoid committing directly in endpoints"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "Session.commit".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_commit".to_string()),
            suggestion: Some(
                "Prefer transactional dependencies and avoid committing directly in endpoints"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "async_sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure async_sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "create_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct engines once at startup and reuse via dependency injection"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "async_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct async engines once at startup and reuse via dependency injection"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
    ]
}

fn default_db_query_patterns() -> Vec<CallPattern> {
    vec![
        CallPattern {
            pattern: "session.execute".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_query".to_string()),
            suggestion: Some(
                "Use async DB drivers or offload heavy queries to worker contexts".to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "Session.execute".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_query".to_string()),
            suggestion: Some(
                "Use async DB drivers or offload heavy queries to worker contexts".to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "session.commit".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_commit".to_string()),
            suggestion: Some(
                "Prefer transactional dependencies and avoid committing directly in endpoints"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "Session.commit".to_string(),
            is_prefix_match: true,
            severity: default_high(),
            category: Some("db_commit".to_string()),
            suggestion: Some(
                "Prefer transactional dependencies and avoid committing directly in endpoints"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: vec![ScopeKind::Endpoint],
        },
        CallPattern {
            pattern: "sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "async_sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure async_sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "create_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct engines once at startup and reuse via dependency injection".to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "async_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct async engines once at startup and reuse via dependency injection"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "sqlalchemy.orm.sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "sqlalchemy.orm.async_sessionmaker".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_pooling".to_string()),
            suggestion: Some(
                "Ensure async_sessionmaker/engine are constructed once and reused via dependencies"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "sqlalchemy.create_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct engines once at startup and reuse via dependency injection"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "sqlalchemy.ext.asyncio.create_async_engine".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("db_engine".to_string()),
            suggestion: Some(
                "Construct async engines once at startup and reuse via dependency injection"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
    ]
}

fn default_env_call_patterns() -> Vec<CallPattern> {
    vec![
        CallPattern {
            pattern: "os.getenv".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("env_access".to_string()),
            suggestion: Some(
                "Centralize environment access in settings classes and avoid scattering os.getenv"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
        CallPattern {
            pattern: "os.environ.get".to_string(),
            is_prefix_match: true,
            severity: default_medium(),
            category: Some("env_access".to_string()),
            suggestion: Some(
                "Centralize environment access in settings classes and avoid scattering os.environ lookups"
                    .to_string(),
            ),
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        },
    ]
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "PascalCase")]
pub enum ScalingSeverity {
    Critical,
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ScopeKind {
    Endpoint,
    Dependency,
    Lifespan,
    Middleware,
    BackgroundTask,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FastapiScalingPolicy {
    pub version: String,

    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub endpoints: EndpointRules,

    #[serde(default)]
    pub dependencies: DependencyRules,

    #[serde(default)]
    pub lifespan: LifespanRules,

    #[serde(default)]
    pub routers: RouterRules,

    #[serde(default)]
    pub middleware: MiddlewareRules,

    #[serde(default)]
    pub background_tasks: BackgroundTaskRules,

    #[serde(default)]
    pub models: ModelRules,

    #[serde(default)]
    pub external_calls: Vec<CallPattern>,

    #[serde(default)]
    pub db_query_calls: Vec<CallPattern>,

    #[serde(default)]
    pub env_call_patterns: Vec<CallPattern>,
}

impl Default for FastapiScalingPolicy {
    fn default() -> Self {
        Self {
            version: "1.0".to_string(),
            enabled: true,
            endpoints: EndpointRules::default(),
            dependencies: DependencyRules::default(),
            lifespan: LifespanRules::default(),
            routers: RouterRules::default(),
            middleware: MiddlewareRules::default(),
            background_tasks: BackgroundTaskRules::default(),
            models: ModelRules::default(),
            external_calls: default_external_patterns(),
            db_query_calls: default_db_query_patterns(),
            env_call_patterns: default_env_call_patterns(),
        }
    }
}

fn analyze_auth_wiring(
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    let mut by_symbol: HashMap<&str, Vec<&ParsedDefinition>> = HashMap::new();
    for parsed in definitions {
        by_symbol
            .entry(parsed.definition.name.as_str())
            .or_default()
            .push(parsed);
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        let mut all_dependencies: Vec<String> = Vec::new();
        let mut security_dependencies: Vec<String> = Vec::new();
        let mut jwt_calls: Vec<String> = Vec::new();
        let mut direct_dep_targets: Vec<String> = Vec::new();
        for param in &def.params {
            if let Some(dep) = &param.dependency_target {
                all_dependencies.push(dep.clone());
                if param.is_fastapi_depends {
                    direct_dep_targets.push(dep.clone());
                }
                let lower = dep.to_lowercase();
                if param.is_security_dependency
                    || lower.contains("oauth2")
                    || lower.contains("security")
                    || lower.contains("auth")
                {
                    security_dependencies.push(dep.clone());
                }
            } else if param.is_security_dependency {
                // Fallback to parameter name when dependency target is not resolved.
                security_dependencies.push(param.name.clone());
                all_dependencies.push(param.name.clone());
            }
        }

        // Expand dependency chain: endpoint depends on get_token -> get_token depends on oauth2_scheme.
        let mut visited: HashSet<String> = HashSet::new();
        let mut queue: Vec<String> = direct_dep_targets.clone();
        while let Some(symbol) = queue.pop() {
            if !visited.insert(symbol.clone()) {
                continue;
            }
            let Some(candidates) = by_symbol.get(symbol.as_str()) else {
                continue;
            };
            for dep_def in candidates {
                for p in &dep_def.definition.params {
                    if let Some(dep_target) = &p.dependency_target {
                        if p.is_fastapi_depends {
                            queue.push(dep_target.clone());
                        }
                        if p.is_security_dependency {
                            security_dependencies.push(dep_target.clone());
                        }
                    }
                }
            }
        }

        let mut has_permission_checks = false;
        let mut permission_dependencies: Vec<String> = Vec::new();
        let mut has_custom_exception_handler = false;

        let has_http_exception = edges.iter().any(|edge| {
            let callee = &edge.callee;
            callee == "HTTPException" || callee.ends_with(".HTTPException")
        });

        for edge in &edges {
            let callee_lc = edge.callee.to_lowercase();
            if callee_lc.contains("oauth2")
                || callee_lc.contains("security")
                || callee_lc.contains("auth")
                || callee_lc.contains("token")
            {
                security_dependencies.push(edge.callee.clone());
            }
            if callee_lc.contains("jwt") {
                jwt_calls.push(edge.callee.clone());
            }
            if callee_lc.contains("permission") || callee_lc.contains("authorize") || callee_lc.contains("scope") {
                has_permission_checks = true;
                permission_dependencies.push(edge.callee.clone());
            }
            if callee_lc.contains("exception_handler") {
                has_custom_exception_handler = true;
            }

            // One-hop expansion: follow dependencies called from this callee to discover auth providers (e.g., oauth2_scheme).
            for sub_edge in call_graph.get_outgoing_edges(&edge.callee) {
                let sub_lc = sub_edge.callee.to_lowercase();
                if sub_lc.contains("oauth2")
                    || sub_lc.contains("security")
                    || sub_lc.contains("auth")
                    || sub_lc.contains("token")
                {
                    security_dependencies.push(sub_edge.callee.clone());
                }
                if sub_lc.contains("jwt") {
                    jwt_calls.push(sub_edge.callee.clone());
                }
                if sub_lc.contains("permission") || sub_lc.contains("authorize") || sub_lc.contains("scope") {
                    has_permission_checks = true;
                    permission_dependencies.push(sub_edge.callee.clone());
                }
            }
        }

        security_dependencies.sort();
        security_dependencies.dedup();

        let security_count = security_dependencies.len();
        let has_security_dependency = security_count > 0;

        let has_oauth2_provider = security_dependencies
            .iter()
            .any(|dep| dep.to_lowercase().contains("oauth2"))
            || edges.iter().any(|edge| {
                let callee = edge.callee.to_lowercase();
                callee.contains("oauth2passwordbearer")
            });

        let has_jwt = !jwt_calls.is_empty()
            || all_dependencies
                .iter()
                .any(|dep| dep.to_lowercase().contains("jwt"));

        if !has_permission_checks {
            has_permission_checks = security_dependencies
                .iter()
                .any(|dep| dep.to_lowercase().contains("permission"));
            if has_permission_checks {
                permission_dependencies
                    .extend(security_dependencies.iter().cloned());
            }
        }

        report.auth_wiring.push(AuthWiringInfo {
            qualified_name: qualified,
            file_path: parsed.file_path.clone(),
            has_security_dependency,
            security_dependency_count: security_count,
            security_dependencies,
            has_oauth2_provider,
            has_jwt,
            jwt_calls,
            has_permission_checks,
            permission_dependencies,
            has_custom_exception_handler,
            has_http_exception,
        });
    }
}

fn analyze_middleware(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    let rules = &policy.middleware;

    if !rules.enabled {
        return;
    }

    // 1. Warn on BaseHTTPMiddleware subclasses if configured.
    if rules.warn_on_base_http_middleware {
        for parsed in definitions {
            let def = &parsed.definition;
            if def
                .base_classes
                .iter()
                .any(|b| b == "BaseHTTPMiddleware")
            {
                let qualified = qualify_name(&parsed.module_path, def);
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Middleware,
                    severity: rules.base_http_middleware_severity,
                    message: format!(
                        "Class '{}' extends BaseHTTPMiddleware; prefer simpler function-based middleware or lighter wrappers for scalability",
                        qualified,
                    ),
                    file_path: Some(parsed.file_path.clone()),
                    qualified_name: Some(qualified),
                    suggestion: None,
                    category: Some("base_http_middleware".to_string()),
                });
            }
        }
    }

    // 2. Enforce maximum number of middleware layers if configured.
    if let Some(max_layers) = rules.max_middleware_layers {
        let middleware_count = definitions
            .iter()
            .filter(|parsed| parsed.definition.roles.contains(&FastapiRole::Middleware))
            .count();

        if middleware_count > max_layers {
            report.violations.push(ScalingViolation {
                scope: ScopeKind::Middleware,
                severity: ScalingSeverity::Medium,
                message: format!(
                    "Project defines {} FastAPI middleware layers (max allowed: {})",
                    middleware_count, max_layers,
                ),
                file_path: None,
                qualified_name: None,
                suggestion: None,
                category: Some("max_middleware_layers".to_string()),
            });
        }
    }

    // 3. Apply blocking call patterns within middleware.
    if rules.blocking_calls.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !def.roles.contains(&FastapiRole::Middleware) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);
        if edges.is_empty() {
            continue;
        }

        let scope = ScopeKind::Middleware;
        for edge in edges {
            let callee = &edge.callee;
            for pattern in &rules.blocking_calls {
                if call_matches_pattern(callee, pattern) && scope_violates_pattern(scope, pattern)
                {
                    report.violations.push(ScalingViolation {
                        scope,
                        severity: pattern.severity,
                        message: format!(
                            "Middleware '{}' calls '{}' which matches a configured blocking_calls pattern",
                            qualified, callee,
                        ),
                        file_path: Some(parsed.file_path.clone()),
                        qualified_name: Some(qualified.clone()),
                        suggestion: pattern.suggestion.clone(),
                        category: pattern.category.clone(),
                    });
                }
            }
        }
    }
}

fn analyze_db_patterns(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if policy.db_query_calls.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let caller_suffix = format!(".{}", def.name);

        for edge in call_graph.edges() {
            if !edge.file_path.contains(&parsed.file_path) {
                continue;
            }
            if edge.caller != qualified && !edge.caller.ends_with(&caller_suffix) {
                continue;
            }
            for pattern in &policy.db_query_calls {
                let callee_norm = edge.callee.trim_end_matches("()");
                let mut matched = call_matches_pattern(callee_norm, pattern);
                if !matched && callee_norm.contains(&pattern.pattern) {
                    matched = true;
                }
                if matched {
                    report.db_patterns.push(DbPatternInsight {
                        qualified_name: qualified.clone(),
                        file_path: parsed.file_path.clone(),
                        callee: edge.callee.clone(),
                        category: pattern
                            .category
                            .clone()
                            .unwrap_or_else(|| "db_query".to_string()),
                        severity: pattern.severity,
                    });
                }
            }
        }
    }
}

fn analyze_config_env_linkage(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if policy.env_call_patterns.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !def.base_classes.iter().any(|base| base == "BaseSettings") {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let mut hits: Vec<ConfigEnvHit> = Vec::new();

        // Call graph callers for methods include class context (e.g., Settings.db_url).
        // DefinitionInfo methods only store the method name (e.g., db_url). Match edges by file_path + module prefix + method suffix.
        let mut caller_suffixes: Vec<String> = Vec::new();
        caller_suffixes.push(format!(".{}", def.name));
        for other in definitions {
            if other.module_path != parsed.module_path {
                continue;
            }
            if other.definition.def_type == DefinitionType::Method {
                caller_suffixes.push(format!(".{}", other.definition.name));
            }
        }
        caller_suffixes.sort();
        caller_suffixes.dedup();

        for edge in call_graph.edges() {
            if edge.file_path != parsed.file_path {
                continue;
            }
            if !edge.caller.starts_with(&parsed.module_path) {
                continue;
            }

            // Callers in the call graph are always module-qualified. For methods they include class context.
            // We therefore match by module prefix plus known ".<method>" suffixes.
            if !caller_suffixes.iter().any(|s| edge.caller.ends_with(s)) {
                continue;
            }

            let callee = &edge.callee;
            for pattern in &policy.env_call_patterns {
                if call_matches_pattern(callee, pattern) {
                    hits.push(ConfigEnvHit {
                        callee: callee.clone(),
                        pattern: pattern.pattern.clone(),
                        category: pattern.category.clone(),
                        severity: pattern.severity,
                    });
                }
            }
        }

        if !hits.is_empty() {
            report.config_env_links.push(ConfigEnvLink {
                settings_name: qualified,
                file_path: parsed.file_path.clone(),
                env_hits: hits,
            });
        }
    }
}

fn analyze_test_linkage(
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let mut seen: HashSet<(String, String, usize)> = HashSet::new();
        let mut all_incoming: Vec<&CallEdge> = Vec::new();
        all_incoming.extend(call_graph.get_incoming_edges(&qualified));
        all_incoming.extend(call_graph.get_incoming_edges(&def.name));

        for edge in all_incoming {
            if !is_test_file(&edge.file_path) {
                continue;
            }
            let callee_matches = edge.callee == def.name
                || edge.callee.ends_with(&format!(".{}", def.name))
                || edge.callee == qualified;
            if !callee_matches {
                continue;
            }
            let key = (edge.caller.clone(), edge.file_path.clone(), edge.line_number);
            if !seen.insert(key) {
                continue;
            }
            report.test_links.push(TestLinkInsight {
                endpoint: qualified.clone(),
                endpoint_file: parsed.file_path.clone(),
                test_caller: edge.caller.clone(),
                test_file: edge.file_path.clone(),
                call_line: edge.line_number,
            });
        }
    }
}

fn analyze_external_calls(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if policy.external_calls.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        for edge in edges {
            let callee = &edge.callee;
            for pattern in &policy.external_calls {
                if call_matches_pattern(callee, pattern)
                    && scope_violates_pattern(ScopeKind::Endpoint, pattern)
                {
                    report.external_calls.push(ExternalCallInsight {
                        qualified_name: qualified.clone(),
                        file_path: parsed.file_path.clone(),
                        callee: callee.clone(),
                        pattern: pattern.pattern.clone(),
                        category: pattern.category.clone(),
                        severity: pattern.severity,
                    });
                }
            }
        }
    }
}

fn analyze_db_queries(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if policy.db_query_calls.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        for edge in edges {
            let callee = &edge.callee;
            for pattern in &policy.db_query_calls {
                if call_matches_pattern(callee, pattern)
                    && scope_violates_pattern(ScopeKind::Endpoint, pattern)
                {
                    report.db_queries.push(DbQueryInsight {
                        qualified_name: qualified.clone(),
                        file_path: parsed.file_path.clone(),
                        callee: callee.clone(),
                        pattern: pattern.pattern.clone(),
                        category: pattern.category.clone(),
                        severity: pattern.severity,
                    });
                }
            }
        }
    }
}

fn analyze_env_access(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if policy.env_call_patterns.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        for edge in edges {
            let callee = &edge.callee;
            for pattern in &policy.env_call_patterns {
                if call_matches_pattern(callee, pattern)
                    && scope_violates_pattern(ScopeKind::Endpoint, pattern)
                {
                    report.env_links.push(EnvAccessInsight {
                        qualified_name: qualified.clone(),
                        file_path: parsed.file_path.clone(),
                        callee: callee.clone(),
                        pattern: pattern.pattern.clone(),
                        category: pattern.category.clone(),
                        severity: pattern.severity,
                    });
                }
            }
        }
    }
}

fn analyze_background_tasks(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    let rules = &policy.background_tasks;

    if !rules.enabled {
        return;
    }

    if rules.heavy_call_patterns.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;

        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);
        if edges.is_empty() {
            continue;
        }

        // Detect whether this endpoint enqueues any job-queue tasks.
        let mut has_job_queue_call = false;
        for edge in &edges {
            for queue in &rules.job_queues {
                for func in &queue.enqueue_functions {
                    if edge.callee == *func
                        || edge.callee == format!("{}.{}", queue.package, func)
                    {
                        has_job_queue_call = true;
                        break;
                    }
                }
                if has_job_queue_call {
                    break;
                }
            }
            if has_job_queue_call {
                break;
            }
        }

        for edge in &edges {
            let callee = &edge.callee;

            for pattern in &rules.heavy_call_patterns {
                if !call_matches_pattern(callee, pattern) {
                    continue;
                }

                // Record observation for report consumers.
                report.background_insights.push(BackgroundTaskInsight {
                    qualified_name: qualified.clone(),
                    file_path: parsed.file_path.clone(),
                    heavy_call: callee.clone(),
                    matched_pattern: pattern.pattern.clone(),
                    enqueued_via_job_queue: has_job_queue_call,
                    is_inline_heavy_call: !has_job_queue_call,
                });

                // If we prefer job queues for heavy tasks but this endpoint never
                // enqueues a job, flag it.
                if rules.prefer_job_queues_for_heavy_tasks && !has_job_queue_call {
                    report.violations.push(ScalingViolation {
                        scope: ScopeKind::BackgroundTask,
                        severity: pattern.severity,
                        message: format!(
                            "Endpoint '{}' calls '{}' which matches a heavy_call_patterns entry but does not enqueue any configured job queue task",
                            qualified, callee,
                        ),
                        file_path: Some(parsed.file_path.clone()),
                        qualified_name: Some(qualified.clone()),
                        suggestion: pattern.suggestion.clone(),
                        category: pattern.category.clone(),
                    });
                }
            }
        }
    }
}

fn analyze_routers(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    report: &mut FastapiScalingReport,
) {
    let router_rules = &policy.routers;

    if !router_rules.enabled || !router_rules.warn_on_direct_app_routes {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;

        if !is_endpoint(def) {
            continue;
        }

        if let Some(router_name) = router_tag(def)
            && router_name == "app"
        {
            let module = parsed.module_path.as_str();
            let allowed = router_rules
                .allowed_direct_route_modules
                .iter()
                .any(|m| m == module);

            if !allowed {
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Endpoint,
                    severity: router_rules.direct_app_route_severity,
                    message: format!(
                        "Endpoint '{}' uses direct app routes in module '{}' (prefer APIRouter instances for scalable routing)",
                        qualify_name(&parsed.module_path, def),
                        parsed.module_path,
                    ),
                    file_path: Some(parsed.file_path.clone()),
                    qualified_name: Some(qualify_name(&parsed.module_path, def)),
                    suggestion: Some(
                        "Move this endpoint to an APIRouter or explicitly allow this module in RouterRules.allowed_direct_route_modules"
                            .to_string(),
                    ),
                    category: Some("direct_app_route".to_string()),
                });
            }
        }
    }
}

#[derive(Debug, Clone)]
pub struct ParsedDefinition {
    pub definition: DefinitionInfo,
    pub file_path: String,
    pub module_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ScalingStats {
    pub total_definitions: usize,
    pub total_endpoints: usize,
    pub async_endpoints: usize,
    pub sync_endpoints: usize,
    pub modules_with_endpoints: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScalingViolation {
    pub scope: ScopeKind,
    pub severity: ScalingSeverity,
    pub message: String,
    pub file_path: Option<String>,
    pub qualified_name: Option<String>,
    pub suggestion: Option<String>,
    pub category: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FastapiScalingReport {
    pub policy_version: String,
    pub stats: ScalingStats,
    pub violations: Vec<ScalingViolation>,
    /// Per-endpoint background task observations derived from heavy_call_patterns and job queue usage.
    #[serde(default)]
    pub background_insights: Vec<BackgroundTaskInsight>,
    /// Mapping of resource kinds to modules and whether lifespan handlers are present.
    #[serde(default)]
    pub lifespan_map: Vec<LifespanResourceUsage>,
    /// Ordered middleware entries discovered in the codebase.
    #[serde(default)]
    pub middleware_stack: Vec<MiddlewareInfo>,
    /// Side-effect observations (e.g., commits) detected in endpoint call graphs.
    #[serde(default)]
    pub side_effects: Vec<SideEffectInsight>,
    /// Auth/security coverage per endpoint.
    #[serde(default)]
    pub auth_wiring: Vec<AuthWiringInfo>,
    /// External call observations (configurable patterns).
    #[serde(default)]
    pub external_calls: Vec<ExternalCallInsight>,
    /// Database query call observations (configurable patterns).
    #[serde(default)]
    pub db_queries: Vec<DbQueryInsight>,
    /// Database pattern semantics (categories derived from db_query_calls patterns).
    #[serde(default)]
    pub db_patterns: Vec<DbPatternInsight>,
    /// Environment/config access observations (configurable patterns).
    #[serde(default)]
    pub env_links: Vec<EnvAccessInsight>,
    /// Settings/config classes (e.g., Pydantic BaseSettings) and their env access hits.
    #[serde(default)]
    pub config_env_links: Vec<ConfigEnvLink>,
    /// Mapping from endpoints to tests/fixtures that call them (for regression targeting).
    #[serde(default)]
    pub test_links: Vec<TestLinkInsight>,
}

impl FastapiScalingReport {
    pub fn new(policy_version: impl Into<String>) -> Self {
        Self {
            policy_version: policy_version.into(),
            stats: ScalingStats::default(),
            violations: Vec::new(),
            background_insights: Vec::new(),
            lifespan_map: Vec::new(),
            middleware_stack: Vec::new(),
            side_effects: Vec::new(),
            auth_wiring: Vec::new(),
            external_calls: Vec::new(),
            db_queries: Vec::new(),
            db_patterns: Vec::new(),
            env_links: Vec::new(),
            config_env_links: Vec::new(),
            test_links: Vec::new(),
        }
    }
}

pub fn analyze_definitions(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
) -> FastapiScalingReport {
    let mut report = FastapiScalingReport::new(&policy.version);
    report.stats.total_definitions = definitions.len();

    if !policy.enabled {
        return report;
    }

    analyze_endpoints(policy, definitions, call_graph, &mut report);
    analyze_dependencies(policy, definitions, call_graph, &mut report);
    analyze_routers(policy, definitions, &mut report);
    analyze_models(policy, definitions, &mut report);

    analyze_endpoint_call_patterns(policy, definitions, call_graph, &mut report);
    analyze_middleware(policy, definitions, call_graph, &mut report);
    report.middleware_stack = build_middleware_stack(definitions, call_graph, policy);
    analyze_background_tasks(policy, definitions, call_graph, &mut report);
    analyze_side_effects(definitions, call_graph, &mut report);
    analyze_auth_wiring(definitions, call_graph, &mut report);
    analyze_external_calls(policy, definitions, call_graph, &mut report);
    analyze_db_queries(policy, definitions, call_graph, &mut report);
    analyze_db_patterns(policy, definitions, call_graph, &mut report);
    analyze_env_access(policy, definitions, call_graph, &mut report);
    analyze_config_env_linkage(policy, definitions, call_graph, &mut report);
    analyze_test_linkage(definitions, call_graph, &mut report);

    report
}

fn analyze_endpoints(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    _call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if !policy.endpoints.enabled {
        return;
    }

    let mut module_counts: HashMap<String, usize> = HashMap::new();
    let mut router_counts: HashMap<String, usize> = HashMap::new();

    for parsed in definitions {
        if !is_endpoint(&parsed.definition) {
            continue;
        }

        report.stats.total_endpoints += 1;
        if parsed.definition.is_async {
            report.stats.async_endpoints += 1;
        } else {
            report.stats.sync_endpoints += 1;
            if policy.endpoints.warn_on_sync_handlers {
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Endpoint,
                    severity: policy.endpoints.sync_handler_severity,
                    message: format!(
                        "Endpoint '{}' is synchronous; convert to async to improve scalability",
                        qualify_name(&parsed.module_path, &parsed.definition)
                    ),
                    file_path: Some(parsed.file_path.clone()),
                    qualified_name: Some(qualify_name(&parsed.module_path, &parsed.definition)),
                    suggestion: Some(
                        "Use async HTTP handlers or move blocking work into background tasks"
                            .to_string(),
                    ),
                    category: Some("sync_handler".to_string()),
                });
            }
        }

        *module_counts.entry(parsed.module_path.clone()).or_insert(0) += 1;
        if let Some(router_name) = router_tag(&parsed.definition) {
            *router_counts.entry(router_name.to_string()).or_insert(0) += 1;
        }
    }

    report.stats.modules_with_endpoints = module_counts.len();

    if let Some(max_sync) = policy.endpoints.thresholds.max_sync_endpoints
        && report.stats.sync_endpoints > max_sync
    {
        report.violations.push(ScalingViolation {
            scope: ScopeKind::Endpoint,
            severity: ScalingSeverity::High,
            message: format!(
                "Project has {} synchronous endpoints (max allowed: {})",
                report.stats.sync_endpoints, max_sync
            ),
            file_path: None,
            qualified_name: None,
            suggestion: Some("Convert synchronous handlers to async or delegate blocking work".to_string()),
            category: Some("threshold_sync_endpoints".to_string()),
        });
    }

    if let Some(limit) = policy.endpoints.thresholds.max_endpoints_per_module {
        for (module, count) in module_counts {
            if count > limit {
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Endpoint,
                    severity: ScalingSeverity::Medium,
                    message: format!(
                        "Module '{}' defines {} endpoints (max allowed per module: {})",
                        module, count, limit
                    ),
                    file_path: None,
                    qualified_name: None,
                    suggestion: Some("Consider splitting endpoints into feature-focused modules or routers".to_string()),
                    category: Some("threshold_module_endpoints".to_string()),
                });
            }
        }
    }

    if let Some(limit) = policy.endpoints.thresholds.max_endpoints_per_router {
        for (router, count) in router_counts {
            if count > limit {
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Endpoint,
                    severity: ScalingSeverity::Medium,
                    message: format!(
                        "Router '{}' exposes {} endpoints (max allowed per router: {})",
                        router, count, limit
                    ),
                    file_path: None,
                    qualified_name: None,
                    suggestion: Some("Break routers into smaller sub-routers to keep routing tables efficient".to_string()),
                    category: Some("threshold_router_endpoints".to_string()),
                });
            }
        }
    }
}

fn is_endpoint(def: &DefinitionInfo) -> bool {
    def.roles.contains(&FastapiRole::Endpoint) || def.tags.iter().any(|t| t == "fastapi_route")
}

fn is_test_file(file_path: &str) -> bool {
    let lower = file_path.to_lowercase();
    if lower.contains("/tests/") || lower.contains("\\tests\\") {
        return true;
    }
    let filename = Path::new(file_path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or_default()
        .to_lowercase();
    filename.starts_with("test_") || filename.ends_with("_test.py")
}

fn qualify_name(module_path: &str, def: &DefinitionInfo) -> String {
    if module_path.is_empty() {
        def.name.clone()
    } else {
        format!("{}.{}", module_path, def.name)
    }
}

fn router_tag(def: &DefinitionInfo) -> Option<&str> {
    for tag in &def.tags {
        if let Some(router) = tag.strip_prefix("router_")
            && !router.is_empty()
        {
            return Some(router);
        }
    }
    None
}

fn infer_scope(def: &DefinitionInfo) -> ScopeKind {
    if def.roles.contains(&FastapiRole::Endpoint) {
        ScopeKind::Endpoint
    } else if def.roles.contains(&FastapiRole::Middleware) {
        ScopeKind::Middleware
    } else if def
        .roles
        .iter()
        .any(|r| matches!(r, FastapiRole::LifespanStartup | FastapiRole::LifespanShutdown))
    {
        ScopeKind::Lifespan
    } else {
        // Treat everything else as a generic dependency/helper.
        ScopeKind::Dependency
    }
}

fn analyze_dependencies(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    let dep_rules = &policy.dependencies;

    if !dep_rules.enabled {
        return;
    }

    if dep_rules.resources.is_empty()
        && dep_rules.require_yield_for_kinds.is_empty()
        && dep_rules
            .forbid_inline_resources_in_endpoints
            .is_empty()
    {
        return;
    }

    // Fast lookup for resource kind rules.
    let mut resources_by_kind: HashMap<&str, &ResourceKindRule> = HashMap::new();
    for resource in &dep_rules.resources {
        resources_by_kind.insert(resource.kind.as_str(), resource);
    }

    // Track first usage of each resource kind per module so we can later
    // validate lifespan coverage.
    let mut first_resource_usage: HashMap<(String, String), usize> = HashMap::new();

    for (idx, parsed) in definitions.iter().enumerate() {
        let def = &parsed.definition;
        let scope = infer_scope(def);
        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        if edges.is_empty() {
            continue;
        }

        for (kind, resource) in &resources_by_kind {
            // Optional module filter
            if !resource.module_prefixes.is_empty()
                && !resource
                    .module_prefixes
                    .iter()
                    .any(|prefix| parsed.module_path.starts_with(prefix))
            {
                continue;
            }

            let mut creates_resource = false;

            for edge in &edges {
                for pattern in &resource.create_call_patterns {
                    let callee = &edge.callee;
                    let matches = if pattern.is_prefix_match {
                        callee.starts_with(&pattern.pattern)
                    } else {
                        callee == &pattern.pattern
                    };

                    if matches {
                        creates_resource = true;

                        // Record first usage for lifespan analysis.
                        first_resource_usage
                            .entry(((*kind).to_string(), parsed.module_path.clone()))
                            .or_insert(idx);

                        // Enforce allowed_scopes for resource kinds.
                        if !resource.allowed_scopes.is_empty()
                            && !resource.allowed_scopes.contains(&scope)
                        {
                            report.violations.push(ScalingViolation {
                                scope,
                                severity: resource.severity_outside_allowed,
                                message: format!(
                                    "Function '{}' (scope {:?}) creates resource kind '{}' via call '{}' which is outside allowed_scopes",
                                    qualified, scope, kind, callee,
                                ),
                                file_path: Some(parsed.file_path.clone()),
                                qualified_name: Some(qualified.clone()),
                                suggestion: None,
                                category: Some("resource_scope".to_string()),
                            });
                        }

                        // Forbid inline resource creation directly in endpoints when configured.
                        if scope == ScopeKind::Endpoint
                            && dep_rules
                                .forbid_inline_resources_in_endpoints
                                .iter()
                                .any(|k| k == *kind)
                        {
                            report.violations.push(ScalingViolation {
                                scope: ScopeKind::Endpoint,
                                severity: resource.severity_outside_allowed,
                                message: format!(
                                    "Endpoint '{}' creates resource kind '{}' inline via call '{}' (consider moving creation into a dependency or background task)",
                                    qualified, kind, callee,
                                ),
                                file_path: Some(parsed.file_path.clone()),
                                qualified_name: Some(qualified.clone()),
                                suggestion: None,
                                category: Some("inline_resource_in_endpoint".to_string()),
                            });
                        }
                    }
                }
            }

            // Require yield-based management for certain kinds in dependency-like scopes.
            if creates_resource
                && scope == ScopeKind::Dependency
                && dep_rules
                    .require_yield_for_kinds
                    .iter()
                    .any(|k| k == *kind)
                && !def.has_yield
            {
                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Dependency,
                    severity: resources_by_kind
                        .get(kind)
                        .map(|r| r.severity_outside_allowed)
                        .unwrap_or(ScalingSeverity::High),
                    message: format!(
                        "Function '{}' manages resource kind '{}' but does not use a yield-based pattern (consider FastAPI's yield dependencies)",
                        qualified, kind,
                    ),
                    file_path: Some(parsed.file_path.clone()),
                    qualified_name: Some(qualified.clone()),
                    suggestion: None,
                    category: Some("resource_missing_yield".to_string()),
                });
            }
        }
    }

    analyze_lifespan_from_usage(&policy.lifespan, definitions, &first_resource_usage, report);
}

fn analyze_lifespan_from_usage(
    life_rules: &LifespanRules,
    definitions: &[ParsedDefinition],
    first_resource_usage: &HashMap<(String, String), usize>,
    report: &mut FastapiScalingReport,
) {
    if !life_rules.enabled || life_rules.require_lifespan_for_kinds.is_empty() {
        return;
    }

    // Collect modules that define lifespan handlers.
    let mut modules_with_lifespan: HashMap<&str, bool> = HashMap::new();
    for parsed in definitions {
        let def = &parsed.definition;
        if def
            .roles
            .iter()
            .any(|r| matches!(r, FastapiRole::LifespanStartup | FastapiRole::LifespanShutdown))
        {
            modules_with_lifespan.insert(parsed.module_path.as_str(), true);
        }
    }

    for kind in &life_rules.require_lifespan_for_kinds {
        for ((resource_kind, module_path), def_index) in first_resource_usage {
            if resource_kind != kind {
                continue;
            }

            if life_rules
                .ignore_modules
                .iter()
                .any(|m| m == module_path)
            {
                continue;
            }

            let has_lifespan = modules_with_lifespan.contains_key(module_path.as_str());

            if let Some(parsed) = definitions.get(*def_index) {
                let qualified = qualify_name(&parsed.module_path, &parsed.definition);
                report.lifespan_map.push(LifespanResourceUsage {
                    resource_kind: resource_kind.clone(),
                    module: module_path.clone(),
                    first_usage: QualifiedLocation {
                        qualified_name: qualified.clone(),
                        file_path: parsed.file_path.clone(),
                    },
                    has_lifespan_handler: has_lifespan,
                });
            }

            if modules_with_lifespan.contains_key(module_path.as_str()) {
                continue;
            }

            if let Some(parsed) = definitions.get(*def_index) {
                let qualified = qualify_name(&parsed.module_path, &parsed.definition);

                report.violations.push(ScalingViolation {
                    scope: ScopeKind::Lifespan,
                    severity: ScalingSeverity::High,
                    message: format!(
                        "Module '{}' uses resource kind '{}' (first seen in '{}') but defines no FastAPI lifespan handlers (startup/shutdown)",
                        module_path, resource_kind, qualified,
                    ),
                    file_path: Some(parsed.file_path.clone()),
                    qualified_name: Some(qualified),
                    suggestion: None,
                    category: Some("missing_lifespan_for_resource".to_string()),
                });
            }
        }
    }
}

fn call_matches_pattern(callee: &str, pattern: &CallPattern) -> bool {
    if pattern.is_prefix_match {
        callee.starts_with(&pattern.pattern)
    } else {
        callee == pattern.pattern
    }
}

fn scope_violates_pattern(scope: ScopeKind, pattern: &CallPattern) -> bool {
    if pattern.forbidden_scopes.contains(&scope) {
        return true;
    }

    if !pattern.allowed_scopes.is_empty() && !pattern.allowed_scopes.contains(&scope) {
        return true;
    }

    false
}

fn analyze_endpoint_call_patterns(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    if !policy.endpoints.enabled {
        return;
    }

    let blocking = &policy.endpoints.blocking_calls;
    let cpu_bound = &policy.endpoints.cpu_bound_calls;

    if blocking.is_empty() && cpu_bound.is_empty() {
        return;
    }

    for parsed in definitions {
        let def = &parsed.definition;

        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        if edges.is_empty() {
            continue;
        }

        let scope = ScopeKind::Endpoint;

        for edge in edges {
            let callee = &edge.callee;

            for pattern in blocking {
                if call_matches_pattern(callee, pattern) && scope_violates_pattern(scope, pattern)
                {
                    report.violations.push(ScalingViolation {
                        scope,
                        severity: pattern.severity,
                        message: format!(
                            "Endpoint '{}' calls '{}' which matches a configured blocking_calls pattern",
                            qualified, callee,
                        ),
                        file_path: Some(parsed.file_path.clone()),
                        qualified_name: Some(qualified.clone()),
                        suggestion: pattern.suggestion.clone(),
                        category: pattern.category.clone(),
                    });
                }
            }

            for pattern in cpu_bound {
                if call_matches_pattern(callee, pattern) && scope_violates_pattern(scope, pattern)
                {
                    report.violations.push(ScalingViolation {
                        scope,
                        severity: pattern.severity,
                        message: format!(
                            "Endpoint '{}' calls '{}' which matches a configured cpu_bound_calls pattern",
                            qualified, callee,
                        ),
                        file_path: Some(parsed.file_path.clone()),
                        qualified_name: Some(qualified.clone()),
                        suggestion: pattern.suggestion.clone(),
                        category: pattern.category.clone(),
                    });
                }
            }
        }
    }
}

fn analyze_models(
    policy: &FastapiScalingPolicy,
    definitions: &[ParsedDefinition],
    report: &mut FastapiScalingReport,
) {
    if !policy.models.enabled {
        return;
    }

    let thresholds = &policy.models.thresholds;

    for parsed in definitions {
        let def = &parsed.definition;

        if !def.tags.iter().any(|t| t == "pydantic_model") {
            continue;
        }

        if let Some(max_fields) = thresholds.max_fields_per_model
            && let Some(field_count) = def.field_count
            && field_count > max_fields
        {
            report.violations.push(ScalingViolation {
                scope: ScopeKind::Dependency,
                severity: ScalingSeverity::Medium,
                message: format!(
                    "Pydantic model '{}' has {} fields (max allowed: {})",
                    qualify_name(&parsed.module_path, def),
                    field_count,
                    max_fields,
                ),
                file_path: Some(parsed.file_path.clone()),
                qualified_name: Some(qualify_name(&parsed.module_path, def)),
                suggestion: Some(
                    "Consider splitting the model into smaller sub-models or simplifying its schema"
                        .to_string(),
                ),
                category: Some("model_max_fields".to_string()),
            });
        }

        if let Some(max_validators) = thresholds.max_validators_per_model
            && let Some(validator_count) = def.validator_count
            && validator_count > max_validators
        {
            report.violations.push(ScalingViolation {
                scope: ScopeKind::Dependency,
                severity: ScalingSeverity::Medium,
                message: format!(
                    "Pydantic model '{}' defines {} validators (max allowed: {})",
                    qualify_name(&parsed.module_path, def),
                    validator_count,
                    max_validators,
                ),
                file_path: Some(parsed.file_path.clone()),
                qualified_name: Some(qualify_name(&parsed.module_path, def)),
                suggestion: Some(
                    "Reduce validator count by consolidating logic or moving heavy checks into services"
                        .to_string(),
                ),
                category: Some("model_max_validators".to_string()),
            });
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CallPattern {
    pub pattern: String,

    #[serde(default)]
    pub is_prefix_match: bool,

    #[serde(default = "default_high")]
    pub severity: ScalingSeverity,

    #[serde(default)]
    pub category: Option<String>,

    #[serde(default)]
    pub suggestion: Option<String>,

    #[serde(default)]
    pub allowed_scopes: Vec<ScopeKind>,

    #[serde(default)]
    pub forbidden_scopes: Vec<ScopeKind>,
}

#[derive(Debug, Clone, Deserialize, Serialize, Default)]
pub struct EndpointThresholds {
    #[serde(default)]
    pub max_sync_endpoints: Option<usize>,

    #[serde(default)]
    pub max_endpoints_per_module: Option<usize>,

    #[serde(default)]
    pub max_endpoints_per_router: Option<usize>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct EndpointRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub warn_on_sync_handlers: bool,

    #[serde(default = "default_medium")]
    pub sync_handler_severity: ScalingSeverity,

    #[serde(default)]
    pub blocking_calls: Vec<CallPattern>,

    #[serde(default)]
    pub cpu_bound_calls: Vec<CallPattern>,

    #[serde(default)]
    pub thresholds: EndpointThresholds,
}

impl Default for EndpointRules {
    fn default() -> Self {
        Self {
            enabled: true,
            warn_on_sync_handlers: true,
            sync_handler_severity: default_medium(),
            blocking_calls: Vec::new(),
            cpu_bound_calls: Vec::new(),
            thresholds: EndpointThresholds::default(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ResourceKindRule {
    pub kind: String,

    #[serde(default)]
    pub create_call_patterns: Vec<CallPattern>,

    #[serde(default)]
    pub module_prefixes: Vec<String>,

    #[serde(default)]
    pub allowed_scopes: Vec<ScopeKind>,

    #[serde(default = "default_high")]
    pub severity_outside_allowed: ScalingSeverity,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DependencyRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub resources: Vec<ResourceKindRule>,

    #[serde(default)]
    pub require_yield_for_kinds: Vec<String>,

    #[serde(default)]
    pub forbid_inline_resources_in_endpoints: Vec<String>,
}

impl Default for DependencyRules {
    fn default() -> Self {
        Self {
            enabled: true,
            resources: Vec::new(),
            require_yield_for_kinds: Vec::new(),
            forbid_inline_resources_in_endpoints: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct LifespanRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub require_lifespan_for_kinds: Vec<String>,

    #[serde(default)]
    pub ignore_modules: Vec<String>,
}

impl Default for LifespanRules {
    fn default() -> Self {
        Self {
            enabled: true,
            require_lifespan_for_kinds: Vec::new(),
            ignore_modules: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Default)]
pub struct RouterThresholds {
    #[serde(default)]
    pub max_endpoints_per_module: Option<usize>,

    #[serde(default)]
    pub max_endpoints_per_router: Option<usize>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RouterRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub warn_on_direct_app_routes: bool,

    #[serde(default = "default_medium")]
    pub direct_app_route_severity: ScalingSeverity,

    #[serde(default)]
    pub thresholds: RouterThresholds,

    #[serde(default)]
    pub allowed_direct_route_modules: Vec<String>,
}

impl Default for RouterRules {
    fn default() -> Self {
        Self {
            enabled: true,
            warn_on_direct_app_routes: true,
            direct_app_route_severity: default_medium(),
            thresholds: RouterThresholds::default(),
            allowed_direct_route_modules: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MiddlewareRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub warn_on_base_http_middleware: bool,

    #[serde(default = "default_medium")]
    pub base_http_middleware_severity: ScalingSeverity,

    #[serde(default)]
    pub max_middleware_layers: Option<usize>,

    #[serde(default)]
    pub blocking_calls: Vec<CallPattern>,
}

impl Default for MiddlewareRules {
    fn default() -> Self {
        Self {
            enabled: true,
            warn_on_base_http_middleware: true,
            base_http_middleware_severity: default_medium(),
            max_middleware_layers: None,
            blocking_calls: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct JobQueuePattern {
    pub name: String,
    pub package: String,

    #[serde(default)]
    pub enqueue_functions: Vec<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct BackgroundTaskRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub heavy_call_patterns: Vec<CallPattern>,

    #[serde(default)]
    pub job_queues: Vec<JobQueuePattern>,

    #[serde(default)]
    pub prefer_job_queues_for_heavy_tasks: bool,
}

impl Default for BackgroundTaskRules {
    fn default() -> Self {
        Self {
            enabled: true,
            heavy_call_patterns: Vec::new(),
            job_queues: Vec::new(),
            prefer_job_queues_for_heavy_tasks: true,
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Default)]
pub struct ModelThresholds {
    #[serde(default)]
    pub max_fields_per_model: Option<usize>,

    #[serde(default)]
    pub max_nested_model_depth: Option<usize>,

    #[serde(default)]
    pub max_validators_per_model: Option<usize>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ModelRules {
    #[serde(default = "default_true")]
    pub enabled: bool,

    #[serde(default)]
    pub thresholds: ModelThresholds,

    #[serde(default)]
    pub allowlist: Vec<String>,
}

impl Default for ModelRules {
    fn default() -> Self {
        Self {
            enabled: true,
            thresholds: ModelThresholds::default(),
            allowlist: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackgroundTaskInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub heavy_call: String,
    pub matched_pattern: String,
    pub enqueued_via_job_queue: bool,
    pub is_inline_heavy_call: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QualifiedLocation {
    pub qualified_name: String,
    pub file_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LifespanResourceUsage {
    pub resource_kind: String,
    pub module: String,
    pub first_usage: QualifiedLocation,
    pub has_lifespan_handler: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MiddlewareInfo {
    pub qualified_name: String,
    pub file_path: String,
    pub router_name: Option<String>,
    pub is_async: bool,
    pub line_start: usize,
    pub line_end: usize,
    #[serde(default)]
    pub blocking_calls: Vec<BlockingCallHit>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockingCallHit {
    pub callee: String,
    pub pattern: String,
    pub category: Option<String>,
    pub severity: ScalingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SideEffectInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub callee: String,
    pub category: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthWiringInfo {
    pub qualified_name: String,
    pub file_path: String,
    pub has_security_dependency: bool,
    pub security_dependency_count: usize,
    #[serde(default)]
    pub security_dependencies: Vec<String>,
    #[serde(default)]
    pub has_oauth2_provider: bool,
    #[serde(default)]
    pub has_jwt: bool,
    #[serde(default)]
    pub jwt_calls: Vec<String>,
    #[serde(default)]
    pub has_permission_checks: bool,
    #[serde(default)]
    pub permission_dependencies: Vec<String>,
    #[serde(default)]
    pub has_custom_exception_handler: bool,
    pub has_http_exception: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExternalCallInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub callee: String,
    pub pattern: String,
    pub category: Option<String>,
    pub severity: ScalingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DbQueryInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub callee: String,
    pub pattern: String,
    pub category: Option<String>,
    pub severity: ScalingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnvAccessInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub callee: String,
    pub pattern: String,
    pub category: Option<String>,
    pub severity: ScalingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigEnvHit {
    pub callee: String,
    pub pattern: String,
    pub category: Option<String>,
    pub severity: ScalingSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigEnvLink {
    pub settings_name: String,
    pub file_path: String,
    pub env_hits: Vec<ConfigEnvHit>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestLinkInsight {
    pub endpoint: String,
    pub endpoint_file: String,
    pub test_caller: String,
    pub test_file: String,
    pub call_line: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DbPatternInsight {
    pub qualified_name: String,
    pub file_path: String,
    pub callee: String,
    pub category: String,
    pub severity: ScalingSeverity,
}

fn build_middleware_stack(
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    policy: &FastapiScalingPolicy,
) -> Vec<MiddlewareInfo> {
    let mut entries: Vec<MiddlewareInfo> = definitions
        .iter()
        .filter(|parsed| parsed.definition.roles.contains(&FastapiRole::Middleware))
        .map(|parsed| {
            let def = &parsed.definition;
            let qualified = qualify_name(&parsed.module_path, def);
            let router = router_tag(def).map(|r| r.to_string());
            let edges = call_graph.get_outgoing_edges(&qualified);

            let mut blocking_calls: Vec<BlockingCallHit> = Vec::new();
            for edge in edges {
                let callee = &edge.callee;
                for pattern in &policy.middleware.blocking_calls {
                    if call_matches_pattern(callee, pattern) && scope_violates_pattern(ScopeKind::Middleware, pattern) {
                        blocking_calls.push(BlockingCallHit {
                            callee: callee.clone(),
                            pattern: pattern.pattern.clone(),
                            category: pattern.category.clone(),
                            severity: pattern.severity,
                        });
                    }
                }
            }

            MiddlewareInfo {
                qualified_name: qualified,
                file_path: parsed.file_path.clone(),
                router_name: router,
                is_async: def.is_async,
                line_start: def.line_start,
                line_end: def.line_end,
                blocking_calls,
            }
        })
        .collect();

    entries.sort_by(|a, b| {
        a.file_path
            .cmp(&b.file_path)
            .then_with(|| a.line_start.cmp(&b.line_start))
            .then_with(|| a.qualified_name.cmp(&b.qualified_name))
    });

    entries
}

fn analyze_side_effects(
    definitions: &[ParsedDefinition],
    call_graph: &CallGraph,
    report: &mut FastapiScalingReport,
) {
    const COMMIT_CALLEES: &[&str] = &["session.commit", "Session.commit"];

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let edges = call_graph.get_outgoing_edges(&qualified);

        for edge in edges {
            let callee = &edge.callee;
            if COMMIT_CALLEES.iter().any(|c| callee == *c) {
                report.side_effects.push(SideEffectInsight {
                    qualified_name: qualified.clone(),
                    file_path: parsed.file_path.clone(),
                    callee: callee.clone(),
                    category: "commit".to_string(),
                });
            }
        }
    }
}

fn default_policy_path(project_root: &Path) -> PathBuf {
    project_root.join(".ranex").join("fastapi_scaling.yaml")
}

impl FastapiScalingPolicy {
    pub fn load(project_root: &Path) -> Result<Self, AtlasError> {
        let path = default_policy_path(project_root);

        if !path.exists() {
            return Ok(FastapiScalingPolicy::default());
        }

        let contents = std::fs::read_to_string(&path).map_err(|e| AtlasError::AnalysisConfig {
            path: path.clone(),
            message: e.to_string(),
        })?;

        let policy: FastapiScalingPolicy =
            serde_yaml::from_str(&contents).map_err(|e| AtlasError::AnalysisConfig {
                path: path.clone(),
                message: e.to_string(),
            })?;

        Ok(policy)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn load_missing_policy_returns_default() -> Result<(), Box<dyn Error>> {
        let temp = TempDir::new()?;
        let policy = FastapiScalingPolicy::load(temp.path())?;
        assert_eq!(policy.version, "1.0");
        assert!(policy.enabled);
        Ok(())
    }

    #[test]
    fn load_policy_parses_yaml() -> Result<(), Box<dyn Error>> {
        let temp = TempDir::new()?;
        let config_dir = temp.path().join(".ranex");
        fs::create_dir_all(&config_dir)?;
        let path = config_dir.join("fastapi_scaling.yaml");

        let yaml = r#"version: "2.0"
endpoints:
  enabled: false
"#;

        fs::write(&path, yaml)?;

        let policy = FastapiScalingPolicy::load(temp.path())?;
        assert_eq!(policy.version, "2.0");
        assert!(!policy.endpoints.enabled);
        Ok(())
    }

    #[test]
    fn analyze_routers_warns_on_direct_app_routes_outside_allowlist() {
        use crate::analysis::call_graph::CallGraph;
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();
        policy.routers.warn_on_direct_app_routes = true;
        policy.routers.allowed_direct_route_modules = vec!["app.exceptions".to_string()];

        let direct_app_endpoint = DefinitionInfo {
            name: "read_main".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec![
                "fastapi_route".to_string(),
                "http_get".to_string(),
                "router_app".to_string(),
            ],
            route_path: Some("/".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let router_endpoint = DefinitionInfo {
            name: "read_item".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec![
                "fastapi_route".to_string(),
                "http_get".to_string(),
                "router_api".to_string(),
            ],
            route_path: Some("/items/{item_id}".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![
            ParsedDefinition {
                definition: direct_app_endpoint,
                file_path: "app/main.py".to_string(),
                module_path: "app.main".to_string(),
            },
            ParsedDefinition {
                definition: router_endpoint,
                file_path: "app/api.py".to_string(),
                module_path: "app.api".to_string(),
            },
        ];

        let call_graph = CallGraph::new();
        let report = analyze_definitions(&policy, &defs, &call_graph);

        let direct_route_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("direct_app_route"))
            .collect();

        assert_eq!(direct_route_violations.len(), 1);

        let direct_route_violation = match direct_route_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one direct_app_route violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert_eq!(
            direct_route_violation
                .qualified_name
                .as_deref(),
            Some("app.main.read_main"),
        );
    }

    #[test]
    fn analyze_definitions_counts_endpoints_and_sync_violations() {
        use crate::analysis::call_graph::CallGraph;
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();
        policy.endpoints.warn_on_sync_handlers = true;
        policy.endpoints.thresholds.max_sync_endpoints = Some(0);

        let endpoint_def = DefinitionInfo {
            name: "read_item".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: false,
            tags: vec!["fastapi_route".to_string(), "http_get".to_string()],
            route_path: Some("/items/{item_id}".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![ParsedDefinition {
            definition: endpoint_def,
            file_path: "app/api/items.py".to_string(),
            module_path: "app.api.items".to_string(),
        }];

        let call_graph = CallGraph::new();
        let report = analyze_definitions(&policy, &defs, &call_graph);

        assert_eq!(report.stats.total_definitions, 1);
        assert_eq!(report.stats.total_endpoints, 1);
        assert_eq!(report.stats.sync_endpoints, 1);
        assert_eq!(report.stats.async_endpoints, 0);
        assert_eq!(report.violations.len(), 2);

        // One violation for sync handler, one for exceeding max_sync_endpoints
        assert!(report
            .violations
            .iter()
            .any(|v| v.category.as_deref() == Some("sync_handler")));
        assert!(report
            .violations
            .iter()
            .any(|v| v.category.as_deref() == Some("threshold_sync_endpoints")));
    }

    #[test]
    fn analyze_models_applies_thresholds() {
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();
        policy.models.thresholds.max_fields_per_model = Some(2);
        policy.models.thresholds.max_validators_per_model = Some(0);

        let model_def = DefinitionInfo {
            name: "User".to_string(),
            def_type: DefinitionType::Class,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: false,
            tags: vec!["pydantic_model".to_string()],
            route_path: None,
            router_prefix: None,
            base_classes: vec!["BaseModel".to_string()],
            params: Vec::new(),
            has_yield: false,
            roles: Vec::new(),
            field_count: Some(3),
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: Some(1),
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![ParsedDefinition {
            definition: model_def,
            file_path: "app/models.py".to_string(),
            module_path: "app".to_string(),
        }];

        let call_graph = CallGraph::new();
        let report = analyze_definitions(&policy, &defs, &call_graph);

        assert_eq!(report.stats.total_definitions, 1);
        assert_eq!(report.violations.len(), 2);

        assert!(report
            .violations
            .iter()
            .any(|v| v.category.as_deref() == Some("model_max_fields")));
        assert!(report
            .violations
            .iter()
            .any(|v| v.category.as_deref() == Some("model_max_validators")));
    }

    #[test]
    fn analyze_dependencies_enforces_inline_and_yield_rules() {
        use crate::analysis::call_graph::{CallGraph, CallType};
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();

        policy.dependencies.resources = vec![ResourceKindRule {
            kind: "db_session".to_string(),
            create_call_patterns: vec![CallPattern {
                pattern: "db.create_session".to_string(),
                is_prefix_match: false,
                severity: ScalingSeverity::High,
                category: Some("db_session_create".to_string()),
                suggestion: None,
                allowed_scopes: Vec::new(),
                forbidden_scopes: Vec::new(),
            }],
            module_prefixes: Vec::new(),
            allowed_scopes: Vec::new(),
            severity_outside_allowed: ScalingSeverity::High,
        }];

        policy.dependencies.require_yield_for_kinds = vec!["db_session".to_string()];
        policy
            .dependencies
            .forbid_inline_resources_in_endpoints = vec!["db_session".to_string()];

        // Endpoint that creates the resource inline
        let endpoint_def = DefinitionInfo {
            name: "read_item".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec!["fastapi_route".to_string(), "http_get".to_string()],
            route_path: Some("/items/{item_id}".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        // Dependency-like function that creates the same resource but does not yield
        let dependency_def = DefinitionInfo {
            name: "get_db".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 5,
            is_async: false,
            tags: Vec::new(),
            route_path: None,
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: Vec::new(),
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![
            ParsedDefinition {
                definition: endpoint_def,
                file_path: "app/api/items.py".to_string(),
                module_path: "app.api.items".to_string(),
            },
            ParsedDefinition {
                definition: dependency_def,
                file_path: "app/db.py".to_string(),
                module_path: "app.db".to_string(),
            },
        ];

        let mut call_graph = CallGraph::new();

        // Endpoint creates the resource inline
        call_graph.add_call(
            "app.api.items.read_item",
            "db.create_session",
            CallType::Direct,
            10,
            "app/api/items.py",
        );

        // Dependency also creates the resource
        call_graph.add_call(
            "app.db.get_db",
            "db.create_session",
            CallType::Direct,
            5,
            "app/db.py",
        );

        let report = analyze_definitions(&policy, &defs, &call_graph);

        // Expect both an inline resource violation on the endpoint and a
        // missing-yield violation on the dependency-like function.
        let inline_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("inline_resource_in_endpoint"))
            .collect();
        assert_eq!(inline_violations.len(), 1);

        let inline_violation = match inline_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one inline_resource_in_endpoint violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert_eq!(
            inline_violation
                .qualified_name
                .as_deref(),
            Some("app.api.items.read_item"),
        );

        let yield_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("resource_missing_yield"))
            .collect();
        assert_eq!(yield_violations.len(), 1);

        let yield_violation = match yield_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one resource_missing_yield violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert_eq!(
            yield_violation
                .qualified_name
                .as_deref(),
            Some("app.db.get_db"),
        );
    }

    #[test]
    fn analyze_lifespan_requires_handlers_for_resource_kinds() {
        use crate::analysis::call_graph::{CallGraph, CallType};
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();

        policy.dependencies.resources = vec![ResourceKindRule {
            kind: "cache_client".to_string(),
            create_call_patterns: vec![CallPattern {
                pattern: "cache.create_client".to_string(),
                is_prefix_match: false,
                severity: ScalingSeverity::Medium,
                category: Some("cache_client_create".to_string()),
                suggestion: None,
                allowed_scopes: Vec::new(),
                forbidden_scopes: Vec::new(),
            }],
            module_prefixes: Vec::new(),
            allowed_scopes: Vec::new(),
            severity_outside_allowed: ScalingSeverity::Medium,
        }];

        policy
            .lifespan
            .require_lifespan_for_kinds = vec!["cache_client".to_string()];

        // Function in app.cache that creates the cache client but module has no lifespan
        let cache_def = DefinitionInfo {
            name: "get_cache".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 5,
            is_async: false,
            tags: Vec::new(),
            route_path: None,
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: Vec::new(),
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![ParsedDefinition {
            definition: cache_def,
            file_path: "app/cache.py".to_string(),
            module_path: "app.cache".to_string(),
        }];

        let mut call_graph = CallGraph::new();
        call_graph.add_call(
            "app.cache.get_cache",
            "cache.create_client",
            CallType::Direct,
            3,
            "app/cache.py",
        );

        let report = analyze_definitions(&policy, &defs, &call_graph);

        let lifespan_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("missing_lifespan_for_resource"))
            .collect();

        assert_eq!(lifespan_violations.len(), 1);

        let lifespan_violation = match lifespan_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one missing_lifespan_for_resource violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert!(lifespan_violation
            .message
            .contains("app.cache")
            && lifespan_violation
                .message
                .contains("cache_client"));
    }

    #[test]
    fn analyze_middleware_applies_max_layers_and_base_http_rule() {
        use crate::analysis::call_graph::CallGraph;
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();
        policy.middleware.warn_on_base_http_middleware = true;
        policy.middleware.max_middleware_layers = Some(1);

        // BaseHTTPMiddleware subclass
        let base_middleware = DefinitionInfo {
            name: "AuthMiddleware".to_string(),
            def_type: DefinitionType::Class,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: false,
            tags: Vec::new(),
            route_path: None,
            router_prefix: None,
            base_classes: vec!["BaseHTTPMiddleware".to_string()],
            params: Vec::new(),
            has_yield: false,
            roles: Vec::new(),
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        // Two function-based middleware layers
        let fn_middleware_1 = DefinitionInfo {
            name: "log_requests".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec!["fastapi_middleware".to_string(), "router_app".to_string()],
            route_path: None,
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Middleware],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let fn_middleware_2 = DefinitionInfo {
            name: "add_security_headers".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec!["fastapi_middleware".to_string(), "router_app".to_string()],
            route_path: None,
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Middleware],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![
            ParsedDefinition {
                definition: base_middleware,
                file_path: "app/middleware.py".to_string(),
                module_path: "app.middleware".to_string(),
            },
            ParsedDefinition {
                definition: fn_middleware_1,
                file_path: "app/middleware.py".to_string(),
                module_path: "app.middleware".to_string(),
            },
            ParsedDefinition {
                definition: fn_middleware_2,
                file_path: "app/middleware.py".to_string(),
                module_path: "app.middleware".to_string(),
            },
        ];

        let call_graph = CallGraph::new();
        let report = analyze_definitions(&policy, &defs, &call_graph);

        let base_http_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("base_http_middleware"))
            .collect();
        assert_eq!(base_http_violations.len(), 1);

        let base_http_violation = match base_http_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one base_http_middleware violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert_eq!(
            base_http_violation
                .qualified_name
                .as_deref(),
            Some("app.middleware.AuthMiddleware"),
        );

        let layer_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("max_middleware_layers"))
            .collect();
        assert_eq!(layer_violations.len(), 1);
    }

    #[test]
    fn analyze_background_tasks_enforces_prefer_job_queues() {
        use crate::analysis::call_graph::{CallGraph, CallType};
        use crate::parser::DefinitionType;

        let mut policy = FastapiScalingPolicy::default();
        policy.background_tasks.heavy_call_patterns = vec![CallPattern {
            pattern: "heavy_op.run".to_string(),
            is_prefix_match: false,
            severity: ScalingSeverity::High,
            category: Some("heavy_op".to_string()),
            suggestion: None,
            allowed_scopes: Vec::new(),
            forbidden_scopes: Vec::new(),
        }];
        policy.background_tasks.job_queues = vec![JobQueuePattern {
            name: "rq".to_string(),
            package: "rq".to_string(),
            enqueue_functions: vec!["enqueue".to_string()],
        }];
        policy.background_tasks.prefer_job_queues_for_heavy_tasks = true;

        // Endpoint that calls the heavy operation directly, no job queue
        let endpoint_def = DefinitionInfo {
            name: "process".to_string(),
            def_type: DefinitionType::Function,
            signature: None,
            docstring: None,
            line_start: 1,
            line_end: 10,
            is_async: true,
            tags: vec!["fastapi_route".to_string(), "http_post".to_string()],
            route_path: Some("/process".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: Vec::new(),
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let defs = vec![ParsedDefinition {
            definition: endpoint_def,
            file_path: "app/api/jobs.py".to_string(),
            module_path: "app.api.jobs".to_string(),
        }];

        let mut call_graph = CallGraph::new();
        call_graph.add_call(
            "app.api.jobs.process",
            "heavy_op.run",
            CallType::Direct,
            5,
            "app/api/jobs.py",
        );

        let report = analyze_definitions(&policy, &defs, &call_graph);

        let heavy_violations: Vec<_> = report
            .violations
            .iter()
            .filter(|v| v.category.as_deref() == Some("heavy_op"))
            .collect();

        assert_eq!(heavy_violations.len(), 1);

        let heavy_violation = match heavy_violations.as_slice() {
            [v] => v,
            slice => {
                assert!(
                    slice.len() == 1,
                    "expected exactly one heavy_op violation, got {}",
                    slice.len()
                );
                return;
            }
        };

        assert_eq!(
            heavy_violation
                .qualified_name
                .as_deref(),
            Some("app.api.jobs.process"),
        );
    }
}
