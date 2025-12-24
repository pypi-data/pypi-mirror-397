//! Pattern detection for code analysis.
//!
//! Identifies common architectural patterns in the codebase:
//! - **CRUD**: Services with create, read, update, delete methods
//! - **Repository**: Data access layer pattern
//! - **Factory**: Object creation pattern
//! - **Service Layer**: Business logic encapsulation
//! - **Singleton**: Single instance pattern
//!
//! ## Example
//!
//! ```rust,ignore
//! use ranex_atlas::analysis::{PatternDetector, PatternType};
//!
//! let detector = PatternDetector::new(&artifacts);
//! let patterns = detector.detect_all()?;
//!
//! for pattern in patterns {
//!     println!("{:?}: {} (confidence: {:.0}%)",
//!         pattern.pattern_type,
//!         pattern.name,
//!         pattern.confidence.as_percentage()
//!     );
//! }
//! ```

use ranex_core::{Artifact, ArtifactKind};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

/// Type of architectural pattern.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PatternType {
    /// CRUD operations (create, read, update, delete).
    Crud,
    /// Repository pattern (data access layer).
    Repository,
    /// Factory pattern (object creation).
    Factory,
    /// Service layer pattern.
    ServiceLayer,
    /// Singleton pattern.
    Singleton,
    /// Strategy pattern.
    Strategy,
    /// Observer/event pattern.
    Observer,
    /// Decorator pattern.
    Decorator,
    /// Adapter pattern.
    Adapter,
    /// Facade pattern.
    Facade,
}

impl PatternType {
    /// Convert to string.
    pub fn as_str(&self) -> &'static str {
        match self {
            PatternType::Crud => "crud",
            PatternType::Repository => "repository",
            PatternType::Factory => "factory",
            PatternType::ServiceLayer => "service_layer",
            PatternType::Singleton => "singleton",
            PatternType::Strategy => "strategy",
            PatternType::Observer => "observer",
            PatternType::Decorator => "decorator",
            PatternType::Adapter => "adapter",
            PatternType::Facade => "facade",
        }
    }

    /// Parse from string.
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "crud" => Some(PatternType::Crud),
            "repository" => Some(PatternType::Repository),
            "factory" => Some(PatternType::Factory),
            "service_layer" | "service" => Some(PatternType::ServiceLayer),
            "singleton" => Some(PatternType::Singleton),
            "strategy" => Some(PatternType::Strategy),
            "observer" => Some(PatternType::Observer),
            "decorator" => Some(PatternType::Decorator),
            "adapter" => Some(PatternType::Adapter),
            "facade" => Some(PatternType::Facade),
            _ => None,
        }
    }

    /// Get human-readable description.
    pub fn description(&self) -> &'static str {
        match self {
            PatternType::Crud => "Create, Read, Update, Delete operations",
            PatternType::Repository => "Data access layer abstracting persistence",
            PatternType::Factory => "Object creation encapsulation",
            PatternType::ServiceLayer => "Business logic encapsulation",
            PatternType::Singleton => "Single instance guarantee",
            PatternType::Strategy => "Interchangeable algorithms",
            PatternType::Observer => "Event/notification pattern",
            PatternType::Decorator => "Dynamic behavior extension",
            PatternType::Adapter => "Interface compatibility layer",
            PatternType::Facade => "Simplified interface to complex subsystem",
        }
    }
}

impl std::fmt::Display for PatternType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Confidence level for pattern detection.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct PatternConfidence(f64);

impl PatternConfidence {
    /// Create a new confidence value (clamped to 0.0-1.0).
    pub fn new(value: f64) -> Self {
        Self(value.clamp(0.0, 1.0))
    }

    /// Get the raw value.
    pub fn value(&self) -> f64 {
        self.0
    }

    /// Get as percentage (0-100).
    pub fn as_percentage(&self) -> f64 {
        self.0 * 100.0
    }

    /// High confidence threshold (>= 80%).
    pub fn is_high(&self) -> bool {
        self.0 >= 0.8
    }

    /// Medium confidence threshold (>= 50%).
    pub fn is_medium(&self) -> bool {
        self.0 >= 0.5
    }
}

