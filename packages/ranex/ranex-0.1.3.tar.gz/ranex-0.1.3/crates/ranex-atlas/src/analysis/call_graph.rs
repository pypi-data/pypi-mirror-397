//! Call graph extraction and analysis.
//!
//! Tracks function-to-function call relationships within a codebase.
//! This is foundational for impact analysis and pattern detection.
//!
//! ## Design Decisions
//!
//! - **Edge granularity**: Each call site is recorded separately (caller, callee, line)
//! - **Call types**: Distinguishes direct, async, callback, and method calls
//! - **Storage**: Persisted to SQLite `calls` table for incremental updates
//!
//! ## Example
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::{CallGraph, CallType};
//!
//! let mut graph = CallGraph::new();
//! graph.add_edge(
//!     "app.services.orders.OrderService.get_order",
//!     "app.repository.orders.OrderRepository.find_by_id",
//!     CallType::Direct,
//!     45,
//! );
//!
//! // Get all callees of a function
//! let callees = graph.get_callees("app.services.orders.OrderService.get_order");
//! ```

use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

/// Type of function call.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CallType {
    /// Direct synchronous call: `foo()`
    Direct,
    /// Async call: `await foo()`
    Async,
    /// Callback/closure: `map(lambda x: foo(x))`
    Callback,
    /// Method call on self: `self.method()`
    Method,
    /// Super call: `super().method()`
    Super,
    /// Static/class method call: `ClassName.method()`
    Static,
}

impl CallType {
    /// Convert to string for database storage.
    pub fn as_str(&self) -> &'static str {
        match self {
            CallType::Direct => "direct",
            CallType::Async => "async",
            CallType::Callback => "callback",
            CallType::Method => "method",
            CallType::Super => "super",
            CallType::Static => "static",
        }
    }

    /// Parse from string.
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "direct" => Some(CallType::Direct),
            "async" => Some(CallType::Async),
            "callback" => Some(CallType::Callback),
            "method" => Some(CallType::Method),
            "super" => Some(CallType::Super),
            "static" => Some(CallType::Static),
            _ => None,
        }
    }
}

impl std::fmt::Display for CallType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// An edge in the call graph representing a function call.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct CallEdge {
    /// Qualified name of the calling function.
    pub caller: String,

    /// Qualified name of the called function.
    pub callee: String,

    /// Type of call.
    pub call_type: CallType,

    /// Line number of the call site (1-indexed).
    pub line_number: usize,

    /// File path where the call occurs.
    pub file_path: String,
}

impl CallEdge {
    /// Create a new call edge.
    pub fn new(
        caller: impl Into<String>,
        callee: impl Into<String>,
        call_type: CallType,
        line_number: usize,
        file_path: impl Into<String>,
    ) -> Self {
        Self {
            caller: caller.into(),
            callee: callee.into(),
            call_type,
            line_number,
            file_path: file_path.into(),
        }
    }
}

/// In-memory call graph for analysis.
///
/// Maintains bidirectional indexes for efficient traversal:
/// - `callers`: callee -> set of callers (who calls this function?)
/// - `callees`: caller -> set of callees (what does this function call?)
#[derive(Debug, Clone, Default)]
pub struct CallGraph {
    /// All edges in the graph.
    edges: Vec<CallEdge>,

    /// Index: callee -> callers (reverse lookup).
    callers: HashMap<String, HashSet<String>>,

    /// Index: caller -> callees (forward lookup).
    callees: HashMap<String, HashSet<String>>,

    /// Index: qualified_name -> edges originating from it.
    edges_by_caller: HashMap<String, Vec<usize>>,

    /// Index: qualified_name -> edges pointing to it.
    edges_by_callee: HashMap<String, Vec<usize>>,
}

impl CallGraph {
    /// Create a new empty call graph.
    pub fn new() -> Self {
        Self::default()
    }

