//! Artifact processing and classification.
//!
//! Converts parsed symbols into classified `Artifact` instances.

use crate::parser::ParseResult;
use ranex_core::{Artifact, ArtifactKind, AtlasError};
use std::collections::HashSet;
use std::path::Path;
use tracing::debug;

/// Processes parsed results into classified artifacts.
pub struct ArtifactProcessor<'a> {
    project_root: &'a Path,
}

impl<'a> ArtifactProcessor<'a> {
    /// Create a new artifact processor.
    pub fn new(project_root: &'a Path) -> Self {
        Self { project_root }
    }

    /// Process a parse result into artifacts.
    pub fn process(
        &self,
        parse_result: ParseResult,
        file_path: &Path,
    ) -> Result<Vec<Artifact>, AtlasError> {
        let relative_path = self.relative_path(file_path);
        let module_path = self.path_to_module(&relative_path);
        let feature = self.extract_feature(&relative_path);

        let mut artifacts = Vec::new();

        // Process function definitions
        for def in parse_result.definitions {
            let kind = self.classify_definition(&def);
            let qualified_name = format!("{}.{}", module_path, def.name);

            let mut artifact = Artifact::new(
                &def.name,
                &qualified_name,
                kind,
                &relative_path,
                &module_path,
                def.line_start,
                def.line_end,
            );

            if let Some(sig) = def.signature {
                artifact = artifact.with_signature(sig);
            }

            if let Some(doc) = def.docstring {
                artifact = artifact.with_docstring(doc);
            }

            if let Some(ref f) = feature {
                artifact = artifact.with_feature(f);
            }

            if let Some(ref route) = def.route_path {
                artifact = artifact.with_route_path(route);
            }

            if let Some(ref prefix) = def.router_prefix {
                artifact = artifact.with_router_prefix(prefix);
            }

            if let Some(method) = def
                .tags
                .iter()
                .find_map(|t| t.strip_prefix("http_").map(str::to_string))
            {
                artifact = artifact.with_http_method(method);
            }

            // Add tags based on decorators
            for tag in &def.tags {
                artifact = artifact.with_tag(tag);
            }

            let mut direct_dependencies: Vec<String> = Vec::new();
            let mut security_dependencies: Vec<String> = Vec::new();
            let mut seen_direct: HashSet<String> = HashSet::new();
            let mut seen_security: HashSet<String> = HashSet::new();

            for param in &def.params {
                if !param.is_fastapi_depends {
                    continue;
                }

                let Some(ref target) = param.dependency_target else {
                    continue;
                };

                if seen_direct.insert(target.clone()) {
                    direct_dependencies.push(target.clone());
                }

                if param.is_security_dependency && seen_security.insert(target.clone()) {
                    security_dependencies.push(target.clone());
                }
            }

            if !direct_dependencies.is_empty() {
                artifact = artifact.with_direct_dependencies(direct_dependencies);
            }

            if !security_dependencies.is_empty() {
                artifact = artifact.with_security_dependencies(security_dependencies);
            }

            if !def.request_models.is_empty() {
                artifact.request_models = def.request_models;
            }

            if !def.response_models.is_empty() {
                artifact.response_models = def.response_models;
            }

            artifact.pydantic_fields_summary = def.pydantic_fields_summary;
            artifact.pydantic_validators_summary = def.pydantic_validators_summary;

            artifacts.push(artifact);
        }

        debug!(
            file = %file_path.display(),
            count = artifacts.len(),
            "Processed artifacts"
        );

        Ok(artifacts)
    }

    /// Convert absolute path to relative path.
    fn relative_path(&self, file_path: &Path) -> String {
        file_path
            .strip_prefix(self.project_root)
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_else(|_| file_path.to_string_lossy().to_string())
    }

    /// Convert file path to Python module path.
    ///
    /// Example: `app/features/payment/service.py` -> `app.features.payment.service`
    fn path_to_module(&self, path: &str) -> String {
        path.trim_end_matches(".py").replace(['/', '\\'], ".")
    }

    /// Extract feature name from path.
    ///
    /// Looks for patterns like:
    /// - `features/payment/...` -> "payment"
    /// - `app/payment/...` -> "payment"
    fn extract_feature(&self, path: &str) -> Option<String> {
        let parts: Vec<&str> = path.split('/').collect();

        // Look for "features" directory
        for (i, part) in parts.iter().enumerate() {
            if *part == "features"
                && let Some(next) = parts.get(i + 1)
            {
                return Some((*next).to_string());
            }
        }

        // Look for common app structure: app/<feature>/...
        if let [first, second, ..] = parts.as_slice()
            && (*first == "app" || *first == "src")
            && !["__pycache__", "tests", "utils", "common", "core", "lib"].contains(second)
        {
            return Some((*second).to_string());
        }

        None
    }