impl Default for PatternConfidence {
    fn default() -> Self {
        Self(0.0)
    }
}

/// A detected pattern in the codebase.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectedPattern {
    /// Type of pattern detected.
    pub pattern_type: PatternType,

    /// Name of the class/module implementing the pattern.
    pub name: String,

    /// File path where the pattern is found.
    pub file_path: String,

    /// Confidence level of detection.
    pub confidence: PatternConfidence,

    /// Artifacts that are part of this pattern.
    pub artifacts: Vec<String>,

    /// Methods/functions that indicate this pattern.
    pub indicators: Vec<String>,

    /// Human-readable explanation.
    pub explanation: String,
}

impl DetectedPattern {
    /// Create a new detected pattern.
    pub fn new(
        pattern_type: PatternType,
        name: impl Into<String>,
        file_path: impl Into<String>,
        confidence: PatternConfidence,
    ) -> Self {
        Self {
            pattern_type,
            name: name.into(),
            file_path: file_path.into(),
            confidence,
            artifacts: Vec::new(),
            indicators: Vec::new(),
            explanation: String::new(),
        }
    }

    /// Add an artifact to the pattern.
    pub fn with_artifact(mut self, artifact: impl Into<String>) -> Self {
        self.artifacts.push(artifact.into());
        self
    }

    /// Add an indicator.
    pub fn with_indicator(mut self, indicator: impl Into<String>) -> Self {
        self.indicators.push(indicator.into());
        self
    }

    /// Set explanation.
    pub fn with_explanation(mut self, explanation: impl Into<String>) -> Self {
        self.explanation = explanation.into();
        self
    }
}

/// Pattern detection engine.
pub struct PatternDetector<'a> {
    artifacts: &'a [Artifact],
    min_confidence: PatternConfidence,
}

impl<'a> PatternDetector<'a> {
    /// Create a new pattern detector.
    pub fn new(artifacts: &'a [Artifact]) -> Self {
        Self {
            artifacts,
            min_confidence: PatternConfidence::new(0.5),
        }
    }

    /// Set minimum confidence threshold for reporting.
    pub fn with_min_confidence(mut self, confidence: f64) -> Self {
        self.min_confidence = PatternConfidence::new(confidence);
        self
    }

    /// Detect all patterns in the codebase.
    pub fn detect_all(&self) -> Vec<DetectedPattern> {
        let mut patterns = Vec::new();

        patterns.extend(self.detect_crud_patterns());
        patterns.extend(self.detect_repository_patterns());
        patterns.extend(self.detect_factory_patterns());
        patterns.extend(self.detect_service_layer_patterns());
        patterns.extend(self.detect_singleton_patterns());

        // Filter by minimum confidence
        patterns.retain(|p| p.confidence >= self.min_confidence);

        patterns
    }

    /// Detect CRUD patterns.
    fn detect_crud_patterns(&self) -> Vec<DetectedPattern> {
        let crud_indicators = [
            "create", "read", "get", "update", "delete", "remove", "list", "find",
        ];
        let mut patterns = Vec::new();

        // Group artifacts by class
        let classes = self.group_by_class();

        for (class_name, methods) in classes {
            // Collect owned strings first
            let method_names: Vec<String> = methods
                .iter()
                .map(|a| a.symbol_name.to_lowercase())
                .collect();

            // Count CRUD indicators
            let mut found_indicators = Vec::new();
            for indicator in &crud_indicators {
                if method_names.iter().any(|m| m.contains(indicator)) {
                    found_indicators.push(*indicator);
                }
            }

            // Need at least 3 CRUD operations for a pattern
            if found_indicators.len() >= 3 {
                let confidence = PatternConfidence::new(found_indicators.len() as f64 / 4.0);
                let file_path = methods
                    .first()
                    .map(|a| a.file_path.to_string_lossy().to_string())
                    .unwrap_or_default();

                let mut pattern =
                    DetectedPattern::new(PatternType::Crud, &class_name, file_path, confidence);

                pattern.indicators = found_indicators.iter().map(|s| s.to_string()).collect();
                pattern.explanation = format!(
                    "Class '{}' implements CRUD operations: {}",
                    class_name,
                    found_indicators.join(", ")
                );

                for method in &methods {
                    pattern.artifacts.push(method.qualified_name.clone());
                }

                patterns.push(pattern);
            }
        }

        // Also check for CRUD patterns at the file/module level (for functions)
        patterns.extend(self.detect_file_crud_patterns(&crud_indicators));

        patterns
    }