    /// Add an edge to the call graph.
    pub fn add_edge(&mut self, edge: CallEdge) {
        let caller = edge.caller.clone();
        let callee = edge.callee.clone();
        let edge_idx = self.edges.len();

        // Update forward index
        self.callees
            .entry(caller.clone())
            .or_default()
            .insert(callee.clone());

        // Update reverse index
        self.callers
            .entry(callee.clone())
            .or_default()
            .insert(caller.clone());

        // Update edge indexes
        self.edges_by_caller
            .entry(caller)
            .or_default()
            .push(edge_idx);
        self.edges_by_callee
            .entry(callee)
            .or_default()
            .push(edge_idx);

        self.edges.push(edge);
    }

    /// Add an edge with individual parameters.
    pub fn add_call(
        &mut self,
        caller: impl Into<String>,
        callee: impl Into<String>,
        call_type: CallType,
        line_number: usize,
        file_path: impl Into<String>,
    ) {
        self.add_edge(CallEdge::new(
            caller,
            callee,
            call_type,
            line_number,
            file_path,
        ));
    }

    /// Get all functions that call the given function.
    pub fn get_callers(&self, qualified_name: &str) -> Vec<&str> {
        self.callers
            .get(qualified_name)
            .map(|set| set.iter().map(String::as_str).collect())
            .unwrap_or_default()
    }

    /// Get all functions called by the given function.
    pub fn get_callees(&self, qualified_name: &str) -> Vec<&str> {
        self.callees
            .get(qualified_name)
            .map(|set| set.iter().map(String::as_str).collect())
            .unwrap_or_default()
    }

