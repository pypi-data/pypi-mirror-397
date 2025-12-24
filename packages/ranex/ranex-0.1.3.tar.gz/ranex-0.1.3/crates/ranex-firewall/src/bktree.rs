//! BK-tree for efficient typosquatting detection.
//!
//! Provides O(log n) average-case edit distance queries,
//! compared to O(n²) brute-force Levenshtein.

use std::collections::HashMap;

/// BK-tree node
struct BKNode {
    word: String,
    children: HashMap<usize, Box<BKNode>>,
}

/// BK-tree for typosquatting detection
pub struct BKTree {
    root: Option<Box<BKNode>>,
    size: usize,
    // Map from typo string to intended correct package
    typo_to_intended: HashMap<String, String>,
}

impl BKTree {
    /// Create empty BK-tree
    pub fn new() -> Self {
        Self {
            root: None,
            size: 0,
            typo_to_intended: HashMap::new(),
        }
    }

    /// Build BK-tree from allowed packages (O(n log n))
    pub fn from_packages(packages: &[String]) -> Self {
        let mut tree = Self::new();
        for pkg in packages {
            tree.insert(pkg);
        }
        tree
    }

    /// Build BK-tree from known typos (O(n log n))
    pub fn from_known_typos(known_typos: &[crate::policy::KnownTypo]) -> Self {
        let mut tree = Self::new();
        for typo in known_typos {
            for typo_str in &typo.typos {
                tree.insert_with_intended(typo_str, &typo.actual);
            }
        }
        tree
    }

    /// Insert word into tree
    pub fn insert(&mut self, word: &str) {
        if word.is_empty() {
            return;
        }

        if self.root.is_none() {
            self.root = Some(Box::new(BKNode {
                word: word.to_string(),
                children: HashMap::new(),
            }));
            self.size += 1;
            return;
        }

        // Use a separate method that returns whether insertion happened
        if let Some(root) = self.root.as_mut()
            && Self::insert_into_node(root, word)
        {
            self.size += 1;
        }
    }

    /// Insert typo with intended correct package
    pub fn insert_with_intended(&mut self, typo: &str, intended: &str) {
        if typo.is_empty() {
            return;
        }

        // Store mapping from typo to intended package
        self.typo_to_intended
            .insert(typo.to_string(), intended.to_string());

        // Insert typo into BK-tree for similarity matching
        self.insert(typo);
    }

    /// Returns true if a new node was inserted, false if duplicate
    fn insert_into_node(node: &mut BKNode, word: &str) -> bool {
        let distance = Self::levenshtein(&node.word, word);

        if distance == 0 {
            // Duplicate - don't insert
            return false;
        }

        // Use entry API to avoid contains_key + insert pattern
        node.children.entry(distance).or_insert_with(|| {
            Box::new(BKNode {
                word: word.to_string(),
                children: HashMap::new(),
            })
        });
        true
    }

    /// Find packages within edit distance threshold
    /// Returns: Option<(intended_package, edit_distance)>
    pub fn find_similar(&self, query: &str, max_distance: usize) -> Option<(String, usize)> {
        let root = self.root.as_ref()?;

        let mut best_match: Option<(String, usize)> = None;
        let mut stack = vec![root.as_ref()];

        while let Some(node) = stack.pop() {
            let distance = Self::levenshtein(&node.word, query);

            // Update best match
            if distance <= max_distance {
                match best_match {
                    None => best_match = Some((node.word.clone(), distance)),
                    Some((_, best_dist)) if distance < best_dist => {
                        best_match = Some((node.word.clone(), distance));
                    }
                    _ => {}
                }
            }

            // Early exit if exact match
            if distance == 0 {
                // Return intended package for exact typo match
                if let Some(intended) = self.typo_to_intended.get(&node.word) {
                    return Some((intended.clone(), 0));
                }
                return Some((node.word.clone(), 0));
            }

            // Search children within distance range
            let min_child_dist = distance.saturating_sub(max_distance);
            let max_child_dist = distance + max_distance;

            for child_dist in min_child_dist..=max_child_dist {
                if let Some(child) = node.children.get(&child_dist) {
                    stack.push(child.as_ref());
                }
            }
        }

        // Map matched typo to intended package
        best_match.map(|(typo, dist)| {
            if let Some(intended) = self.typo_to_intended.get(&typo) {
                (intended.clone(), dist)
            } else {
                (typo, dist)
            }
        })
    }

    /// Number of words in tree
    pub fn len(&self) -> usize {
        self.size
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    /// Levenshtein distance - space-optimized two-row algorithm
    #[inline]
    pub(crate) fn levenshtein(a: &str, b: &str) -> usize {
        crate::typosquat::levenshtein_distance(a, b)
    }
}

impl Default for BKTree {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_levenshtein_identical() {
        assert_eq!(BKTree::levenshtein("requests", "requests"), 0);
    }

    #[test]
    fn test_levenshtein_one_char() {
        assert_eq!(BKTree::levenshtein("requests", "reqeusts"), 2);
    }

    #[test]
    fn test_levenshtein_empty() {
        assert_eq!(BKTree::levenshtein("", "abc"), 3);
        assert_eq!(BKTree::levenshtein("abc", ""), 3);
    }

    #[test]
    fn test_find_similar_exact() {
        let tree = BKTree::from_packages(&["requests".into(), "flask".into()]);
        let result = tree.find_similar("requests", 2);
        assert_eq!(result, Some(("requests".into(), 0)));
    }

    #[test]
    fn test_find_similar_typo() {
        let tree = BKTree::from_packages(&["requests".into(), "flask".into()]);
        let result = tree.find_similar("reqeusts", 2);
        assert!(result.is_some());
        let Some((word, dist)) = result else {
            return;
        };
        assert_eq!(word, "requests");
        assert!(dist <= 2);
    }

    #[test]
    fn test_find_similar_no_match() {
        let tree = BKTree::from_packages(&["requests".into(), "flask".into()]);
        let result = tree.find_similar("completely_different", 2);
        assert!(result.is_none());
    }

    #[test]
    fn test_insert_empty_string() {
        let mut tree = BKTree::new();
        tree.insert("");
        assert_eq!(tree.len(), 0);
    }

    #[test]
    fn test_insert_duplicates() {
        let mut tree = BKTree::new();
        tree.insert("requests");
        tree.insert("requests");
        assert_eq!(tree.len(), 1);
    }
}
