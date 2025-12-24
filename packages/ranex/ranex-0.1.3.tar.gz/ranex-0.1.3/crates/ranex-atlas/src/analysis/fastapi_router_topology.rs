use crate::analysis::fastapi_scaling::ParsedDefinition;
use crate::parser::{DefinitionInfo, FastapiRole};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

fn is_endpoint(def: &DefinitionInfo) -> bool {
    def.roles.contains(&FastapiRole::Endpoint) || def.tags.iter().any(|t| t == "fastapi_route")
}

fn router_tag(def: &DefinitionInfo) -> Option<&str> {
    for tag in &def.tags {
        if let Some(router) = tag.strip_prefix("router_") && !router.is_empty() {
            return Some(router);
        }
    }
    None
}

fn http_methods(def: &DefinitionInfo) -> Vec<String> {
    let mut methods: Vec<String> = def
        .tags
        .iter()
        .filter_map(|t| t.strip_prefix("http_").map(|m| m.to_string()))
        .collect();
    methods.sort();
    methods.dedup();
    methods
}

fn qualify_name(module_path: &str, def: &DefinitionInfo) -> String {
    format!("{}.{}", module_path, def.name)
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct RouterTopologyReport {
    pub routers: Vec<RouterInfo>,
    pub direct_app_routes: Vec<RouteInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RouterInfo {
    pub name: String,
    pub prefix: Option<String>,
    pub modules: Vec<String>,
    pub includes: Vec<String>,
    pub endpoints: Vec<RouteInfo>,
    pub is_app: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RouteInfo {
    pub qualified_name: String,
    pub file_path: String,
    pub http_methods: Vec<String>,
    pub route_path: Option<String>,
    pub router_prefix: Option<String>,
}

struct RouterBuilder {
    name: String,
    prefix: Option<String>,
    modules: HashSet<String>,
    includes: HashSet<String>,
    endpoints: Vec<RouteInfo>,
    is_app: bool,
}

impl RouterBuilder {
    fn into_info(mut self) -> RouterInfo {
        self.endpoints
            .sort_by(|a, b| a.qualified_name.cmp(&b.qualified_name));
        let mut modules: Vec<String> = self.modules.into_iter().collect();
        modules.sort();
        let mut includes: Vec<String> = self.includes.into_iter().collect();
        includes.sort();

        RouterInfo {
            name: self.name,
            prefix: self.prefix,
            modules,
            includes,
            endpoints: self.endpoints,
            is_app: self.is_app,
        }
    }
}

pub fn analyze_router_topology(definitions: &[ParsedDefinition]) -> RouterTopologyReport {
    let mut routers: HashMap<String, RouterBuilder> = HashMap::new();
    let mut direct_app_routes: Vec<RouteInfo> = Vec::new();

    for parsed in definitions {
        let def = &parsed.definition;
        if !is_endpoint(def) {
            continue;
        }

        let qualified = qualify_name(&parsed.module_path, def);
        let route = RouteInfo {
            qualified_name: qualified,
            file_path: parsed.file_path.clone(),
            http_methods: http_methods(def),
            route_path: def.route_path.clone(),
            router_prefix: def.router_prefix.clone(),
        };

        let router_name = router_tag(def).unwrap_or("unscoped").to_string();
        let builder = routers.entry(router_name.clone()).or_insert_with(|| RouterBuilder {
            name: router_name.clone(),
            prefix: def.router_prefix.clone(),
            modules: HashSet::new(),
            includes: HashSet::new(),
            endpoints: Vec::new(),
            is_app: router_name == "app",
        });

        if builder.prefix.is_none() && def.router_prefix.is_some() {
            builder.prefix = def.router_prefix.clone();
        }

        builder.modules.insert(parsed.module_path.clone());
        builder.endpoints.push(route.clone());

        if builder.is_app {
            direct_app_routes.push(route);
        }
    }

    let mut router_names: Vec<String> = routers.keys().cloned().collect();
    router_names.sort();

    // Derive parent-child includes based on prefix nesting and ensure parent routers exist.
    for child_name in router_names.clone() {
        let child_prefix = routers
            .get(&child_name)
            .and_then(|r| r.prefix.clone())
            .unwrap_or_default();

        let mut parent_candidate: Option<String> = None;
        let mut best_len = 0usize;

        if !child_prefix.is_empty() {
            for (name, info) in &routers {
                if *name == child_name {
                    continue;
                }

                if let Some(prefix) = &info.prefix {
                    if prefix.is_empty() || prefix.len() > child_prefix.len() {
                        continue;
                    }
                    if child_prefix.starts_with(prefix) && prefix.len() > best_len {
                        best_len = prefix.len();
                        parent_candidate = Some(name.clone());
                    }
                }
            }
        }

        // Heuristic: if no parent found, derive one from the child's prefix path segments.
        if parent_candidate.is_none() && !child_prefix.is_empty() {
            let segments: Vec<&str> = child_prefix.split('/').filter(|s| !s.is_empty()).collect();
            if let Some((_, parents)) = segments.split_last() {
                let parent_prefix = format!("/{}", parents.join("/"));
                if let Some(parent_name) = parents.first().map(|s| s.to_string())
                    && !parent_name.is_empty()
                {
                    routers
                        .entry(parent_name.clone())
                        .or_insert_with(|| RouterBuilder {
                            name: parent_name.clone(),
                            prefix: Some(parent_prefix.clone()),
                            modules: HashSet::new(),
                            includes: HashSet::new(),
                            endpoints: Vec::new(),
                            is_app: parent_name == "app",
                        })
                        .prefix
                        .get_or_insert(parent_prefix);
                    parent_candidate = Some(parent_name);
                }
            }
        }

        if parent_candidate.is_none()
            && child_name != "app"
            && routers.contains_key("app")
        {
            parent_candidate = Some("app".to_string());
        }

        if let Some(parent) = parent_candidate
            && let Some(parent_router) = routers.get_mut(&parent)
        {
            parent_router.includes.insert(child_name);
        }
    }

    let mut routers_vec: Vec<RouterInfo> = routers
        .into_values()
        .map(RouterBuilder::into_info)
        .collect();
    routers_vec.sort_by(|a, b| a.name.cmp(&b.name));

    direct_app_routes.sort_by(|a, b| a.qualified_name.cmp(&b.qualified_name));

    RouterTopologyReport {
        routers: routers_vec,
        direct_app_routes,
    }
}
