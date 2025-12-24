use ranex_core::{Artifact, ArtifactKind};
use std::collections::{HashMap, HashSet};

use crate::analysis::CallEdge;

#[derive(Clone)]
struct ArtifactNode {
    qualified_name: String,
    module_path: String,
    direct_dependencies: Vec<String>,
}

struct Resolver {
    nodes: Vec<ArtifactNode>,
    by_symbol: HashMap<String, Vec<usize>>,
    by_qualified: HashMap<String, usize>,
}

impl Resolver {
    fn new(artifacts: &[Artifact]) -> Self {
        let mut nodes = Vec::with_capacity(artifacts.len());
        let mut by_symbol: HashMap<String, Vec<usize>> = HashMap::new();
        let mut by_qualified: HashMap<String, usize> = HashMap::new();

        for (idx, a) in artifacts.iter().enumerate() {
            nodes.push(ArtifactNode {
                qualified_name: a.qualified_name.clone(),
                module_path: a.module_path.clone(),
                direct_dependencies: a.direct_dependencies.iter().map(|d| normalize_target(d)).collect(),
            });

            by_symbol.entry(a.symbol_name.clone()).or_default().push(idx);
            by_qualified.insert(a.qualified_name.clone(), idx);
        }

        Self {
            nodes,
            by_symbol,
            by_qualified,
        }
    }

    fn resolve(&self, root_module: &str, target: &str) -> Option<usize> {
        let target = normalize_target(target);

        if target.contains('.') {
            if let Some(idx) = self.by_qualified.get(&target) {
                return Some(*idx);
            }

            let last = target.rsplit('.').next()?;

            let candidates = self.by_symbol.get(last)?;

            let mut filtered: Vec<usize> = candidates
                .iter()
                .copied()
                .filter(|idx| {
                    let Some(node) = self.nodes.get(*idx) else {
                        return false;
                    };
                    node.qualified_name.ends_with(&target)
                })
                .collect();

            if filtered.is_empty() {
                return None;
            }

            filtered.sort_by(|a, b| {
                let sa = self
                    .nodes
                    .get(*a)
                    .map(|n| common_prefix_len(root_module, &n.module_path))
                    .unwrap_or(0);
                let sb = self
                    .nodes
                    .get(*b)
                    .map(|n| common_prefix_len(root_module, &n.module_path))
                    .unwrap_or(0);

                let qa = self
                    .nodes
                    .get(*a)
                    .map(|n| n.qualified_name.as_str())
                    .unwrap_or("");
                let qb = self
                    .nodes
                    .get(*b)
                    .map(|n| n.qualified_name.as_str())
                    .unwrap_or("");
                sb.cmp(&sa)
                    .then_with(|| qa.cmp(qb))
            });

            return filtered.first().copied();
        }

        let candidates = self.by_symbol.get(&target)?;

        if candidates.len() == 1 {
            return candidates.first().copied();
        }

        let mut ordered = candidates.clone();
        ordered.sort_by(|a, b| {
            let sa = self
                .nodes
                .get(*a)
                .map(|n| common_prefix_len(root_module, &n.module_path))
                .unwrap_or(0);
            let sb = self
                .nodes
                .get(*b)
                .map(|n| common_prefix_len(root_module, &n.module_path))
                .unwrap_or(0);

            let qa = self
                .nodes
                .get(*a)
                .map(|n| n.qualified_name.as_str())
                .unwrap_or("");
            let qb = self
                .nodes
                .get(*b)
                .map(|n| n.qualified_name.as_str())
                .unwrap_or("");
            sb.cmp(&sa)
                .then_with(|| qa.cmp(qb))
        });

        ordered.first().copied()
    }
}