    /// Classify a definition into an ArtifactKind.
    fn classify_definition(&self, def: &crate::parser::DefinitionInfo) -> ArtifactKind {
        // Check tags for specific classifications
        for tag in &def.tags {
            match tag.as_str() {
                "fastapi_route" | "http_get" | "http_post" | "http_put" | "http_delete" => {
                    return ArtifactKind::Endpoint;
                }
                "contract" => return ArtifactKind::Contract,
                "pydantic_model" => return ArtifactKind::Model,
                _ => {}
            }
        }

        // Fall back to basic type
        match def.def_type {
            crate::parser::DefinitionType::Function => {
                if def.is_async {
                    ArtifactKind::AsyncFunction
                } else {
                    ArtifactKind::Function
                }
            }
            crate::parser::DefinitionType::Class => ArtifactKind::Class,
            crate::parser::DefinitionType::Method => ArtifactKind::Method,
            crate::parser::DefinitionType::Constant => ArtifactKind::Constant,
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::parser::{
        DefinitionInfo, DefinitionType, FastapiRole, ParseResult, ParameterInfo,
    };
    use super::*;
    use std::error::Error;
    use std::path::Path;

    #[test]
    fn test_path_to_module() {
        let processor = ArtifactProcessor::new(Path::new("/project"));

        assert_eq!(
            processor.path_to_module("app/features/payment/service.py"),
            "app.features.payment.service"
        );
        assert_eq!(
            processor.path_to_module("utils/helpers.py"),
            "utils.helpers"
        );
    }

    #[test]
    fn test_extract_feature() {
        let processor = ArtifactProcessor::new(Path::new("/project"));

        assert_eq!(
            processor.extract_feature("app/features/payment/service.py"),
            Some("payment".to_string())
        );
        assert_eq!(
            processor.extract_feature("app/orders/handlers.py"),
            Some("orders".to_string())
        );
        assert_eq!(processor.extract_feature("utils/helpers.py"), None);
    }

    #[test]
    fn test_process_sets_http_metadata() -> Result<(), Box<dyn Error>> {
        let processor = ArtifactProcessor::new(Path::new("/project"));
        let def = DefinitionInfo {
            name: "read_item".to_string(),
            def_type: DefinitionType::Function,
            signature: Some("read_item(item_id)".to_string()),
            docstring: None,
            line_start: 1,
            line_end: 5,
            is_async: true,
            tags: vec!["fastapi_route".to_string(), "http_get".to_string()],
            route_path: Some("/items/{item_id}".to_string()),
            router_prefix: None,
            base_classes: Vec::new(),
            params: vec![ParameterInfo {
                name: "item_id".to_string(),
                annotation: None,
                default_expr: None,
                is_vararg: false,
                is_kwonly: false,
                is_varkw: false,
                is_fastapi_depends: false,
                dependency_target: None,
                is_security_dependency: false,
                is_background_tasks: false,
                is_fastapi_body: false,
                fastapi_body_embed: None,
                type_names: Vec::new(),
            }, ParameterInfo {
                name: "db".to_string(),
                annotation: None,
                default_expr: None,
                is_vararg: false,
                is_kwonly: false,
                is_varkw: false,
                is_fastapi_depends: true,
                dependency_target: Some("get_db".to_string()),
                is_security_dependency: false,
                is_background_tasks: false,
                is_fastapi_body: false,
                fastapi_body_embed: None,
                type_names: Vec::new(),
            }],
            has_yield: false,
            roles: vec![FastapiRole::Endpoint],
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models: vec!["ItemOut".to_string()],
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        };

        let parse_result = ParseResult {
            hash: "dummy".to_string(),
            definitions: vec![def],
            imports: Vec::new(),
            calls: Vec::new(),
            line_count: 10,
            from_cache: false,
        };

        let artifacts = processor
            .process(parse_result, Path::new("/project/app/main.py"))
            ?;

        let endpoint = artifacts
            .iter()
            .find(|a| a.symbol_name == "read_item")
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "endpoint missing"))?;

        assert_eq!(endpoint.http_method.as_deref(), Some("get"));
        assert_eq!(endpoint.route_path.as_deref(), Some("/items/{item_id}"));
        assert!(endpoint.tags.contains(&"fastapi_route".to_string()));
        assert!(endpoint.tags.contains(&"http_get".to_string()));

        assert_eq!(endpoint.direct_dependencies, vec!["get_db".to_string()]);
        assert!(endpoint.security_dependencies.is_empty());

        assert!(endpoint.request_models.is_empty());
        assert_eq!(endpoint.response_models, vec!["ItemOut".to_string()]);
        Ok(())
    }
}
