//! Duplicate code detection.
//!
//! Identifies similar code blocks across the codebase for DRY enforcement.
//! Uses multiple techniques:
//!
//! - **Token sequence hashing**: Fast initial filtering
//! - **AST structure comparison**: Semantic similarity
//! - **Signature matching**: Functions with similar signatures
//!
//! ## Example
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::{DuplicateDetector, SimilarityScore};
//!
//! let detector = DuplicateDetector::new(&artifacts)
//!     .with_threshold(SimilarityScore::new(0.8));
//!
//! let matches = detector.find_duplicates()?;
//! for m in matches {
//!     println!("Similar: {} <-> {} ({:.0}%)",
//!         m.artifact_a, m.artifact_b, m.similarity.as_percentage()
//!     );
//! }
//! ```

use ranex_core::Artifact;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Similarity score between two code blocks (0.0 to 1.0).
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct SimilarityScore(f64);

impl SimilarityScore {
    /// Create a new similarity score (clamped to 0.0-1.0).
    pub fn new(value: f64) -> Self {
        Self(value.clamp(0.0, 1.0))
    }

    /// Get the raw value.
    pub fn value(&self) -> f64 {
        self.0
    }

    /// Get as percentage.
    pub fn as_percentage(&self) -> f64 {
        self.0 * 100.0
    }

    /// Check if this exceeds a threshold.
    pub fn exceeds(&self, threshold: SimilarityScore) -> bool {
        self.0 >= threshold.0
    }
}

impl Default for SimilarityScore {
    fn default() -> Self {
        Self(0.0)
    }
}

/// A match between two similar code blocks.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DuplicateMatch {
    /// First artifact's qualified name.
    pub artifact_a: String,

    /// Second artifact's qualified name.
    pub artifact_b: String,

    /// File path of first artifact.
    pub file_a: String,

    /// File path of second artifact.
    pub file_b: String,

    /// Line range in first file.
    pub lines_a: (usize, usize),

    /// Line range in second file.
    pub lines_b: (usize, usize),

    /// Similarity score.
    pub similarity: SimilarityScore,

    /// Type of similarity detected.
    pub match_type: MatchType,

    /// Suggestion for refactoring.
    pub suggestion: Option<String>,
}

/// Type of duplicate/similarity match.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MatchType {
    /// Exact or near-exact code duplication.
    ExactDuplicate,
    /// Similar function signatures.
    SimilarSignature,
    /// Similar structure (AST pattern).
    SimilarStructure,
    /// Similar naming pattern.
    SimilarNaming,
}

impl MatchType {
    pub fn as_str(&self) -> &'static str {
        match self {
            MatchType::ExactDuplicate => "exact_duplicate",
            MatchType::SimilarSignature => "similar_signature",
            MatchType::SimilarStructure => "similar_structure",
            MatchType::SimilarNaming => "similar_naming",
        }
    }
}

impl std::fmt::Display for MatchType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Configuration for duplicate detection limits.
#[derive(Debug, Clone)]
pub struct DuplicateDetectorConfig {
    /// Maximum group size to process (to avoid O(n²) explosion).
    /// Groups larger than this will be sampled.
    pub max_group_size: usize,
    /// Maximum total comparisons to perform.
    pub max_comparisons: usize,
    /// Whether to log warnings when limits are hit.
    pub warn_on_limits: bool,
}

impl Default for DuplicateDetectorConfig {
    fn default() -> Self {
        Self {
            max_group_size: 100,     // Process groups up to 100 (was 10)
            max_comparisons: 10_000, // Cap total comparisons
            warn_on_limits: true,
        }
    }
}

/// Duplicate code detector.
pub struct DuplicateDetector<'a> {
    artifacts: &'a [Artifact],
    threshold: SimilarityScore,
    min_lines: usize,
    config: DuplicateDetectorConfig,
}