pub fn expand_dependency_chains(artifacts: &mut [Artifact]) {
    let resolver = Resolver::new(artifacts);

    for artifact in artifacts {
        if artifact.direct_dependencies.is_empty() {
            continue;
        }

        let root_module = artifact.module_path.clone();

        let mut chain: Vec<String> = Vec::new();
        let mut seen: HashSet<String> = HashSet::new();
        let mut visiting: HashSet<String> = HashSet::new();
        let mut ctx = ExpandContext {
            root_module: &root_module,
            max_depth: 25,
            chain: &mut chain,
            seen: &mut seen,
            visiting: &mut visiting,
        };

        let direct: Vec<String> = artifact
            .direct_dependencies
            .iter()
            .map(|d| normalize_target(d))
            .collect();

        for dep in direct {
            expand_target(&resolver, &dep, 0, &mut ctx);
        }

        artifact.dependency_chain = chain;
    }
}

pub fn highlight_auth_enforcement(artifacts: &mut [Artifact], call_edges: &[CallEdge]) {
    let resolver = Resolver::new(artifacts);

    let mut raises_http_exception: HashSet<String> = HashSet::new();
    for edge in call_edges {
        if edge.callee == "HTTPException" || edge.callee.ends_with(".HTTPException") {
            raises_http_exception.insert(edge.caller.clone());
        }
    }

    for artifact in artifacts {
        if artifact.kind != ArtifactKind::Endpoint {
            continue;
        }

        let has_security = !artifact.security_dependencies.is_empty();

        let mut enforced_by: Vec<String> = Vec::new();
        let root_module = artifact.module_path.clone();

        for dep in artifact.dependency_chain.iter().map(|d| normalize_target(d)) {
            let Some(idx) = resolver.resolve(&root_module, &dep) else {
                continue;
            };
            let Some(node) = resolver.nodes.get(idx) else {
                continue;
            };
            let q = &node.qualified_name;
            if raises_http_exception.contains(q) {
                enforced_by.push(dep);
            }
        }

        let has_http_exception = !enforced_by.is_empty();
        if !has_security && !has_http_exception {
            continue;
        }

        add_tag_if_missing(artifact, "auth_enforced");
        if has_security {
            add_tag_if_missing(artifact, "auth_security");
        }
        if has_http_exception {
            add_tag_if_missing(artifact, "auth_http_exception");
            for dep in enforced_by {
                add_tag_if_missing(artifact, &format!("auth_enforced_by:{}", dep));
            }
        }
    }
}

struct ExpandContext<'a> {
    root_module: &'a str,
    max_depth: usize,
    chain: &'a mut Vec<String>,
    seen: &'a mut HashSet<String>,
    visiting: &'a mut HashSet<String>,
}

fn expand_target(resolver: &Resolver, target: &str, depth: usize, ctx: &mut ExpandContext<'_>) {
    if depth >= ctx.max_depth {
        return;
    }

    let target = normalize_target(target);

    let resolved_key = resolver
        .resolve(ctx.root_module, &target)
        .and_then(|idx| resolver.nodes.get(idx).map(|n| n.qualified_name.clone()))
        .unwrap_or_else(|| target.clone());

    if ctx.visiting.contains(&resolved_key) {
        return;
    }

    if ctx.seen.insert(target.clone()) {
        ctx.chain.push(target.clone());
    }

    let Some(idx) = resolver.resolve(ctx.root_module, &target) else {
        return;
    };

    ctx.visiting.insert(resolved_key.clone());

    let Some(node) = resolver.nodes.get(idx) else {
        ctx.visiting.remove(&resolved_key);
        return;
    };

    let deps = node.direct_dependencies.clone();
    for dep in deps {
        expand_target(resolver, &dep, depth + 1, ctx);
    }

    ctx.visiting.remove(&resolved_key);
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

fn normalize_target(target: &str) -> String {
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

fn add_tag_if_missing(artifact: &mut Artifact, tag: &str) {
    if artifact.tags.iter().any(|t| t == tag) {
        return;
    }
    artifact.tags.push(tag.to_string());
}