    /// Get all edges where the given function is the caller.
    pub fn get_outgoing_edges(&self, qualified_name: &str) -> Vec<&CallEdge> {
        self.edges_by_caller
            .get(qualified_name)
            .map(|indices| {
                indices
                    .iter()
                    .filter_map(|&i| self.edges.get(i))
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Get all edges where the given function is the callee.
    pub fn get_incoming_edges(&self, qualified_name: &str) -> Vec<&CallEdge> {
        self.edges_by_callee
            .get(qualified_name)
            .map(|indices| {
                indices
                    .iter()
                    .filter_map(|&i| self.edges.get(i))
                    .collect()
            })
            .unwrap_or_default()
    }

    /// Get transitive callers (all functions that eventually call this one).
    ///
    /// Uses BFS to avoid stack overflow on deep call chains.
    pub fn get_transitive_callers(&self, qualified_name: &str, max_depth: usize) -> Vec<String> {
        let mut visited = HashSet::new();
        let mut queue = std::collections::VecDeque::new();
        let mut result = Vec::new();

        queue.push_back((qualified_name.to_string(), 0));
        visited.insert(qualified_name.to_string());

        while let Some((current, depth)) = queue.pop_front() {
            if depth >= max_depth {
                continue;
            }

            if let Some(callers) = self.callers.get(&current) {
                for caller in callers {
                    if visited.insert(caller.clone()) {
                        result.push(caller.clone());
                        queue.push_back((caller.clone(), depth + 1));
                    }
                }
            }
        }

        result
    }

    /// Get transitive callees (all functions eventually called by this one).
    ///
    /// Uses BFS to avoid stack overflow on deep call chains.
    pub fn get_transitive_callees(&self, qualified_name: &str, max_depth: usize) -> Vec<String> {
        let mut visited = HashSet::new();
        let mut queue = std::collections::VecDeque::new();
        let mut result = Vec::new();

        queue.push_back((qualified_name.to_string(), 0));
        visited.insert(qualified_name.to_string());

        while let Some((current, depth)) = queue.pop_front() {
            if depth >= max_depth {
                continue;
            }

            if let Some(callees) = self.callees.get(&current) {
                for callee in callees {
                    if visited.insert(callee.clone()) {
                        result.push(callee.clone());
                        queue.push_back((callee.clone(), depth + 1));
                    }
                }
            }
        }

        result
    }

    /// Get the total number of edges.
    pub fn edge_count(&self) -> usize {
        self.edges.len()
    }

    /// Get the total number of unique functions (nodes).
    pub fn node_count(&self) -> usize {
        let mut nodes: HashSet<&str> = HashSet::new();
        for edge in &self.edges {
            nodes.insert(&edge.caller);
            nodes.insert(&edge.callee);
        }
        nodes.len()
    }

    /// Get all edges in the graph.
    pub fn edges(&self) -> &[CallEdge] {
        &self.edges
    }

    /// Check if the graph contains a specific function.
    pub fn contains(&self, qualified_name: &str) -> bool {
        self.callers.contains_key(qualified_name) || self.callees.contains_key(qualified_name)
    }

    /// Clear the graph.
    pub fn clear(&mut self) {
        self.edges.clear();
        self.callers.clear();
        self.callees.clear();
        self.edges_by_caller.clear();
        self.edges_by_callee.clear();
    }

    /// Build from a list of edges.
    pub fn from_edges(edges: impl IntoIterator<Item = CallEdge>) -> Self {
        let mut graph = Self::new();
        for edge in edges {
            graph.add_edge(edge);
        }
        graph
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_edge() {
        let mut graph = CallGraph::new();
        graph.add_call(
            "app.service.get_order",
            "app.repo.find_by_id",
            CallType::Direct,
            45,
            "app/service.py",
        );

        assert_eq!(graph.edge_count(), 1);
        assert_eq!(graph.node_count(), 2);
    }

    #[test]
    fn test_get_callers_and_callees() {
        let mut graph = CallGraph::new();

        // A calls B, A calls C, D calls B
        graph.add_call("A", "B", CallType::Direct, 10, "a.py");
        graph.add_call("A", "C", CallType::Direct, 20, "a.py");
        graph.add_call("D", "B", CallType::Direct, 30, "d.py");

        let callees_of_a = graph.get_callees("A");
        assert_eq!(callees_of_a.len(), 2);
        assert!(callees_of_a.contains(&"B"));
        assert!(callees_of_a.contains(&"C"));

        let callers_of_b = graph.get_callers("B");
        assert_eq!(callers_of_b.len(), 2);
        assert!(callers_of_b.contains(&"A"));
        assert!(callers_of_b.contains(&"D"));
    }

    #[test]
    fn test_transitive_callers() {
        let mut graph = CallGraph::new();

        // Chain: A -> B -> C -> D
        graph.add_call("A", "B", CallType::Direct, 1, "a.py");
        graph.add_call("B", "C", CallType::Direct, 1, "b.py");
        graph.add_call("C", "D", CallType::Direct, 1, "c.py");

        // All callers of D (should be C, B, A)
        let callers = graph.get_transitive_callers("D", 10);
        assert_eq!(callers.len(), 3);
        assert!(callers.contains(&"A".to_string()));
        assert!(callers.contains(&"B".to_string()));
        assert!(callers.contains(&"C".to_string()));
    }

    #[test]
    fn test_transitive_callers_with_depth_limit() {
        let mut graph = CallGraph::new();

        // Chain: A -> B -> C -> D
        graph.add_call("A", "B", CallType::Direct, 1, "a.py");
        graph.add_call("B", "C", CallType::Direct, 1, "b.py");
        graph.add_call("C", "D", CallType::Direct, 1, "c.py");

        // Only get callers within depth 1 from D (should be just C)
        let callers = graph.get_transitive_callers("D", 1);
        assert_eq!(callers.len(), 1);
        assert!(callers.contains(&"C".to_string()));
    }

    #[test]
    fn test_call_type_roundtrip() {
        for call_type in [
            CallType::Direct,
            CallType::Async,
            CallType::Callback,
            CallType::Method,
            CallType::Super,
            CallType::Static,
        ] {
            let s = call_type.as_str();
            let parsed = CallType::parse(s);
            assert_eq!(parsed, Some(call_type));
        }
    }

    #[test]
    fn test_cycle_handling() {
        let mut graph = CallGraph::new();

        // Cycle: A -> B -> C -> A
        graph.add_call("A", "B", CallType::Direct, 1, "a.py");
        graph.add_call("B", "C", CallType::Direct, 1, "b.py");
        graph.add_call("C", "A", CallType::Direct, 1, "c.py");

        // Should not infinite loop
        let callers = graph.get_transitive_callers("A", 10);
        assert_eq!(callers.len(), 2); // B and C (not A itself)
    }
}