impl<'a> DuplicateDetector<'a> {
    /// Create a new duplicate detector.
    pub fn new(artifacts: &'a [Artifact]) -> Self {
        Self {
            artifacts,
            threshold: SimilarityScore::new(0.8),
            min_lines: 3,
            config: DuplicateDetectorConfig::default(),
        }
    }

    /// Set similarity threshold.
    pub fn with_threshold(mut self, threshold: SimilarityScore) -> Self {
        self.threshold = threshold;
        self
    }

    /// Set minimum lines for consideration.
    pub fn with_min_lines(mut self, lines: usize) -> Self {
        self.min_lines = lines;
        self
    }

    /// Set configuration for limits.
    pub fn with_config(mut self, config: DuplicateDetectorConfig) -> Self {
        self.config = config;
        self
    }

    /// Find all duplicates above threshold.
    ///
    /// Only detects actual duplicates based on:
    /// - Identical function signatures (same parameter types and return type)
    ///
    /// Note: Naming pattern matching (get_x, create_x) was removed because
    /// following naming conventions is NOT duplication - it's good practice.
    pub fn find_duplicates(&self) -> Vec<DuplicateMatch> {
        let mut matches = Vec::new();

        // Find signature-based duplicates only
        // Naming patterns like get_x, create_x are NOT duplicates
        matches.extend(self.find_signature_duplicates());

        // Sort by similarity (highest first), treating NaN as equal
        matches.sort_by(|a, b| {
            b.similarity
                .partial_cmp(&a.similarity)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        matches
    }

    /// Find functions with similar signatures.
    fn find_signature_duplicates(&self) -> Vec<DuplicateMatch> {
        let mut matches = Vec::new();
        let mut total_comparisons: usize = 0;
        let mut groups_sampled: usize = 0;
        let mut groups_processed: usize = 0;

        // Group artifacts by signature pattern
        let mut signature_groups: HashMap<String, Vec<&Artifact>> = HashMap::new();

        for artifact in self.artifacts {
            if let Some(sig) = &artifact.signature {
                // Skip trivial signatures that would cause false positives
                if self.is_trivial_signature(sig) {
                    continue;
                }

                // Normalize signature for comparison
                let normalized = self.normalize_signature(sig);

                // Skip if normalized signature is too short (likely trivial)
                if normalized.len() < 10 {
                    continue;
                }

                signature_groups
                    .entry(normalized)
                    .or_default()
                    .push(artifact);
            }
        }

        // Find groups with multiple artifacts
        for (sig, group) in &signature_groups {
            if group.len() < 2 {
                continue;
            }

            groups_processed += 1;

            // Determine which artifacts to compare
            let artifacts_to_compare: Vec<&&Artifact> = if group.len() > self.config.max_group_size
            {
                // Sample the group to avoid O(n²) explosion
                groups_sampled += 1;
                if self.config.warn_on_limits {
                    tracing::warn!(
                        signature = %sig,
                        group_size = group.len(),
                        max_size = self.config.max_group_size,
                        "Large signature group detected, sampling subset for comparison"
                    );
                }
                // Take evenly distributed samples
                let step = group.len() / self.config.max_group_size;
                group
                    .iter()
                    .step_by(step.max(1))
                    .take(self.config.max_group_size)
                    .collect()
            } else {
                group.iter().collect()
            };

            // Compare pairs
            for i in 0..artifacts_to_compare.len() {
                for j in (i + 1)..artifacts_to_compare.len() {
                    // Check if we've hit the comparison limit
                    if total_comparisons >= self.config.max_comparisons {
                        if self.config.warn_on_limits {
                            tracing::warn!(
                                max_comparisons = self.config.max_comparisons,
                                "Hit maximum comparison limit, stopping early"
                            );
                        }
                        return matches;
                    }

                    total_comparisons += 1;
                    let (Some(&a), Some(&b)) = (
                        artifacts_to_compare.get(i),
                        artifacts_to_compare.get(j),
                    ) else {
                        continue;
                    };

                    // Skip if same file and close lines (likely same class)
                    if a.file_path == b.file_path
                        && (a.line_start as i64 - b.line_start as i64).abs() < 20
                    {
                        continue;
                    }

                    let similarity = self.calculate_signature_similarity(a, b);
                    if similarity.exceeds(self.threshold) {
                        matches.push(DuplicateMatch {
                            artifact_a: a.qualified_name.clone(),
                            artifact_b: b.qualified_name.clone(),
                            file_a: a.file_path.to_string_lossy().to_string(),
                            file_b: b.file_path.to_string_lossy().to_string(),
                            lines_a: (a.line_start, a.line_end),
                            lines_b: (b.line_start, b.line_end),
                            similarity,
                            match_type: MatchType::SimilarSignature,
                            suggestion: Some(format!(
                                "Consider creating a generic function to replace '{}' and '{}'",
                                a.symbol_name, b.symbol_name
                            )),
                        });
                    }
                }
            }
        }

        tracing::debug!(
            groups_processed = groups_processed,
            groups_sampled = groups_sampled,
            total_comparisons = total_comparisons,
            matches_found = matches.len(),
            "Duplicate detection completed"
        );

        matches
    }

    /// Check if a signature is too trivial for duplicate detection.
    /// Trivial signatures like () or (self) produce too many false positives.
    fn is_trivial_signature(&self, sig: &str) -> bool {
        let trimmed = sig.trim();

        // Empty or very short signatures
        if trimmed.len() < 5 {
            return true;
        }

        // Just parentheses with nothing meaningful
        let params_only = trimmed.split("->").next().unwrap_or("").trim();

        // Common trivial patterns
        let trivial_patterns = [
            "()",
            "(self)",
            "(cls)",
            "() -> None",
            "(self) -> None",
            "(self) -> Self",
            "(*args, **kwargs)",
            "(self, *args, **kwargs)",
        ];

        for pattern in &trivial_patterns {
            if params_only == *pattern || trimmed == *pattern {
                return true;
            }
        }

        // Count actual typed parameters (excluding self)
        let param_count = params_only.matches(':').count();

        // If there's only one typed parameter (often just a generic return type scenario)
        // it's not meaningful for duplicate detection
        if param_count < 2 {
            return true;
        }

        false
    }

    /// Normalize a signature for comparison.
    fn normalize_signature(&self, sig: &str) -> String {
        // Remove parameter names, keep only types
        // (amount: float, rate: float) -> float
        // becomes: (float, float) -> float

        let mut normalized = String::new();
        let mut in_type = false;

        for c in sig.chars() {
            match c {
                ':' => {
                    in_type = true;
                }
                ',' | ')' => {
                    in_type = false;
                    normalized.push(c);
                }
                _ if in_type => {
                    normalized.push(c);
                }
                '(' | '-' | '>' | ' ' => {
                    normalized.push(c);
                }
                _ => {}
            }
        }

        // Further normalize by removing whitespace
        normalized.replace(' ', "")
    }

    /// Calculate signature-based similarity between two artifacts.
    fn calculate_signature_similarity(&self, a: &Artifact, b: &Artifact) -> SimilarityScore {
        match (&a.signature, &b.signature) {
            (Some(sig_a), Some(sig_b)) => {
                let norm_a = self.normalize_signature(sig_a);
                let norm_b = self.normalize_signature(sig_b);

                if norm_a == norm_b {
                    // Exact signature match
                    SimilarityScore::new(0.95)
                } else {
                    // Calculate Levenshtein-based similarity
                    let distance = self.levenshtein_distance(&norm_a, &norm_b);
                    let max_len = norm_a.len().max(norm_b.len());
                    if max_len == 0 {
                        SimilarityScore::new(1.0)
                    } else {
                        SimilarityScore::new(1.0 - (distance as f64 / max_len as f64))
                    }
                }
            }
            _ => SimilarityScore::new(0.0),
        }
    }

    /// Calculate Levenshtein distance between two strings.
    fn levenshtein_distance(&self, a: &str, b: &str) -> usize {
        let a_chars: Vec<char> = a.chars().collect();
        let b_chars: Vec<char> = b.chars().collect();
        let m = a_chars.len();
        let n = b_chars.len();

        if m == 0 {
            return n;
        }
        if n == 0 {
            return m;
        }

        let mut matrix = vec![vec![0; n + 1]; m + 1];

        for (i, row) in matrix.iter_mut().enumerate().take(m + 1) {
            if let Some(first) = row.first_mut() {
                *first = i;
            }
        }
        if let Some(first_row) = matrix.first_mut() {
            for (j, cell) in first_row.iter_mut().enumerate().take(n + 1) {
                *cell = j;
            }
        }

        for i in 1..=m {
            for j in 1..=n {
                let a_ch = a_chars.get(i.wrapping_sub(1)).copied();
                let b_ch = b_chars.get(j.wrapping_sub(1)).copied();
                let cost = if let (Some(a_ch), Some(b_ch)) = (a_ch, b_ch) {
                    if a_ch == b_ch { 0 } else { 1 }
                } else {
                    1
                };

                let above = matrix
                    .get(i.wrapping_sub(1))
                    .and_then(|row| row.get(j))
                    .copied();
                let left = matrix
                    .get(i)
                    .and_then(|row| row.get(j.wrapping_sub(1)))
                    .copied();
                let diag = matrix
                    .get(i.wrapping_sub(1))
                    .and_then(|row| row.get(j.wrapping_sub(1)))
                    .copied();

                if let (Some(above), Some(left), Some(diag)) = (above, left, diag)
                    && let Some(row) = matrix.get_mut(i)
                    && let Some(cell) = row.get_mut(j)
                {
                    *cell = (above + 1).min(left + 1).min(diag + cost);
                }
            }
        }

        matrix
            .get(m)
            .and_then(|row| row.get(n))
            .copied()
            .unwrap_or(0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ranex_core::ArtifactKind;
    use std::path::PathBuf;

    fn make_artifact(name: &str, qualified: &str, sig: Option<&str>) -> Artifact {
        Artifact {
            symbol_name: name.to_string(),
            qualified_name: qualified.to_string(),
            kind: ArtifactKind::Function,
            file_path: PathBuf::from(format!("{}.py", name)),
            module_path: "test".to_string(),
            signature: sig.map(String::from),
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

    #[test]
    fn test_signature_similarity() {
        // Use non-trivial signatures with multiple typed parameters
        let artifacts = vec![
            make_artifact(
                "calculate_order_total",
                "orders.calculate_order_total",
                Some("(items: list, tax_rate: float, discount: float) -> float"),
            ),
            make_artifact(
                "calculate_invoice_total",
                "invoices.calculate_invoice_total",
                Some("(items: list, tax_rate: float, discount: float) -> float"),
            ),
        ];

        let detector = DuplicateDetector::new(&artifacts).with_threshold(SimilarityScore::new(0.7));
        let matches = detector.find_signature_duplicates();

        // Should find similar signatures
        assert!(!matches.is_empty(), "Expected to find similar signatures");
    }

    #[test]
    fn test_similarity_score() {
        let score = SimilarityScore::new(0.85);
        assert_eq!(score.as_percentage(), 85.0);
        assert!(score.exceeds(SimilarityScore::new(0.8)));
        assert!(!score.exceeds(SimilarityScore::new(0.9)));
    }

    #[test]
    fn test_levenshtein_distance() {
        let detector = DuplicateDetector::new(&[]);

        assert_eq!(detector.levenshtein_distance("", ""), 0);
        assert_eq!(detector.levenshtein_distance("abc", "abc"), 0);
        assert_eq!(detector.levenshtein_distance("abc", "abd"), 1);
        assert_eq!(detector.levenshtein_distance("abc", ""), 3);
    }
}
