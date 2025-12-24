//! Atlas integration for internal import validation.
//!
//! This module provides integration with the ranex-atlas crate
//! to validate internal imports against the actual codebase index.

use std::collections::HashMap;
use std::path::PathBuf;
use std::time::{Duration, Instant};

use parking_lot::RwLock;
use ranex_atlas::Atlas;
use ranex_core::AtlasError;

use crate::circuit::CircuitBreaker;
use crate::policy::AtlasConfig;
use ranex_core::{FirewallError, FirewallResult};

/// Cache entry with TTL
#[derive(Clone)]
struct CacheEntry {
    exists: bool,
    suggestions: Vec<String>,
    cached_at: Instant,
}

/// Atlas client for internal import validation
pub struct AtlasClient {
    /// Atlas instance (lazy loaded)
    atlas: Option<Atlas>,

    /// Path to Atlas database
    db_path: PathBuf,

    /// Query cache with TTL
    cache: RwLock<HashMap<String, CacheEntry>>,

    /// Cache TTL duration
    cache_ttl: Duration,

    /// Circuit breaker for Atlas failures
    circuit_breaker: CircuitBreaker,

    /// Whether to fail open (allow) on Atlas errors / open circuit.
    fail_open: bool,
}

impl AtlasClient {
    /// Create new Atlas client
    ///
    /// Note: Atlas is lazily initialized on first query to avoid
    /// startup overhead if internal imports aren't used.
    pub fn new(db_path: &str) -> FirewallResult<Self> {
        Ok(Self {
            atlas: None,
            db_path: PathBuf::from(db_path),
            cache: RwLock::new(HashMap::new()),
            cache_ttl: Duration::from_secs(300), // 5 minutes default
            circuit_breaker: CircuitBreaker::new(5, Duration::from_secs(30)),
            fail_open: true,
        })
    }

    /// Create with custom TTL
    pub fn with_ttl(db_path: &str, ttl_seconds: u64) -> FirewallResult<Self> {
        let mut client = Self::new(db_path)?;
        client.cache_ttl = Duration::from_secs(ttl_seconds);
        Ok(client)
    }

    /// Create from full AtlasConfig (preferred path for policy-driven setup).
    pub fn from_config(config: &AtlasConfig) -> FirewallResult<Self> {
        let mut client = Self::new(&config.db_path)?;
        client.cache_ttl = Duration::from_secs(config.cache_ttl);
        client.fail_open = config.fail_open;
        Ok(client)
    }

    /// Check if a module path exists in Atlas
    ///
    /// Returns true if the module or any symbol within it exists.
    pub fn check_exists(&mut self, module_path: &str) -> FirewallResult<bool> {
        // Check cache first
        if let Some(cached) = self.get_cached(module_path) {
            return Ok(cached);
        }

        // Try to query Atlas
        let module_path_owned = module_path.to_string();

        match self.query_atlas_checked(&module_path_owned) {
            Ok(exists) => {
                self.set_cached(module_path, exists, vec![]);
                Ok(exists)
            }
            Err(e) => {
                // Log error; behavior depends on fail_open flag
                tracing::error!("Atlas query failed for {}: {:?}", module_path, e);
                if self.fail_open {
                    Ok(true)
                } else {
                    Err(e)
                }
            }
        }
    }

    /// Find similar module paths (for suggestions)
    pub fn find_similar(&mut self, module_path: &str, limit: usize) -> FirewallResult<Vec<String>> {
        // Check cache
        if let Some(entry) = self.get_cache_entry(module_path)
            && !entry.suggestions.is_empty()
        {
            return Ok(entry.suggestions.clone());
        }

        // Try to query Atlas
        let module_path_owned = module_path.to_string();

        match self.query_similar_checked(&module_path_owned, limit) {
            Ok(suggestions) => {
                self.update_suggestions(module_path, suggestions.clone());
                Ok(suggestions)
            }
            Err(_) => {
                // Fail gracefully with empty suggestions
                Ok(vec![])
            }
        }
    }

    /// Query Atlas with circuit breaker protection
    fn query_atlas_checked(&mut self, module_path: &str) -> FirewallResult<bool> {
        // Short-circuit if circuit is open
        if self.circuit_breaker.is_open() {
            if self.fail_open {
                tracing::warn!("Atlas circuit breaker open, allowing {}", module_path);
                return Ok(true);
            }

            tracing::warn!("Atlas circuit breaker open, treating {} as unavailable", module_path);
            return Err(FirewallError::PolicyError {
                config_path: "atlas".to_string(),
                reason: "Atlas circuit breaker open".to_string(),
            });
        }

        // Execute query
        match self.query_atlas(module_path) {
            Ok(exists) => {
                // Record success
                let _ = self.circuit_breaker.call::<(), &str, _>(|| Ok(()));
                Ok(exists)
            }
            Err(e) => {
                // Record failure
                let _ = self
                    .circuit_breaker
                    .call::<(), _, _>(|| Err::<(), _>(e.to_string()));
                Err(FirewallError::PolicyError {
                    config_path: "atlas".to_string(),
                    reason: e.to_string(),
                })
            }
        }
    }

