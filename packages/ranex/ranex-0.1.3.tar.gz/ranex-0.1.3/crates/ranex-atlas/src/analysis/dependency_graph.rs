//! Dependency graph queries and traversal.
//!
//! Builds on the existing `imports` table to provide higher-level
//! dependency analysis: what files/modules depend on what.
//!
//! ## Design
//!
//! Unlike the call graph (function-to-function), the dependency graph
//! operates at the file/module level, using import relationships.
//!
//! ## Example
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::DependencyGraph;
//!
//! let graph = DependencyGraph::from_imports(&imports)?;
//!
//! // Get all files that import this module
//! let dependents = graph.get_dependents("app/commons/database.py");
//!
//! // Get all files this module imports
//! let dependencies = graph.get_dependencies("app/main.py");
//! ```

use ranex_core::ImportEdge;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

/// A node in the dependency graph (represents a file or module).
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct DependencyNode {
    /// File path (relative to project root).
    pub file_path: String,

    /// Module path (Python import path).
    pub module_path: Option<String>,
}

impl DependencyNode {
    /// Create a new dependency node.
    pub fn new(file_path: impl Into<String>) -> Self {
        Self {
            file_path: file_path.into(),
            module_path: None,
        }
    }

    /// Create with module path.
    pub fn with_module(file_path: impl Into<String>, module_path: impl Into<String>) -> Self {
        Self {
            file_path: file_path.into(),
            module_path: Some(module_path.into()),
        }
    }
}

/// File-level dependency graph.
///
/// Tracks which files import which other files, enabling:
/// - Impact analysis: "If I change X, what else might break?"
/// - Dependency cycles detection
/// - Layer violation detection
#[derive(Debug, Clone, Default)]
pub struct DependencyGraph {
    /// All import edges.
    edges: Vec<ImportEdge>,

    /// Index: target_file -> source_files (who imports this?).
    dependents: HashMap<String, HashSet<String>>,

    /// Index: source_file -> target_files (what does this import?).
    dependencies: HashMap<String, HashSet<String>>,
}

impl DependencyGraph {
    /// Create a new empty dependency graph.
    pub fn new() -> Self {
        Self::default()
    }

    /// Build from a list of import edges.
    pub fn from_edges(edges: impl IntoIterator<Item = ImportEdge>) -> Self {
        let mut graph = Self::new();
        for edge in edges {
            graph.add_edge(edge);
        }
        graph
    }

    /// Add an import edge to the graph.
    pub fn add_edge(&mut self, edge: ImportEdge) {
        let source = edge.source_file.clone();
        let target = edge.target_file.clone();

        // Update dependents index (reverse lookup)
        self.dependents
            .entry(target.clone())
            .or_default()
            .insert(source.clone());

        // Update dependencies index (forward lookup)
        self.dependencies.entry(source).or_default().insert(target);

        self.edges.push(edge);
    }

    /// Get all files that import the given file (direct dependents).
    pub fn get_dependents(&self, file_path: &str) -> Vec<&str> {
        self.dependents
            .get(file_path)
            .map(|set| set.iter().map(String::as_str).collect())
            .unwrap_or_default()
    }

    /// Get all files that the given file imports (direct dependencies).
    pub fn get_dependencies(&self, file_path: &str) -> Vec<&str> {
        self.dependencies
            .get(file_path)
            .map(|set| set.iter().map(String::as_str).collect())
            .unwrap_or_default()
    }

    /// Get transitive dependents (all files that eventually depend on this one).
    pub fn get_transitive_dependents(&self, file_path: &str, max_depth: usize) -> Vec<String> {
        let mut visited = HashSet::new();
        let mut queue = std::collections::VecDeque::new();
        let mut result = Vec::new();

        queue.push_back((file_path.to_string(), 0));
        visited.insert(file_path.to_string());

        while let Some((current, depth)) = queue.pop_front() {
            if depth >= max_depth {
                continue;
            }

            if let Some(dependents) = self.dependents.get(&current) {
                for dependent in dependents {
                    if visited.insert(dependent.clone()) {
                        result.push(dependent.clone());
                        queue.push_back((dependent.clone(), depth + 1));
                    }
                }
            }
        }

        result
    }

    /// Get transitive dependencies (all files eventually imported by this one).
    pub fn get_transitive_dependencies(&self, file_path: &str, max_depth: usize) -> Vec<String> {
        let mut visited = HashSet::new();
        let mut queue = std::collections::VecDeque::new();
        let mut result = Vec::new();

        queue.push_back((file_path.to_string(), 0));
        visited.insert(file_path.to_string());

        while let Some((current, depth)) = queue.pop_front() {
            if depth >= max_depth {
                continue;
            }

            if let Some(deps) = self.dependencies.get(&current) {
                for dep in deps {
                    if visited.insert(dep.clone()) {
                        result.push(dep.clone());
                        queue.push_back((dep.clone(), depth + 1));
                    }
                }
            }
        }

        result
    }

    /// Detect cycles in the dependency graph.
    ///
    /// Returns a list of cycles found, where each cycle is a vector
    /// of file paths forming the cycle.
    pub fn detect_cycles(&self) -> Vec<Vec<String>> {
        let mut cycles = Vec::new();
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();
        let mut path = Vec::new();

        // Get all nodes
        let mut all_nodes: HashSet<&str> = HashSet::new();
        for (source, targets) in &self.dependencies {
            all_nodes.insert(source);
            for target in targets {
                all_nodes.insert(target);
            }
        }

        for node in all_nodes {
            if !visited.contains(node) {
                self.detect_cycles_dfs(node, &mut visited, &mut rec_stack, &mut path, &mut cycles);
            }
        }

        cycles
    }