    /// Detect CRUD patterns in functions grouped by file.
    fn detect_file_crud_patterns(&self, crud_indicators: &[&str]) -> Vec<DetectedPattern> {
        let mut patterns = Vec::new();
        let file_groups = self.group_by_file();

        for (file_path, functions) in file_groups {
            // Only consider files with multiple functions
            if functions.len() < 3 {
                continue;
            }

            let func_names: Vec<String> = functions
                .iter()
                .map(|a| a.symbol_name.to_lowercase())
                .collect();

            // Count CRUD indicators
            let mut found_indicators = Vec::new();
            for indicator in crud_indicators {
                if func_names.iter().any(|m| m.contains(indicator)) {
                    found_indicators.push(*indicator);
                }
            }

            // Need at least 3 CRUD operations for a pattern
            if found_indicators.len() >= 3 {
                let confidence = PatternConfidence::new(found_indicators.len() as f64 / 4.0);

                // Use file name as the pattern name
                let module_name = std::path::Path::new(&file_path)
                    .file_stem()
                    .map(|s| s.to_string_lossy().to_string())
                    .unwrap_or_else(|| file_path.clone());

                let mut pattern =
                    DetectedPattern::new(PatternType::Crud, &module_name, file_path, confidence);

                pattern.indicators = found_indicators.iter().map(|s| s.to_string()).collect();
                pattern.explanation = format!(
                    "Module '{}' implements CRUD operations: {}",
                    module_name,
                    found_indicators.join(", ")
                );

                for func in &functions {
                    pattern.artifacts.push(func.qualified_name.clone());
                }

                patterns.push(pattern);
            }
        }

        patterns
    }

    /// Detect Repository patterns.
    fn detect_repository_patterns(&self) -> Vec<DetectedPattern> {
        let repo_indicators = [
            "find", "save", "delete", "get_by", "find_by", "query", "fetch",
        ];
        let repo_name_patterns = ["repository", "repo", "dao", "store"];
        let mut patterns = Vec::new();

        let classes = self.group_by_class();

        for (class_name, methods) in classes {
            let class_lower = class_name.to_lowercase();

            // Check if class name suggests repository
            let name_match = repo_name_patterns.iter().any(|p| class_lower.contains(p));

            // Check method names
            let method_names: HashSet<String> = methods
                .iter()
                .map(|a| a.symbol_name.to_lowercase())
                .collect();

            let indicator_count = repo_indicators
                .iter()
                .filter(|ind| method_names.iter().any(|m| m.contains(*ind)))
                .count();

            // Calculate confidence
            let name_score = if name_match { 0.4 } else { 0.0 };
            let method_score = (indicator_count as f64 / repo_indicators.len() as f64) * 0.6;
            let confidence = PatternConfidence::new(name_score + method_score);

            if confidence.is_medium() {
                let file_path = methods
                    .first()
                    .map(|a| a.file_path.to_string_lossy().to_string())
                    .unwrap_or_default();

                let pattern = DetectedPattern::new(
                    PatternType::Repository,
                    &class_name,
                    file_path,
                    confidence,
                )
                .with_explanation(format!(
                    "Class '{}' follows Repository pattern (data access abstraction)",
                    class_name
                ));

                patterns.push(pattern);
            }
        }

        patterns
    }