    /// Query similar with circuit breaker protection
    fn query_similar_checked(
        &mut self,
        module_path: &str,
        limit: usize,
    ) -> FirewallResult<Vec<String>> {
        if self.circuit_breaker.is_open() {
            return Ok(vec![]);
        }

        match self.query_similar(module_path, limit) {
            Ok(suggestions) => {
                let _ = self.circuit_breaker.call::<(), &str, _>(|| Ok(()));
                Ok(suggestions)
            }
            Err(e) => {
                let _ = self
                    .circuit_breaker
                    .call::<(), _, _>(|| Err::<(), _>(e.to_string()));
                Ok(vec![])
            }
        }
    }

    /// Initialize Atlas lazily
    fn ensure_atlas(&mut self) -> FirewallResult<&mut Atlas> {
        if self.atlas.is_none() {
            // Determine project root from db path
            let project_root = self
                .db_path
                .parent()
                .and_then(|p| p.parent())
                .unwrap_or_else(|| std::path::Path::new("."));

            let atlas = Atlas::new(project_root).map_err(|e| FirewallError::PolicyError {
                config_path: self.db_path.display().to_string(),
                reason: e.to_string(),
            })?;
            self.atlas = Some(atlas);
        }

        match self.atlas.as_mut() {
            Some(atlas) => Ok(atlas),
            None => Err(FirewallError::PolicyError {
                config_path: self.db_path.display().to_string(),
                reason: "Failed to initialize Atlas".to_string(),
            }),
        }
    }

    /// Query Atlas for module existence
    fn query_atlas(&mut self, module_path: &str) -> std::result::Result<bool, AtlasError> {
        let atlas = self
            .ensure_atlas()
            .map_err(|_| AtlasError::database("initialize", "Failed to initialize Atlas"))?;

        // Search for qualified names that match or start with module_path
        let results = atlas.search(module_path, 1)?;

        // Check if any result has a qualified_name that starts with our module_path
        let exists = results.iter().any(|artifact| {
            artifact.qualified_name.starts_with(module_path)
                || artifact.module_path.starts_with(module_path)
        });

        Ok(exists)
    }

    /// Query Atlas for similar modules
    fn query_similar(
        &mut self,
        module_path: &str,
        limit: usize,
    ) -> std::result::Result<Vec<String>, AtlasError> {
        let atlas = self
            .ensure_atlas()
            .map_err(|_| AtlasError::database("initialize", "Failed to initialize Atlas"))?;

        // Extract the last component for fuzzy search
        let symbol_name = module_path.split('.').next_back().unwrap_or(module_path);

        let results = atlas.search(symbol_name, limit)?;

        Ok(results.into_iter().map(|r| r.qualified_name).collect())
    }

    // Cache management

    #[doc(hidden)] // Hide from public docs but allow access in tests
    pub fn get_cached(&self, module_path: &str) -> Option<bool> {
        let cache = self.cache.read();
        if let Some(entry) = cache.get(module_path)
            && entry.cached_at.elapsed() < self.cache_ttl
        {
            return Some(entry.exists);
        }
        None
    }

    fn get_cache_entry(&self, module_path: &str) -> Option<CacheEntry> {
        let cache = self.cache.read();
        if let Some(entry) = cache.get(module_path)
            && entry.cached_at.elapsed() < self.cache_ttl
        {
            return Some(entry.clone());
        }
        None
    }

    #[doc(hidden)] // Hide from public docs but allow access in tests
    pub fn set_cached(&self, module_path: &str, exists: bool, suggestions: Vec<String>) {
        let mut cache = self.cache.write();
        cache.insert(
            module_path.to_string(),
            CacheEntry {
                exists,
                suggestions,
                cached_at: Instant::now(),
            },
        );
    }

    fn update_suggestions(&self, module_path: &str, suggestions: Vec<String>) {
        let mut cache = self.cache.write();
        if let Some(entry) = cache.get_mut(module_path) {
            entry.suggestions = suggestions;
        }
    }

    /// Clear the cache
    pub fn clear_cache(&self) {
        let mut cache = self.cache.write();
        cache.clear();
    }

    /// Get circuit breaker state
    pub fn circuit_state(&self) -> crate::circuit::CircuitState {
        self.circuit_breaker.state()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_atlas_client_creation() {
        // Should not fail even with non-existent path (lazy init)
        let client = AtlasClient::new("/nonexistent/path.db");
        assert!(client.is_ok());
    }

    #[test]
    fn test_cache_ttl() -> FirewallResult<()> {
        let client = AtlasClient::with_ttl("/test.db", 1)?;

        // Set cache
        client.set_cached("test.module", true, vec![]);

        // Should be cached
        assert_eq!(client.get_cached("test.module"), Some(true));

        // Wait for TTL
        std::thread::sleep(Duration::from_secs(2));

        // Should be expired
        assert_eq!(client.get_cached("test.module"), None);
        Ok(())
    }

    #[test]
    fn test_cache_clear() -> FirewallResult<()> {
        let client = AtlasClient::new("/test.db")?;

        client.set_cached("test.module", true, vec![]);
        assert_eq!(client.get_cached("test.module"), Some(true));

        client.clear_cache();
        assert_eq!(client.get_cached("test.module"), None);
        Ok(())
    }
}
