//! Trie for O(k) blocked pattern matching.

use crate::policy::BlockedPattern;
use std::collections::HashMap;

struct TrieNode {
    children: HashMap<char, TrieNode>,
    pattern: Option<BlockedPattern>,
    is_prefix_match: bool,
}

/// Trie for blocked pattern matching
pub struct PatternTrie {
    root: TrieNode,
    count: usize,
}

impl PatternTrie {
    pub fn new() -> Self {
        Self {
            root: TrieNode::new(),
            count: 0,
        }
    }

    /// Build trie from blocked patterns
    pub fn from_patterns(patterns: &[BlockedPattern]) -> Self {
        let mut trie = Self::new();
        for pattern in patterns {
            trie.insert(pattern.clone());
        }
        trie
    }

    /// Insert pattern into trie
    pub fn insert(&mut self, pattern: BlockedPattern) {
        let mut current = &mut self.root;

        for ch in pattern.pattern.chars() {
            current = current.children.entry(ch).or_insert_with(TrieNode::new);
        }

        current.is_prefix_match = pattern.is_prefix_match;
        current.pattern = Some(pattern);
        self.count += 1;
    }

    /// Find matching pattern for import path
    /// Returns the BlockedPattern if matched
    pub fn find_match(&self, import_path: &str) -> Option<&BlockedPattern> {
        let mut current = &self.root;
        let mut last_prefix_match: Option<&BlockedPattern> = None;

        for ch in import_path.chars() {
            // Check if current node is a prefix match
            if current.is_prefix_match && current.pattern.is_some() {
                last_prefix_match = current.pattern.as_ref();
            }

            // Move to next node
            match current.children.get(&ch) {
                Some(node) => current = node,
                None => {
                    // No more children - return prefix match if we have one
                    return last_prefix_match;
                }
            }
        }

        // Check final node
        if current.is_prefix_match || current.pattern.is_some() {
            current.pattern.as_ref()
        } else {
            last_prefix_match
        }
    }

    pub fn len(&self) -> usize {
        self.count
    }

    pub fn is_empty(&self) -> bool {
        self.count == 0
    }
}

impl TrieNode {
    fn new() -> Self {
        Self {
            children: HashMap::new(),
            pattern: None,
            is_prefix_match: false,
        }
    }
}

impl Default for PatternTrie {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Severity;

    fn make_pattern(pattern: &str, is_prefix: bool) -> BlockedPattern {
        BlockedPattern {
            pattern: pattern.to_string(),
            reason: "Test".to_string(),
            severity: Severity::High,
            alternatives: vec![],
            is_prefix_match: is_prefix,
        }
    }

    #[test]
    fn test_exact_match() {
        let trie = PatternTrie::from_patterns(&[make_pattern("os.system", false)]);
        assert!(trie.find_match("os.system").is_some());
        assert!(trie.find_match("os.path").is_none());
    }

    #[test]
    fn test_prefix_match() {
        let trie = PatternTrie::from_patterns(&[make_pattern("pickle", true)]);

        assert!(trie.find_match("pickle.loads").is_some());
        assert!(trie.find_match("pickle.dumps").is_some());
        assert!(trie.find_match("json.loads").is_none());
    }

    #[test]
    fn test_empty_trie() {
        let trie = PatternTrie::new();
        assert!(trie.is_empty());
        assert_eq!(trie.len(), 0);
    }
}
