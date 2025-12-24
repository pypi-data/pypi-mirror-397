//! Typosquatting detection for Python packages.
//!
//! Uses Levenshtein distance to detect packages with names
//! suspiciously similar to popular packages.

/// Popular Python packages that are often typosquatted.
const POPULAR_PACKAGES: &[&str] = &[
    "requests",
    "numpy",
    "pandas",
    "django",
    "flask",
    "fastapi",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "matplotlib",
    "pillow",
    "boto3",
    "selenium",
    "beautifulsoup4",
    "sqlalchemy",
    "celery",
    "redis",
    "pymongo",
    "psycopg2",
    "cryptography",
    "pyyaml",
    "pydantic",
    "httpx",
    "aiohttp",
    "starlette",
    "uvicorn",
];

/// Check if a package name is potentially a typosquat.
pub fn check_typosquat(package: &str, threshold: f64) -> Option<TyposquatMatch> {
    let package_lower = package.to_lowercase();

    if package_lower.starts_with('.') {
        return None;
    }

    for &popular in POPULAR_PACKAGES {
        if popular == package_lower {
            return None;
        }

        let similarity = normalized_levenshtein(&package_lower, popular);

        if similarity >= threshold && similarity < 1.0 {
            return Some(TyposquatMatch {
                suspicious_package: package.to_string(),
                similar_to: popular.to_string(),
                similarity,
            });
        }
    }

    None
}

/// A potential typosquatting match.
#[derive(Debug, Clone)]
pub struct TyposquatMatch {
    pub suspicious_package: String,
    pub similar_to: String,
    pub similarity: f64,
}

impl TyposquatMatch {
    pub fn warning_message(&self) -> String {
        format!(
            "Package '{}' is {:.0}% similar to popular package '{}' - possible typosquat",
            self.suspicious_package,
            self.similarity * 100.0,
            self.similar_to
        )
    }
}

/// Calculate the Levenshtein distance between two strings.
pub fn levenshtein_distance(a: &str, b: &str) -> usize {
    let a_chars: Vec<char> = a.chars().collect();
    let b_chars: Vec<char> = b.chars().collect();

    let a_len = a_chars.len();
    let b_len = b_chars.len();

    if a_len == 0 {
        return b_len;
    }
    if b_len == 0 {
        return a_len;
    }

    // prev_row[j] == edit distance between a[..i] and b[..j]
    let mut prev_row: Vec<usize> = (0..=b_len).collect();
    let mut current_row: Vec<usize> = vec![0; b_len + 1];

    for (i, a_ch) in a_chars.iter().enumerate() {
        // First column: cost of deletions to match empty prefix of b
        if let Some(first) = current_row.first_mut() {
            *first = i + 1;
        } else {
            // Should be unreachable, but fall back safely
            return b_len;
        }

        // prev_diag tracks the value from prev_row[j] (top-left in the DP matrix)
        let mut prev_diag = match prev_row.first().copied() {
            Some(v) => v,
            None => return b_len,
        };

        for (j, b_ch) in b_chars.iter().enumerate() {
            // Value directly above (prev_row[j + 1])
            let above = match prev_row.get(j + 1).copied() {
                Some(v) => v,
                None => return a_len,
            };

            // Value directly left (current_row[j])
            let left = match current_row.get(j).copied() {
                Some(v) => v,
                None => i + 1,
            };

            let cost = if a_ch == b_ch { 0 } else { 1 };
            let insertion = left + 1;
            let deletion = above + 1;
            let substitution = prev_diag + cost;
            let value = insertion.min(deletion).min(substitution);

            if let Some(cell) = current_row.get_mut(j + 1) {
                *cell = value;
            }

            // Move the diagonal for the next iteration
            prev_diag = above;
        }

        std::mem::swap(&mut prev_row, &mut current_row);
    }

    prev_row.last().copied().unwrap_or_default()
}

/// Calculate normalized Levenshtein similarity (0.0 - 1.0).
pub fn normalized_levenshtein(a: &str, b: &str) -> f64 {
    let max_len = a.len().max(b.len());
    if max_len == 0 {
        return 1.0;
    }

    let distance = levenshtein_distance(a, b);
    1.0 - (distance as f64 / max_len as f64)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error;

    #[test]
    fn test_typosquat_detection() -> Result<(), Box<dyn Error>> {
        let result = check_typosquat("requets", 0.8);
        assert!(result.is_some());
        let match_result = result.ok_or_else(|| {
            std::io::Error::new(std::io::ErrorKind::NotFound, "expected typosquat match")
        })?;
        assert_eq!(match_result.similar_to, "requests");

        // Exact match - not a typosquat
        let result = check_typosquat("requests", 0.8);
        assert!(result.is_none());
        Ok(())
    }

    #[test]
    fn test_levenshtein_distance() {
        assert_eq!(levenshtein_distance("kitten", "sitting"), 3);
        assert_eq!(levenshtein_distance("requests", "requets"), 1); // only 1 transposition
        assert_eq!(levenshtein_distance("", "abc"), 3);
        assert_eq!(levenshtein_distance("abc", ""), 3);
    }

    #[test]
    fn test_normalized_levenshtein() {
        let sim = normalized_levenshtein("requests", "requets");
        assert!(sim > 0.7);

        let sim = normalized_levenshtein("abc", "xyz");
        assert!(sim < 0.5);
    }

    #[test]
    fn test_no_typosquat_for_relative_imports() {
        let result = check_typosquat(".models", 0.8);
        assert!(result.is_none());
    }

    #[test]
    fn test_warning_message() {
        let typo_match = TyposquatMatch {
            suspicious_package: "requets".to_string(),
            similar_to: "requests".to_string(),
            similarity: 0.875,
        };

        let message = typo_match.warning_message();
        assert!(message.contains("requets"));
        assert!(message.contains("requests"));
        assert!(message.contains("88%")); // 87.5 rounds to 88
    }
}
