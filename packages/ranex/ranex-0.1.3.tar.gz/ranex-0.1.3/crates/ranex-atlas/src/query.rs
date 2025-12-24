//! Query builder for Atlas searches.
//!
//! Provides a fluent API for constructing artifact queries.

use ranex_core::ArtifactKind;

/// Builder for constructing artifact queries.
#[derive(Debug, Clone, Default)]
pub struct QueryBuilder {
    /// Symbol name filter (partial match)
    pub symbol_name: Option<String>,

    /// Feature filter
    pub feature: Option<String>,

    /// Kind filter
    pub kind: Option<ArtifactKind>,

    /// File path filter (partial match)
    pub file_path: Option<String>,

    /// Tag filter (must have all specified tags)
    pub tags: Vec<String>,

    /// Maximum results
    pub limit: usize,

    /// Offset for pagination
    pub offset: usize,
}

impl QueryBuilder {
    /// Create a new query builder with default settings.
    pub fn new() -> Self {
        Self {
            limit: 100,
            ..Default::default()
        }
    }

    /// Filter by symbol name (partial match).
    pub fn symbol(mut self, name: impl Into<String>) -> Self {
        self.symbol_name = Some(name.into());
        self
    }

    /// Filter by feature name.
    pub fn feature(mut self, feature: impl Into<String>) -> Self {
        self.feature = Some(feature.into());
        self
    }

    /// Filter by artifact kind.
    pub fn kind(mut self, kind: ArtifactKind) -> Self {
        self.kind = Some(kind);
        self
    }

    /// Filter by file path (partial match).
    pub fn file_path(mut self, path: impl Into<String>) -> Self {
        self.file_path = Some(path.into());
        self
    }

    /// Filter by tag (artifact must have this tag).
    pub fn with_tag(mut self, tag: impl Into<String>) -> Self {
        self.tags.push(tag.into());
        self
    }

    /// Set maximum number of results.
    pub fn limit(mut self, limit: usize) -> Self {
        self.limit = limit;
        self
    }

    /// Set offset for pagination.
    pub fn offset(mut self, offset: usize) -> Self {
        self.offset = offset;
        self
    }

    /// Build the SQL WHERE clause.
    pub fn build_where_clause(&self) -> (String, Vec<String>) {
        let mut conditions = Vec::new();
        let mut params = Vec::new();

        if let Some(ref name) = self.symbol_name {
            conditions.push("symbol_name LIKE ?".to_string());
            params.push(format!("%{}%", name));
        }

        if let Some(ref feature) = self.feature {
            conditions.push("feature = ?".to_string());
            params.push(feature.clone());
        }

        if let Some(ref kind) = self.kind {
            conditions.push("kind = ?".to_string());
            params.push(kind.as_str().to_string());
        }

        if let Some(ref path) = self.file_path {
            conditions.push("file_path LIKE ?".to_string());
            params.push(format!("%{}%", path));
        }

        // Tags are stored as JSON array, need special handling
        for tag in &self.tags {
            conditions.push("tags LIKE ?".to_string());
            params.push(format!("%\"{}\",%", tag));
        }

        let where_clause = if conditions.is_empty() {
            String::new()
        } else {
            format!("WHERE {}", conditions.join(" AND "))
        };

        (where_clause, params)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_query_builder() {
        let query = QueryBuilder::new()
            .symbol("payment")
            .kind(ArtifactKind::Function)
            .limit(10);

        let (clause, params) = query.build_where_clause();

        assert!(clause.contains("symbol_name LIKE"));
        assert!(clause.contains("kind ="));
        assert_eq!(params.len(), 2);
    }

    #[test]
    fn test_empty_query() {
        let query = QueryBuilder::new();
        let (clause, params) = query.build_where_clause();

        assert!(clause.is_empty());
        assert!(params.is_empty());
    }
}