    fn detect_cycles_dfs(
        &self,
        node: &str,
        visited: &mut HashSet<String>,
        rec_stack: &mut HashSet<String>,
        path: &mut Vec<String>,
        cycles: &mut Vec<Vec<String>>,
    ) {
        visited.insert(node.to_string());
        rec_stack.insert(node.to_string());
        path.push(node.to_string());

        if let Some(deps) = self.dependencies.get(node) {
            for dep in deps {
                if !visited.contains(dep.as_str()) {
                    self.detect_cycles_dfs(dep, visited, rec_stack, path, cycles);
                } else if rec_stack.contains(dep.as_str()) {
                    // Found a cycle - extract it from path
                    if let Some(start_idx) = path.iter().position(|p| p == dep)
                        && let Some(slice) = path.get(start_idx..)
                    {
                        let cycle: Vec<String> = slice.to_vec();
                        cycles.push(cycle);
                    }
                }
            }
        }

        path.pop();
        rec_stack.remove(node);
    }

    /// Get the number of edges in the graph.
    pub fn edge_count(&self) -> usize {
        self.edges.len()
    }

    /// Get the number of unique files (nodes).
    pub fn node_count(&self) -> usize {
        let mut nodes: HashSet<&str> = HashSet::new();
        for edge in &self.edges {
            nodes.insert(&edge.source_file);
            nodes.insert(&edge.target_file);
        }
        nodes.len()
    }

    /// Check if a file is in the graph.
    pub fn contains(&self, file_path: &str) -> bool {
        self.dependencies.contains_key(file_path) || self.dependents.contains_key(file_path)
    }

    /// Get all edges.
    pub fn edges(&self) -> &[ImportEdge] {
        &self.edges
    }

    /// Clear the graph.
    pub fn clear(&mut self) {
        self.edges.clear();
        self.dependents.clear();
        self.dependencies.clear();
    }

    /// Get all files with no dependents (root/entry points).
    pub fn get_root_files(&self) -> Vec<&str> {
        let mut roots = Vec::new();

        // Files that have dependencies but no dependents
        for file in self.dependencies.keys() {
            if !self.dependents.contains_key(file.as_str())
                || self
                    .dependents
                    .get(file.as_str())
                    .is_none_or(|s| s.is_empty())
            {
                roots.push(file.as_str());
            }
        }

        roots
    }

    /// Get all files with no dependencies (leaf nodes).
    pub fn get_leaf_files(&self) -> Vec<&str> {
        let mut leaves = Vec::new();

        // Files that are imported but don't import anything
        for file in self.dependents.keys() {
            if !self.dependencies.contains_key(file.as_str())
                || self
                    .dependencies
                    .get(file.as_str())
                    .is_none_or(|s| s.is_empty())
            {
                leaves.push(file.as_str());
            }
        }

        leaves
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ranex_core::ImportType;

    fn make_edge(source: &str, target: &str) -> ImportEdge {
        ImportEdge::new(
            source,
            target,
            format!("{}.{}", source, target),
            ImportType::Module,
            1,
        )
    }

    #[test]
    fn test_basic_dependency_tracking() {
        let mut graph = DependencyGraph::new();
        graph.add_edge(make_edge("main.py", "utils.py"));
        graph.add_edge(make_edge("main.py", "config.py"));
        graph.add_edge(make_edge("api.py", "utils.py"));

        // main.py imports 2 files
        let deps = graph.get_dependencies("main.py");
        assert_eq!(deps.len(), 2);

        // utils.py is imported by 2 files
        let dependents = graph.get_dependents("utils.py");
        assert_eq!(dependents.len(), 2);
    }

    #[test]
    fn test_transitive_dependents() {
        let mut graph = DependencyGraph::new();
        // Chain: app.py -> service.py -> repo.py -> db.py
        graph.add_edge(make_edge("app.py", "service.py"));
        graph.add_edge(make_edge("service.py", "repo.py"));
        graph.add_edge(make_edge("repo.py", "db.py"));

        // All dependents of db.py (should be repo, service, app)
        let dependents = graph.get_transitive_dependents("db.py", 10);
        assert_eq!(dependents.len(), 3);
        assert!(dependents.contains(&"repo.py".to_string()));
        assert!(dependents.contains(&"service.py".to_string()));
        assert!(dependents.contains(&"app.py".to_string()));
    }

    #[test]
    fn test_cycle_detection() {
        let mut graph = DependencyGraph::new();
        // Cycle: a.py -> b.py -> c.py -> a.py
        graph.add_edge(make_edge("a.py", "b.py"));
        graph.add_edge(make_edge("b.py", "c.py"));
        graph.add_edge(make_edge("c.py", "a.py"));

        let cycles = graph.detect_cycles();
        assert!(!cycles.is_empty(), "Should detect a cycle");
    }

    #[test]
    fn test_root_and_leaf_files() {
        let mut graph = DependencyGraph::new();
        // main.py -> service.py -> db.py
        graph.add_edge(make_edge("main.py", "service.py"));
        graph.add_edge(make_edge("service.py", "db.py"));

        let roots = graph.get_root_files();
        assert!(roots.contains(&"main.py"));
        assert!(!roots.contains(&"db.py"));

        let leaves = graph.get_leaf_files();
        assert!(leaves.contains(&"db.py"));
        assert!(!leaves.contains(&"main.py"));
    }
}