    /// Detect Factory patterns.
    fn detect_factory_patterns(&self) -> Vec<DetectedPattern> {
        let factory_indicators = ["create", "make", "build", "new", "get_instance", "produce"];
        let factory_name_patterns = ["factory", "builder", "creator"];
        let mut patterns = Vec::new();

        let classes = self.group_by_class();

        for (class_name, methods) in classes {
            let class_lower = class_name.to_lowercase();

            let name_match = factory_name_patterns
                .iter()
                .any(|p| class_lower.contains(p));

            let method_names: HashSet<String> = methods
                .iter()
                .map(|a| a.symbol_name.to_lowercase())
                .collect();

            let indicator_count = factory_indicators
                .iter()
                .filter(|ind| method_names.iter().any(|m| m.starts_with(*ind)))
                .count();

            let name_score = if name_match { 0.5 } else { 0.0 };
            let method_score = (indicator_count as f64 / 3.0).min(0.5);
            let confidence = PatternConfidence::new(name_score + method_score);

            if confidence.is_medium() {
                let file_path = methods
                    .first()
                    .map(|a| a.file_path.to_string_lossy().to_string())
                    .unwrap_or_default();

                let pattern =
                    DetectedPattern::new(PatternType::Factory, &class_name, file_path, confidence)
                        .with_explanation(format!(
                            "Class '{}' follows Factory pattern (object creation)",
                            class_name
                        ));

                patterns.push(pattern);
            }
        }

        patterns
    }

    /// Detect Service Layer patterns.
    fn detect_service_layer_patterns(&self) -> Vec<DetectedPattern> {
        let service_name_patterns = ["service", "manager", "handler", "controller"];
        let mut patterns = Vec::new();

        let classes = self.group_by_class();

        for (class_name, methods) in classes {
            let class_lower = class_name.to_lowercase();

            let name_match = service_name_patterns
                .iter()
                .any(|p| class_lower.ends_with(p));

            // Services typically have multiple public methods
            let method_count = methods.len();

            if name_match && method_count >= 2 {
                let confidence =
                    PatternConfidence::new(0.6 + (method_count as f64 / 10.0).min(0.4));

                let file_path = methods
                    .first()
                    .map(|a| a.file_path.to_string_lossy().to_string())
                    .unwrap_or_default();

                let pattern = DetectedPattern::new(
                    PatternType::ServiceLayer,
                    &class_name,
                    file_path,
                    confidence,
                )
                .with_explanation(format!(
                    "Class '{}' is a service layer component ({} methods)",
                    class_name, method_count
                ));

                patterns.push(pattern);
            }
        }

        patterns
    }

    /// Detect Singleton patterns.
    fn detect_singleton_patterns(&self) -> Vec<DetectedPattern> {
        let singleton_indicators = ["get_instance", "instance", "_instance", "getInstance"];
        let mut patterns = Vec::new();

        let classes = self.group_by_class();

        for (class_name, methods) in classes {
            let method_names: HashSet<String> = methods
                .iter()
                .map(|a| a.symbol_name.to_lowercase())
                .collect();

            let has_singleton_method = singleton_indicators
                .iter()
                .any(|ind| method_names.iter().any(|m| m.contains(&ind.to_lowercase())));

            if has_singleton_method {
                let file_path = methods
                    .first()
                    .map(|a| a.file_path.to_string_lossy().to_string())
                    .unwrap_or_default();

                let pattern = DetectedPattern::new(
                    PatternType::Singleton,
                    &class_name,
                    file_path,
                    PatternConfidence::new(0.7),
                )
                .with_explanation(format!(
                    "Class '{}' appears to implement Singleton pattern",
                    class_name
                ));

                patterns.push(pattern);
            }
        }

        patterns
    }

    /// Group artifacts by their containing class.
    fn group_by_class(&self) -> HashMap<String, Vec<&Artifact>> {
        let mut classes: HashMap<String, Vec<&Artifact>> = HashMap::new();

        for artifact in self.artifacts {
            // Extract class name from qualified name
            // e.g., "app.service.OrderService.get_order" -> "OrderService"
            if artifact.kind == ArtifactKind::Method || artifact.kind == ArtifactKind::Class {
                let parts: Vec<&str> = artifact.qualified_name.split('.').collect();
                if parts.len() >= 2 {
                    let class_name_opt = if artifact.kind == ArtifactKind::Class {
                        parts.last()
                    } else {
                        // For methods, get the second-to-last part
                        parts.get(parts.len() - 2)
                    };

                    if let Some(class_name) = class_name_opt {
                        classes
                            .entry((*class_name).to_string())
                            .or_default()
                            .push(artifact);
                    }
                }
            }
        }

        classes
    }

    /// Group artifacts by their file path.
    /// This is useful for detecting patterns at the module/file level.
    fn group_by_file(&self) -> HashMap<String, Vec<&Artifact>> {
        let mut files: HashMap<String, Vec<&Artifact>> = HashMap::new();

        for artifact in self.artifacts {
            // Include functions and async functions (not methods which belong to classes)
            if artifact.kind == ArtifactKind::Function
                || artifact.kind == ArtifactKind::AsyncFunction
                || artifact.kind == ArtifactKind::Endpoint
            {
                let file_path = artifact.file_path.to_string_lossy().to_string();
                files.entry(file_path).or_default().push(artifact);
            }
        }

        files
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn make_artifact(name: &str, qualified: &str, kind: ArtifactKind) -> Artifact {
        Artifact {
            symbol_name: name.to_string(),
            qualified_name: qualified.to_string(),
            kind,
            file_path: PathBuf::from("test.py"),
            module_path: "test".to_string(),
            signature: None,
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
    fn test_crud_pattern_detection() {
        let artifacts = vec![
            make_artifact("OrderService", "app.OrderService", ArtifactKind::Class),
            make_artifact(
                "create_order",
                "app.OrderService.create_order",
                ArtifactKind::Method,
            ),
            make_artifact(
                "get_order",
                "app.OrderService.get_order",
                ArtifactKind::Method,
            ),
            make_artifact(
                "update_order",
                "app.OrderService.update_order",
                ArtifactKind::Method,
            ),
            make_artifact(
                "delete_order",
                "app.OrderService.delete_order",
                ArtifactKind::Method,
            ),
        ];

        let detector = PatternDetector::new(&artifacts);
        let patterns = detector.detect_crud_patterns();

        assert!(!patterns.is_empty());
        assert!(patterns.iter().any(|p| p.pattern_type == PatternType::Crud));
    }

    #[test]
    fn test_repository_pattern_detection() {
        let artifacts = vec![
            make_artifact(
                "OrderRepository",
                "app.OrderRepository",
                ArtifactKind::Class,
            ),
            make_artifact(
                "find_by_id",
                "app.OrderRepository.find_by_id",
                ArtifactKind::Method,
            ),
            make_artifact("save", "app.OrderRepository.save", ArtifactKind::Method),
            make_artifact("delete", "app.OrderRepository.delete", ArtifactKind::Method),
        ];

        let detector = PatternDetector::new(&artifacts);
        let patterns = detector.detect_repository_patterns();

        assert!(!patterns.is_empty());
        assert!(patterns
            .iter()
            .any(|p| p.pattern_type == PatternType::Repository));
    }

    #[test]
    fn test_service_layer_detection() {
        let artifacts = vec![
            make_artifact("PaymentService", "app.PaymentService", ArtifactKind::Class),
            make_artifact(
                "process",
                "app.PaymentService.process",
                ArtifactKind::Method,
            ),
            make_artifact("refund", "app.PaymentService.refund", ArtifactKind::Method),
            make_artifact(
                "validate",
                "app.PaymentService.validate",
                ArtifactKind::Method,
            ),
        ];

        let detector = PatternDetector::new(&artifacts);
        let patterns = detector.detect_service_layer_patterns();

        assert!(!patterns.is_empty());
    }

    #[test]
    fn test_confidence_levels() {
        assert!(PatternConfidence::new(0.9).is_high());
        assert!(PatternConfidence::new(0.6).is_medium());
        assert!(!PatternConfidence::new(0.3).is_medium());
    }

    #[test]
    fn test_pattern_type_roundtrip() {
        for pattern in [
            PatternType::Crud,
            PatternType::Repository,
            PatternType::Factory,
            PatternType::ServiceLayer,
        ] {
            let s = pattern.as_str();
            let parsed = PatternType::parse(s);
            assert_eq!(parsed, Some(pattern));
        }
    }
}
