//! Symbol extraction from Python AST.
//!
//! Walks the AST tree to extract function and class definitions,
//! including their signatures, docstrings, and decorators.
//!
//! ## FastAPI Endpoint Detection
//!
//! This extractor supports the full range of FastAPI routing patterns:
//! - `@app.get/post/put/delete/patch` - Direct app routes
//! - `@router.get/post/put/delete/patch` - APIRouter routes (most common in production)
//! - `@<any_name>.get/post/put/delete/patch` - Any router instance
//!
//! All detected HTTP decorators receive both the HTTP method tag (e.g., "http_get")
//! and the "fastapi_route" tag for consistent classification.

// Fields stored for future use in enhanced extraction

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList};
use ranex_core::AtlasError;
use serde::Serialize;
use std::collections::HashMap;
use std::path::PathBuf;

/// HTTP methods supported by FastAPI.
const HTTP_METHODS: &[&str] = &["get", "post", "put", "delete", "patch", "options", "head"];

/// Pydantic base classes that indicate a model.
const PYDANTIC_BASES: &[&str] = &["BaseModel", "BaseSettings", "BaseConfig"];

/// Type of definition.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DefinitionType {
    Function,
    Class,
    Method,
    Constant,
}

/// Information about an import statement.
#[derive(Debug, Clone)]
pub struct ImportInfo {
    /// The module being imported (e.g., "os.path" or "app.utils")
    pub module_name: String,

    /// Specific names imported (for "from x import y, z")
    pub imported_names: Vec<String>,

    /// Import alias if any (e.g., "np" for "import numpy as np")
    pub alias: Option<String>,

    /// Line number of the import statement (1-indexed)
    pub line_number: usize,

    /// Whether this is a relative import (starts with .)
    pub is_relative: bool,

    /// Relative import level (number of dots: 1 for ".", 2 for "..", etc.)
    pub relative_level: usize,

    /// Whether this is a wildcard import (from x import *)
    pub is_wildcard: bool,
}

/// Information about a function call extracted from AST.
#[derive(Debug, Clone)]
pub struct CallInfo {
    /// Name of the caller function (qualified if possible)
    pub caller_name: String,

    /// Name of the called function/method
    pub callee_name: String,

    /// Line number of the call site (1-indexed)
    pub line_number: usize,

    /// Whether this is an async call (await)
    pub is_async: bool,

    /// Whether this is a method call (has attribute access)
    pub is_method: bool,
}

/// Information about a function parameter.
#[derive(Debug, Clone)]
pub struct ParameterInfo {
    /// Parameter name
    pub name: String,

    /// Type annotation as a string (if any)
    pub annotation: Option<String>,

    /// Default value expression as a string (if any)
    pub default_expr: Option<String>,

    /// True if this is *args
    pub is_vararg: bool,

    /// True if this is a keyword-only argument
    pub is_kwonly: bool,

    /// True if this is **kwargs
    pub is_varkw: bool,

    /// True if this parameter is a FastAPI dependency (Depends(...))
    pub is_fastapi_depends: bool,

    /// Dependency callable name (if this parameter is a dependency).
    ///
    /// Examples: "get_db", "get_current_user", "oauth2_bearer".
    pub dependency_target: Option<String>,

    /// True if this dependency is security-related (e.g., Security(...) or depends on OAuth2PasswordBearer).
    pub is_security_dependency: bool,

    /// True if this parameter is a FastAPI BackgroundTasks parameter
    pub is_background_tasks: bool,

    pub is_fastapi_body: bool,

    pub fastapi_body_embed: Option<bool>,

    pub type_names: Vec<String>,
}

#[derive(Debug, Clone)]
struct DependencyAliasInfo {
    target: String,
    is_security: bool,
}

#[derive(Debug, Clone, Serialize)]
struct PydanticFieldSummary {
    name: String,
    type_expr: Option<String>,
    has_default: bool,
}

#[derive(Debug, Clone, Serialize)]
struct PydanticValidatorSummary {
    name: String,
    kind: String,
    fields: Vec<String>,
    mode: Option<String>,
}

#[derive(Debug, Clone)]
struct ParsedPydanticValidatorDecorator {
    kind: String,
    fields: Vec<String>,
    mode: Option<String>,
}

/// Role of a FastAPI-related function or method.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FastapiRole {
    Endpoint,
    Dependency,
    LifespanStartup,
    LifespanShutdown,
    Middleware,
    BackgroundTaskProducer,
}

/// Information about a function or class definition.
#[derive(Debug, Clone)]
pub struct DefinitionInfo {
    /// Name of the symbol
    pub name: String,

    /// Type of definition
    pub def_type: DefinitionType,

    /// Function signature (for functions/methods)
    pub signature: Option<String>,

    /// Extracted docstring
    pub docstring: Option<String>,

    /// Starting line number (1-indexed)
    pub line_start: usize,

    /// Ending line number (1-indexed)
    pub line_end: usize,

    /// Whether this is an async function
    pub is_async: bool,

    /// Tags from decorators (e.g., "fastapi_route", "contract")
    pub tags: Vec<String>,

    /// HTTP route path if this is an endpoint (e.g., "/payments/{id}")
    pub route_path: Option<String>,

    /// Router prefix if available (e.g., "/api/v1" from APIRouter(prefix=...)).
    pub router_prefix: Option<String>,

    /// Base classes for class definitions
    pub base_classes: Vec<String>,

    /// Function parameters (for functions/methods)
    pub params: Vec<ParameterInfo>,

    /// True if the function body contains a yield / yield from
    pub has_yield: bool,

    /// FastAPI-specific roles inferred from decorators/tags
    pub roles: Vec<FastapiRole>,

    /// Number of fields for class definitions (especially Pydantic models)
    pub field_count: Option<usize>,

    /// Number of fields that reference other models (optional, computed later)
    pub nested_model_field_count: Option<usize>,

    /// Maximum nested model depth (optional, computed later)
    pub max_nested_model_depth: Option<usize>,

    /// Number of Pydantic validators defined on the model (optional)
    pub validator_count: Option<usize>,

    pub request_models: Vec<String>,

    pub response_models: Vec<String>,

    pub pydantic_fields_summary: Option<String>,

    pub pydantic_validators_summary: Option<String>,
}

/// Extracts symbols from Python AST.
pub struct SymbolExtractor;

impl Default for SymbolExtractor {
    fn default() -> Self {
        Self::new()
    }
}

impl SymbolExtractor {
    /// Create a new symbol extractor.
    pub fn new() -> Self {
        Self
    }

    /// Extract definitions from an AST tree.
    pub fn extract_from_tree(&self, tree: Bound<'_, PyAny>) -> Result<Vec<DefinitionInfo>, AtlasError> {
        let mut definitions = Vec::new();

        // Get the body of the module
        let body = tree.getattr("body").map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get AST body: {}", e),
        })?;

        // Iterate through top-level statements
        if let Ok(body_list) = body.cast::<PyList>() {
            let router_prefixes = self.collect_router_prefixes(body_list)?;
            let dep_aliases = self.collect_dependency_aliases(body_list)?;
            let security_deps = self.collect_security_dependables(body_list)?;
            for item in body_list.iter() {
                self.extract_from_node(
                    &item,
                    &mut definitions,
                    false,
                    &router_prefixes,
                    &dep_aliases,
                    &security_deps,
                )?;
            }

            let model_names: std::collections::HashSet<String> = definitions
                .iter()
                .filter(|d| d.tags.iter().any(|t| t == "pydantic_model"))
                .map(|d| d.name.clone())
                .collect();

            for def in &mut definitions {
                if !def.tags.iter().any(|t| t == "fastapi_route") {
                    continue;
                }

                let mut request_models: Vec<String> = Vec::new();
                let mut seen: std::collections::HashSet<String> =
                    std::collections::HashSet::new();

                for param in &def.params {
                    if param.is_fastapi_depends || param.is_background_tasks {
                        continue;
                    }

                    for name in &param.type_names {
                        if model_names.contains(name) && seen.insert(name.clone()) {
                            request_models.push(name.clone());
                        }
                    }
                }

                def.request_models = request_models;
            }
        }

        Ok(definitions)
    }

    /// Extract all imports from an AST tree.
    pub fn extract_imports_from_tree(
        &self,
        tree: Bound<'_, PyAny>,
    ) -> Result<Vec<ImportInfo>, AtlasError> {
        let mut imports = Vec::new();

        // Get the body of the module
        let body = tree.getattr("body").map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get AST body: {}", e),
        })?;

        // Iterate through top-level statements
        if let Ok(body_list) = body.cast::<PyList>() {
            for item in body_list.iter() {
                self.extract_imports_from_node(&item, &mut imports)?;
            }
        }

        Ok(imports)
    }

    /// Extract all function calls from an AST tree.
    ///
    /// Walks through function/method bodies to find Call nodes.
    /// Per Python AST docs: Call(expr func, expr* args, keyword* keywords)
    pub fn extract_calls_from_tree(
        &self,
        tree: Bound<'_, PyAny>,
    ) -> Result<Vec<CallInfo>, AtlasError> {
        let mut calls = Vec::new();

        // Get the body of the module
        let body = tree.getattr("body").map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get AST body: {}", e),
        })?;

        // Iterate through top-level statements looking for function/class definitions
        if let Ok(body_list) = body.cast::<PyList>() {
            for item in body_list.iter() {
                self.extract_calls_from_node(&item, "", &mut calls)?;
            }
        }

        Ok(calls)
    }

    /// Extract calls from an AST node recursively.
    ///
    /// `current_function` is the qualified name of the current function context.
    fn extract_calls_from_node(
        &self,
        node: &Bound<'_, PyAny>,
        current_function: &str,
        calls: &mut Vec<CallInfo>,
    ) -> Result<(), AtlasError> {
        let node_type = self.get_node_type(node)?;

        match node_type.as_str() {
            "FunctionDef" | "AsyncFunctionDef" => {
                // Get function name to track caller context
                let func_name = self.get_str_attr(node, "name").unwrap_or_default();
                let qualified_name = if current_function.is_empty() {
                    func_name.clone()
                } else {
                    format!("{}.{}", current_function, func_name)
                };

                // Walk the function body to find calls
                if let Ok(body) = node.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for stmt in body_list.iter() {
                        self.extract_calls_from_statement(&stmt, &qualified_name, calls)?;
                    }
                }
            }
            "ClassDef" => {
                // Get class name for context
                let class_name = self.get_str_attr(node, "name").unwrap_or_default();
                let qualified_name = if current_function.is_empty() {
                    class_name.clone()
                } else {
                    format!("{}.{}", current_function, class_name)
                };

                // Recurse into class body to find methods
                if let Ok(body) = node.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for item in body_list.iter() {
                        self.extract_calls_from_node(&item, &qualified_name, calls)?;
                    }
                }
            }
            _ => {}
        }

        Ok(())
    }

    /// Extract calls from a statement within a function body.
    fn extract_calls_from_statement(
        &self,
        stmt: &Bound<'_, PyAny>,
        caller: &str,
        calls: &mut Vec<CallInfo>,
    ) -> Result<(), AtlasError> {
        let node_type = self.get_node_type(stmt)?;

        match node_type.as_str() {
            "Expr" => {
                // Expression statement - check if it's a Call
                if let Ok(value) = stmt.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            "Assign" | "AnnAssign" => {
                // Assignment - check RHS for calls
                if let Ok(value) = stmt.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            "Return" => {
                // Return statement - check value for calls
                if let Ok(value) = stmt.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            "If" | "While" => {
                // Conditionals - check test and body
                if let Ok(test) = stmt.getattr("test") {
                    self.extract_calls_from_expr(&test, caller, false, calls)?;
                }
                if let Ok(body) = stmt.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for s in body_list.iter() {
                        self.extract_calls_from_statement(&s, caller, calls)?;
                    }
                }
                if let Ok(orelse) = stmt.getattr("orelse")
                    && let Ok(orelse_list) = orelse.cast::<PyList>()
                {
                    for s in orelse_list.iter() {
                        self.extract_calls_from_statement(&s, caller, calls)?;
                    }
                }
            }
            "For" | "AsyncFor" => {
                // For loops - check iter and body
                if let Ok(iter_expr) = stmt.getattr("iter") {
                    self.extract_calls_from_expr(&iter_expr, caller, false, calls)?;
                }
                if let Ok(body) = stmt.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for s in body_list.iter() {
                        self.extract_calls_from_statement(&s, caller, calls)?;
                    }
                }
            }
            "With" | "AsyncWith" => {
                // With statements - check items and body
                if let Ok(items) = stmt.getattr("items")
                    && let Ok(items_list) = items.cast::<PyList>()
                {
                    for item in items_list.iter() {
                        if let Ok(context_expr) = item.getattr("context_expr") {
                            self.extract_calls_from_expr(&context_expr, caller, false, calls)?;
                        }
                    }
                }
                if let Ok(body) = stmt.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for s in body_list.iter() {
                        self.extract_calls_from_statement(&s, caller, calls)?;
                    }
                }
            }
            "Try" | "TryStar" => {
                // Try statements - check body, handlers, else, finally
                for attr in &["body", "orelse", "finalbody"] {
                    if let Ok(block) = stmt.getattr(*attr)
                        && let Ok(block_list) = block.cast::<PyList>()
                    {
                        for s in block_list.iter() {
                            self.extract_calls_from_statement(&s, caller, calls)?;
                        }
                    }
                }
                if let Ok(handlers) = stmt.getattr("handlers")
                    && let Ok(handlers_list) = handlers.cast::<PyList>()
                {
                    for handler in handlers_list.iter() {
                        if let Ok(body) = handler.getattr("body")
                            && let Ok(body_list) = body.cast::<PyList>()
                        {
                            for s in body_list.iter() {
                                self.extract_calls_from_statement(&s, caller, calls)?;
                            }
                        }
                    }
                }
            }
            "Raise" => {
                // Raise - check exc expression
                if let Ok(exc) = stmt.getattr("exc") {
                    self.extract_calls_from_expr(&exc, caller, false, calls)?;
                }
            }
            _ => {}
        }

        Ok(())
    }

    /// Extract calls from an expression.
    fn extract_calls_from_expr(
        &self,
        expr: &Bound<'_, PyAny>,
        caller: &str,
        is_await: bool,
        calls: &mut Vec<CallInfo>,
    ) -> Result<(), AtlasError> {
        // Check for None (Python None becomes a PyNone which we need to handle)
        if expr.is_none() {
            return Ok(());
        }

        let node_type = self.get_node_type(expr)?;

        match node_type.as_str() {
            "Call" => {
                // This is a function call - extract it
                if let Ok(func) = expr.getattr("func") {
                    let (callee_name, is_method) = self.resolve_callee_name(&func)?;
                    let line_number = self.get_int_attr(expr, "lineno").unwrap_or(0) as usize;

                    if !callee_name.is_empty() {
                        calls.push(CallInfo {
                            caller_name: caller.to_string(),
                            callee_name,
                            line_number,
                            is_async: is_await,
                            is_method,
                        });
                    }
                }

                // Also check arguments for nested calls
                if let Ok(args) = expr.getattr("args")
                    && let Ok(args_list) = args.cast::<PyList>()
                {
                    for arg in args_list.iter() {
                        self.extract_calls_from_expr(&arg, caller, false, calls)?;
                    }
                }
            }
            "Await" => {
                // Await expression - mark as async and recurse
                if let Ok(value) = expr.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, true, calls)?;
                }
            }
            "BinOp" | "BoolOp" | "UnaryOp" | "Compare" => {
                // Binary/boolean operations - check operands
                for attr in &["left", "right", "operand"] {
                    if let Ok(operand) = expr.getattr(*attr) {
                        self.extract_calls_from_expr(&operand, caller, false, calls)?;
                    }
                }
                if let Ok(values) = expr.getattr("values")
                    && let Ok(values_list) = values.cast::<PyList>()
                {
                    for v in values_list.iter() {
                        self.extract_calls_from_expr(&v, caller, false, calls)?;
                    }
                }
                if let Ok(comparators) = expr.getattr("comparators")
                    && let Ok(comp_list) = comparators.cast::<PyList>()
                {
                    for c in comp_list.iter() {
                        self.extract_calls_from_expr(&c, caller, false, calls)?;
                    }
                }
            }
            "IfExp" => {
                // Ternary expression
                for attr in &["test", "body", "orelse"] {
                    if let Ok(part) = expr.getattr(*attr) {
                        self.extract_calls_from_expr(&part, caller, false, calls)?;
                    }
                }
            }
            "ListComp" | "SetComp" | "GeneratorExp" => {
                // Comprehensions - check elt and generators
                if let Ok(elt) = expr.getattr("elt") {
                    self.extract_calls_from_expr(&elt, caller, false, calls)?;
                }
            }
            "DictComp" => {
                // Dict comprehension
                if let Ok(key) = expr.getattr("key") {
                    self.extract_calls_from_expr(&key, caller, false, calls)?;
                }
                if let Ok(value) = expr.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            "List" | "Tuple" | "Set" => {
                // Collections - check elements
                if let Ok(elts) = expr.getattr("elts")
                    && let Ok(elts_list) = elts.cast::<PyList>()
                {
                    for e in elts_list.iter() {
                        self.extract_calls_from_expr(&e, caller, false, calls)?;
                    }
                }
            }
            "Dict" => {
                // Dict - check keys and values
                if let Ok(values) = expr.getattr("values")
                    && let Ok(values_list) = values.cast::<PyList>()
                {
                    for v in values_list.iter() {
                        self.extract_calls_from_expr(&v, caller, false, calls)?;
                    }
                }
            }
            "Subscript" => {
                // Subscript - check value
                if let Ok(value) = expr.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            "Attribute" => {
                // Attribute access - check value for calls
                if let Ok(value) = expr.getattr("value") {
                    self.extract_calls_from_expr(&value, caller, false, calls)?;
                }
            }
            _ => {}
        }

        Ok(())
    }

    /// Resolve callee name from a Call node's func attribute.
    ///
    /// Per Python AST docs:
    /// - Name(id) -> simple function call: func_name
    /// - Attribute(value, attr) -> method call: value.attr
    fn resolve_callee_name(&self, func: &Bound<'_, PyAny>) -> Result<(String, bool), AtlasError> {
        let func_type = self.get_node_type(func)?;

        match func_type.as_str() {
            "Name" => {
                // Simple function call: foo()
                let name = self.get_str_attr(func, "id").unwrap_or_default();
                Ok((name, false))
            }
            "Attribute" => {
                // Method call: obj.method() or module.function()
                let attr = self.get_str_attr(func, "attr").unwrap_or_default();

                // Try to get the value part (could be Name, Attribute, or Call)
                if let Ok(value) = func.getattr("value") {
                    let value_type = self.get_node_type(&value)?;
                    match value_type.as_str() {
                        "Name" => {
                            let base_name = self.get_str_attr(&value, "id").unwrap_or_default();
                            Ok((format!("{}.{}", base_name, attr), true))
                        }
                        "Attribute" => {
                            // Chained: a.b.c() - recurse
                            let (base, _) = self.resolve_callee_name(&value)?;
                            Ok((format!("{}.{}", base, attr), true))
                        }
                        _ => {
                            // Complex expression, just use the attribute
                            Ok((attr, true))
                        }
                    }
                } else {
                    Ok((attr, true))
                }
            }
            _ => {
                // Some other call pattern (e.g., (get_func())())
                Ok((String::new(), false))
            }
        }
    }

    /// Extract imports from an AST node.
    fn extract_imports_from_node(
        &self,
        node: &Bound<'_, PyAny>,
        imports: &mut Vec<ImportInfo>,
    ) -> Result<(), AtlasError> {
        let node_type = self.get_node_type(node)?;

        match node_type.as_str() {
            "Import" => {
                // import x, y as z
                self.extract_import_statement(node, imports)?;
            }
            "ImportFrom" => {
                // from x import y, z
                self.extract_import_from_statement(node, imports)?;
            }
            _ => {}
        }

        Ok(())
    }

    /// Extract from "import x" or "import x as y" statements.
    fn extract_import_statement(
        &self,
        node: &Bound<'_, PyAny>,
        imports: &mut Vec<ImportInfo>,
    ) -> Result<(), AtlasError> {
        let line_number = self.get_int_attr(node, "lineno").unwrap_or(0) as usize;

        // Get the names list
        if let Ok(names) = node.getattr("names")
            && let Ok(names_list) = names.cast::<PyList>()
        {
            for alias_node in names_list.iter() {
                // Each alias has 'name' and optional 'asname'
                let module_name = self.get_str_attr(&alias_node, "name").unwrap_or_default();
                let alias = self.get_str_attr(&alias_node, "asname").ok();

                if !module_name.is_empty() {
                    imports.push(ImportInfo {
                        module_name,
                        imported_names: Vec::new(),
                        alias,
                        line_number,
                        is_relative: false,
                        relative_level: 0,
                        is_wildcard: false,
                    });
                }
            }
        }

        Ok(())
    }

    /// Extract from "from x import y" statements.
    fn extract_import_from_statement(
        &self,
        node: &Bound<'_, PyAny>,
        imports: &mut Vec<ImportInfo>,
    ) -> Result<(), AtlasError> {
        let line_number = self.get_int_attr(node, "lineno").unwrap_or(0) as usize;

        // Get the module name (can be None for relative imports like "from . import x")
        let module_name = self.get_str_attr(node, "module").unwrap_or_default();

        // Get the relative import level (0 for absolute, 1 for ".", 2 for "..", etc.)
        let relative_level = self.get_int_attr(node, "level").unwrap_or(0) as usize;
        let is_relative = relative_level > 0;

        // Get imported names
        let mut imported_names = Vec::new();
        let mut is_wildcard = false;

        if let Ok(names) = node.getattr("names")
            && let Ok(names_list) = names.cast::<PyList>()
        {
            for alias_node in names_list.iter() {
                let name = self.get_str_attr(&alias_node, "name").unwrap_or_default();
                if name == "*" {
                    is_wildcard = true;
                } else if !name.is_empty() {
                    imported_names.push(name);
                }
            }
        }

        // For "from x import y, z" we create one ImportInfo with all names
        // For "from x import *" we mark it as wildcard
        imports.push(ImportInfo {
            module_name,
            imported_names,
            alias: None, // from imports don't have module-level alias
            line_number,
            is_relative,
            relative_level,
            is_wildcard,
        });

        Ok(())
    }

    /// Extract definitions from an AST node.
    fn extract_from_node(
        &self,
        node: &Bound<'_, PyAny>,
        definitions: &mut Vec<DefinitionInfo>,
        in_class: bool,
        router_prefixes: &HashMap<String, String>,
        dep_aliases: &HashMap<String, DependencyAliasInfo>,
        security_deps: &HashMap<String, String>,
    ) -> Result<(), AtlasError> {
        let node_type = self.get_node_type(node)?;

        match node_type.as_str() {
            "FunctionDef" | "AsyncFunctionDef" => {
                let def = self.extract_function(
                    node,
                    in_class,
                    node_type == "AsyncFunctionDef",
                    router_prefixes,
                    dep_aliases,
                    security_deps,
                )?;
                definitions.push(def);
            }
            "ClassDef" => {
                let class_def = self.extract_class(node)?;
                definitions.push(class_def);

                // Extract methods from class body
                if let Ok(body) = node.getattr("body")
                    && let Ok(body_list) = body.cast::<PyList>()
                {
                    for item in body_list.iter() {
                        self.extract_from_node(
                            &item,
                            definitions,
                            true,
                            router_prefixes,
                            dep_aliases,
                            security_deps,
                        )?;
                    }
                }
            }
            "Assign" => {
                // Check for module-level constants (SCREAMING_CASE)
                if !in_class
                    && let Some(const_def) = self.try_extract_constant(node)?
                {
                    definitions.push(const_def);
                }
            }
            _ => {}
        }

        Ok(())
    }

    /// Get the type name of an AST node.
    fn get_node_type(&self, node: &Bound<'_, PyAny>) -> Result<String, AtlasError> {
        let type_obj = node.get_type();
        let type_name = type_obj.name().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get node type: {}", e),
        })?;
        Ok(type_name.to_string())
    }

    /// Extract a function definition.
    fn extract_function(
        &self,
        node: &Bound<'_, PyAny>,
        in_class: bool,
        is_async: bool,
        router_prefixes: &HashMap<String, String>,
        dep_aliases: &HashMap<String, DependencyAliasInfo>,
        security_deps: &HashMap<String, String>,
    ) -> Result<DefinitionInfo, AtlasError> {
        let name = self.get_str_attr(node, "name")?;
        let line_start = self.get_int_attr(node, "lineno")? as usize;
        let line_end = self
            .get_int_attr(node, "end_lineno")
            .unwrap_or(line_start as i64) as usize;

        let signature = self.extract_signature(node)?;
        let docstring = self.extract_docstring(node)?;
        let (tags, route_path) = self.extract_decorator_tags_and_route(node)?;
        let response_models = self.extract_response_models_from_decorators(node)?;
        let params = self.extract_parameters(node, dep_aliases, security_deps)?;
        let has_yield = self.extract_has_yield(node)?;

        let def_type = if in_class {
            DefinitionType::Method
        } else {
            DefinitionType::Function
        };

        let roles = self.infer_roles(def_type, is_async, &tags);

        let router_prefix = tags
            .iter()
            .find_map(|t| t.strip_prefix("router_"))
            .and_then(|router_name| router_prefixes.get(router_name).cloned());

        Ok(DefinitionInfo {
            name,
            def_type,
            signature: Some(signature),
            docstring,
            line_start,
            line_end,
            is_async,
            tags,
            route_path,
            router_prefix,
            base_classes: Vec::new(),
            params,
            has_yield,
            roles,
            field_count: None,
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: None,
            request_models: Vec::new(),
            response_models,
            pydantic_fields_summary: None,
            pydantic_validators_summary: None,
        })
    }

    /// Extract a class definition.
    fn extract_class(&self, node: &Bound<'_, PyAny>) -> Result<DefinitionInfo, AtlasError> {
        let name = self.get_str_attr(node, "name")?;
        let line_start = self.get_int_attr(node, "lineno")? as usize;
        let line_end = self
            .get_int_attr(node, "end_lineno")
            .unwrap_or(line_start as i64) as usize;

        let docstring = self.extract_docstring(node)?;
        let (mut tags, _) = self.extract_decorator_tags_and_route(node)?;
        let base_classes = self.extract_base_classes(node)?;
        let field_count = self.count_class_fields(node)?;
        let validator_count = self.count_pydantic_validators(node)?;

        // Detect Pydantic models by base class
        for base in &base_classes {
            if PYDANTIC_BASES.contains(&base.as_str()) {
                tags.push("pydantic_model".to_string());
                break;
            }
        }

        let (pydantic_fields_summary, pydantic_validators_summary) = if tags
            .iter()
            .any(|t| t == "pydantic_model")
        {
            (
                self.extract_pydantic_fields_summary(node)?,
                self.extract_pydantic_validators_summary(node)?,
            )
        } else {
            (None, None)
        };

        let roles = self.infer_roles(DefinitionType::Class, false, &tags);

        Ok(DefinitionInfo {
            name,
            def_type: DefinitionType::Class,
            signature: None,
            docstring,
            line_start,
            line_end,
            is_async: false,
            tags,
            route_path: None,
            router_prefix: None,
            base_classes,
            params: Vec::new(),
            has_yield: false,
            roles,
            field_count: Some(field_count),
            nested_model_field_count: None,
            max_nested_model_depth: None,
            validator_count: Some(validator_count),
            request_models: Vec::new(),
            response_models: Vec::new(),
            pydantic_fields_summary,
            pydantic_validators_summary,
        })
    }

    fn extract_pydantic_fields_summary(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Option<String>, AtlasError> {
        let mut fields: Vec<PydanticFieldSummary> = Vec::new();

        let Ok(body) = node.getattr("body") else {
            return Ok(None);
        };
        let Ok(body_list) = body.cast::<PyList>() else {
            return Ok(None);
        };

        for item in body_list.iter() {
            let node_type = self.get_node_type(&item)?;
            if node_type != "AnnAssign" {
                continue;
            }

            let Ok(target) = item.getattr("target") else {
                continue;
            };

            let name = if let Ok(id) = self.get_str_attr(&target, "id") {
                id
            } else if let Ok(attr) = self.get_str_attr(&target, "attr") {
                attr
            } else {
                continue;
            };

            let type_expr = match item.getattr("annotation") {
                Ok(ann) if !ann.is_none() => {
                    let s = self.expr_to_type_string(&ann)?;
                    if s.is_empty() { None } else { Some(s) }
                }
                _ => None,
            };

            let has_default = match item.getattr("value") {
                Ok(v) => !v.is_none(),
                Err(_) => false,
            };

            fields.push(PydanticFieldSummary {
                name,
                type_expr,
                has_default,
            });
        }

        fields.sort_by(|a, b| a.name.cmp(&b.name));

        if fields.is_empty() {
            return Ok(None);
        }

        let s = serde_json::to_string(&fields).map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to serialize pydantic_fields_summary: {}", e),
        })?;

        Ok(Some(s))
    }

    fn extract_pydantic_validators_summary(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Option<String>, AtlasError> {
        let mut validators: Vec<PydanticValidatorSummary> = Vec::new();

        let Ok(body) = node.getattr("body") else {
            return Ok(None);
        };
        let Ok(body_list) = body.cast::<PyList>() else {
            return Ok(None);
        };

        for item in body_list.iter() {
            let item_type = self.get_node_type(&item)?;
            if item_type != "FunctionDef" && item_type != "AsyncFunctionDef" {
                continue;
            }

            let Ok(func_name) = self.get_str_attr(&item, "name") else {
                continue;
            };

            let decorators = item.getattr("decorator_list").ok();
            let Some(decorators) = decorators else {
                continue;
            };
            let Ok(dec_list) = decorators.cast::<PyList>() else {
                continue;
            };

            for dec in dec_list.iter() {
                let Some(parsed) = self.try_parse_pydantic_validator_decorator(&dec)? else {
                    continue;
                };

                let mut fields = parsed.fields;
                fields.sort();

                validators.push(PydanticValidatorSummary {
                    name: func_name.clone(),
                    kind: parsed.kind,
                    fields,
                    mode: parsed.mode,
                });
            }
        }

        validators.sort_by(|a, b| {
            a.name
                .cmp(&b.name)
                .then_with(|| a.kind.cmp(&b.kind))
                .then_with(|| a.mode.cmp(&b.mode))
        });

        if validators.is_empty() {
            return Ok(None);
        }

        let s = serde_json::to_string(&validators).map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to serialize pydantic_validators_summary: {}", e),
        })?;

        Ok(Some(s))
    }

    fn try_parse_pydantic_validator_decorator(
        &self,
        decorator: &Bound<'_, PyAny>,
    ) -> Result<Option<ParsedPydanticValidatorDecorator>, AtlasError> {
        let dec_type = self.get_node_type(decorator)?;
        match dec_type.as_str() {
            "Name" => {
                let Ok(id) = self.get_str_attr(decorator, "id") else {
                    return Ok(None);
                };
                if id == "validator" || id == "field_validator" || id == "model_validator" {
                    return Ok(Some(ParsedPydanticValidatorDecorator {
                        kind: id,
                        fields: Vec::new(),
                        mode: None,
                    }));
                }
            }
            "Attribute" => {
                let Ok(attr) = self.get_str_attr(decorator, "attr") else {
                    return Ok(None);
                };
                if attr == "validator" || attr == "field_validator" || attr == "model_validator" {
                    return Ok(Some(ParsedPydanticValidatorDecorator {
                        kind: attr,
                        fields: Vec::new(),
                        mode: None,
                    }));
                }
            }
            "Call" => {
                let Ok(func) = decorator.getattr("func") else {
                    return Ok(None);
                };
                let (callee, _) = self.resolve_callee_name(&func)?;
                let kind = callee
                    .split('.')
                    .next_back()
                    .unwrap_or_default()
                    .to_string();
                if kind != "validator" && kind != "field_validator" && kind != "model_validator" {
                    return Ok(None);
                }

                let mut fields: Vec<String> = Vec::new();
                if let Ok(args) = decorator.getattr("args")
                    && let Ok(args_list) = args.cast::<PyList>()
                {
                    for arg in args_list.iter() {
                        let arg_type = self.get_node_type(&arg)?;
                        if arg_type != "Constant" {
                            continue;
                        }
                        let Ok(value) = arg.getattr("value") else {
                            continue;
                        };
                        if let Ok(s) = value.extract::<String>() {
                            fields.push(s);
                        }
                    }
                }

                let mut mode: Option<String> = None;
                if let Ok(keywords) = decorator.getattr("keywords")
                    && let Ok(kw_list) = keywords.cast::<PyList>()
                {
                    for kw in kw_list.iter() {
                        let Ok(arg) = kw.getattr("arg") else {
                            continue;
                        };
                        if arg.is_none() {
                            continue;
                        }
                        let Ok(arg_name) = arg.extract::<String>() else {
                            continue;
                        };
                        if arg_name != "mode" {
                            continue;
                        }
                        let Ok(value) = kw.getattr("value") else {
                            continue;
                        };
                        let value_type = self.get_node_type(&value)?;
                        if value_type != "Constant" {
                            continue;
                        }
                        let Ok(inner) = value.getattr("value") else {
                            continue;
                        };
                        if let Ok(s) = inner.extract::<String>() {
                            mode = Some(s);
                            break;
                        }
                    }
                }

                return Ok(Some(ParsedPydanticValidatorDecorator { kind, fields, mode }));
            }
            _ => {}
        }

        Ok(None)
    }

    /// Collect router prefixes from APIRouter declarations at module scope.
    fn collect_router_prefixes(
        &self,
        body_list: &Bound<'_, PyList>,
    ) -> Result<HashMap<String, String>, AtlasError> {
        let mut prefixes = HashMap::new();

        // Capture prefixes from APIRouter(...) assignments.
        let len = body_list.len();
        for idx in 0..len {
            let item = body_list.get_item(idx).map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: e.to_string(),
            })?;
            let node_type = self.get_node_type(&item)?;
            if node_type != "Assign" {
                continue;
            }

            // Get targets[0].id as router name
            if let Ok(targets) = item.getattr("targets")
                && let Ok(target_list) = targets.cast::<PyList>()
                && let Ok(first_target) = target_list.get_item(0)
                && let Ok(router_name) = self.get_str_attr(&first_target, "id")
            {
                // Check value is Call to APIRouter(...)
                if let Ok(value) = item.getattr("value") {
                    let value_type = self.get_node_type(&value)?;
                    if value_type == "Call" {
                        // Verify func is APIRouter
                        let mut is_api_router = false;
                        if let Ok(func) = value.getattr("func") {
                            let func_type = self.get_node_type(&func)?;
                            if func_type == "Name"
                                && let Ok(id) = self.get_str_attr(&func, "id")
                                && id == "APIRouter"
                            {
                                is_api_router = true;
                            } else if func_type == "Attribute"
                                && let Ok(attr) = self.get_str_attr(&func, "attr")
                                && attr == "APIRouter"
                            {
                                is_api_router = true;
                            }
                        }

                        if is_api_router
                            && let Ok(keywords) = value.getattr("keywords")
                            && let Ok(kw_list) = keywords.cast::<PyList>()
                        {
                            for kw in kw_list.iter() {
                                if let Ok(arg_name) = kw.getattr("arg")
                                    && let Ok(arg_str) = arg_name.extract::<String>()
                                    && arg_str == "prefix"
                                    && let Ok(kw_value) = kw.getattr("value")
                                {
                                    let kw_type = self.get_node_type(&kw_value)?;
                                    if kw_type == "Constant"
                                        && let Ok(prefix) = kw_value
                                            .getattr("value")
                                            .and_then(|v| v.extract::<String>())
                                    {
                                        prefixes.insert(router_name.clone(), prefix);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Capture prefixes from include_router(..., prefix="...") mount points.
        for idx in 0..len {
            let item = body_list.get_item(idx).map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: e.to_string(),
            })?;
            let node_type = self.get_node_type(&item)?;
            if node_type != "Expr" {
                continue;
            }

            // Expect value to be a Call expression
            let Ok(value) = item.getattr("value") else {
                continue;
            };
            let value_type = self.get_node_type(&value)?;
            if value_type != "Call" {
                continue;
            }

            // Ensure func is an Attribute ending with include_router
            let Ok(func) = value.getattr("func") else {
                continue;
            };
            let func_type = self.get_node_type(&func)?;
            if func_type != "Attribute" {
                continue;
            }
            let Ok(attr_name) = self.get_str_attr(&func, "attr") else {
                continue;
            };
            if attr_name != "include_router" {
                continue;
            }

            // Parent router variable name (e.g., `api` in `api.include_router(...)`)
            let parent_router_name = func
                .getattr("value")
                .ok()
                .and_then(|v| self.get_str_attr(&v, "id").ok());

            // First positional arg should be the router variable name
            let mut child_router_name = None;
            if let Ok(args) = value.getattr("args")
                && let Ok(args_list) = args.cast::<PyList>()
                && let Ok(first_arg) = args_list.get_item(0)
                && let Ok(name) = self.get_str_attr(&first_arg, "id")
            {
                child_router_name = Some(name);
            }

            // Extract prefix keyword if present
            let mut include_prefix = None;
            if let Ok(keywords) = value.getattr("keywords")
                && let Ok(kw_list) = keywords.cast::<PyList>()
            {
                for kw in kw_list.iter() {
                    if let Ok(arg_name) = kw.getattr("arg")
                        && let Ok(arg_str) = arg_name.extract::<String>()
                        && arg_str == "prefix"
                        && let Ok(kw_value) = kw.getattr("value")
                    {
                        let kw_type = self.get_node_type(&kw_value)?;
                        if kw_type == "Constant"
                            && let Ok(prefix) = kw_value
                                .getattr("value")
                                .and_then(|v| v.extract::<String>())
                        {
                            include_prefix = Some(prefix);
                            break;
                        }
                    }
                }
            }

            if let (Some(child_name), Some(include_prefix)) = (child_router_name, include_prefix) {
                let parent_prefix = parent_router_name
                    .as_deref()
                    .and_then(|p| prefixes.get(p))
                    .cloned()
                    .unwrap_or_default();

                let child_prefix = prefixes.get(&child_name).cloned().unwrap_or_default();

                // Effective mounted prefix = parent_prefix + include_prefix + child_prefix
                // This enables callers to build full paths as router_prefix + route_path.
                prefixes.insert(child_name, format!("{}{}{}", parent_prefix, include_prefix, child_prefix));
            }
        }

        Ok(prefixes)
    }

    fn collect_dependency_aliases(
        &self,
        body_list: &Bound<'_, PyList>,
    ) -> Result<HashMap<String, DependencyAliasInfo>, AtlasError> {
        let mut aliases = HashMap::new();
        let len = body_list.len();

        for idx in 0..len {
            let item = body_list.get_item(idx).map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: e.to_string(),
            })?;

            let node_type = self.get_node_type(&item)?;
            if node_type != "Assign" {
                continue;
            }

            let Ok(targets) = item.getattr("targets") else {
                continue;
            };
            let Ok(target_list) = targets.cast::<PyList>() else {
                continue;
            };
            let Ok(first_target) = target_list.get_item(0) else {
                continue;
            };
            let Ok(alias_name) = self.get_str_attr(&first_target, "id") else {
                continue;
            };

            let Ok(value) = item.getattr("value") else {
                continue;
            };

            if let Some(info) = self.try_parse_annotated_dependency(&value)? {
                aliases.insert(alias_name, info);
            }
        }

        Ok(aliases)
    }

    fn collect_security_dependables(
        &self,
        body_list: &Bound<'_, PyList>,
    ) -> Result<HashMap<String, String>, AtlasError> {
        let mut security = HashMap::new();
        let len = body_list.len();

        for idx in 0..len {
            let item = body_list.get_item(idx).map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: e.to_string(),
            })?;
            let node_type = self.get_node_type(&item)?;
            if node_type != "Assign" {
                continue;
            }

            let Ok(targets) = item.getattr("targets") else {
                continue;
            };
            let Ok(target_list) = targets.cast::<PyList>() else {
                continue;
            };
            let Ok(first_target) = target_list.get_item(0) else {
                continue;
            };
            let Ok(var_name) = self.get_str_attr(&first_target, "id") else {
                continue;
            };

            let Ok(value) = item.getattr("value") else {
                continue;
            };
            let value_type = self.get_node_type(&value)?;
            if value_type != "Call" {
                continue;
            }

            let Ok(func) = value.getattr("func") else {
                continue;
            };
            let (callee, _) = self.resolve_callee_name(&func)?;
            if callee == "OAuth2PasswordBearer" || callee.ends_with(".OAuth2PasswordBearer") {
                security.insert(var_name, callee);
            }
        }

        Ok(security)
    }

    fn try_parse_annotated_dependency(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Option<DependencyAliasInfo>, AtlasError> {
        let node_type = self.get_node_type(node)?;
        if node_type != "Subscript" {
            return Ok(None);
        }

        let Ok(value) = node.getattr("value") else {
            return Ok(None);
        };

        let base_type = self.get_node_type(&value)?;
        let is_annotated = if base_type == "Name" {
            self.get_str_attr(&value, "id").ok().as_deref() == Some("Annotated")
        } else if base_type == "Attribute" {
            self.get_str_attr(&value, "attr").ok().as_deref() == Some("Annotated")
        } else {
            false
        };

        if !is_annotated {
            return Ok(None);
        }

        let Ok(slice) = node.getattr("slice") else {
            return Ok(None);
        };
        let slice_type = self.get_node_type(&slice)?;
        if slice_type != "Tuple" {
            return Ok(None);
        }

        let Ok(elts) = slice.getattr("elts") else {
            return Ok(None);
        };
        let Ok(elts_list) = elts.cast::<PyList>() else {
            return Ok(None);
        };

        // FastAPI docs show Annotated[..., Depends(callable)] or Annotated[..., Security(callable, ...)]
        for elt in elts_list.iter() {
            let elt_type = self.get_node_type(&elt)?;
            if elt_type != "Call" {
                continue;
            }
            let Some((target, is_security)) = self.extract_dep_target_from_dep_call(&elt)? else {
                continue;
            };
            return Ok(Some(DependencyAliasInfo { target, is_security }));
        }

        Ok(None)
    }

    fn extract_dep_target_from_dep_call(
        &self,
        call_node: &Bound<'_, PyAny>,
    ) -> Result<Option<(String, bool)>, AtlasError> {
        let Ok(func) = call_node.getattr("func") else {
            return Ok(None);
        };
        let (callee, _) = self.resolve_callee_name(&func)?;

        let is_dep = callee == "Depends" || callee.ends_with(".Depends");
        let is_sec = callee == "Security" || callee.ends_with(".Security");
        if !is_dep && !is_sec {
            return Ok(None);
        }

        let Ok(args) = call_node.getattr("args") else {
            return Ok(None);
        };
        let Ok(args_list) = args.cast::<PyList>() else {
            return Ok(None);
        };
        let Ok(first_arg) = args_list.get_item(0) else {
            return Ok(None);
        };

        let first_arg_type = self.get_node_type(&first_arg)?;
        let target = if first_arg_type == "Name" {
            self.get_str_attr(&first_arg, "id")?
        } else {
            self.expr_to_string(&first_arg)?
        };

        Ok(Some((target, is_sec)))
    }

    /// Extract base class names from a class definition.
    fn extract_base_classes(&self, node: &Bound<'_, PyAny>) -> Result<Vec<String>, AtlasError> {
        let mut bases = Vec::new();

        if let Ok(bases_attr) = node.getattr("bases")
            && let Ok(bases_list) = bases_attr.cast::<PyList>()
        {
            for base in bases_list.iter() {
                // Handle simple Name nodes (e.g., BaseModel)
                if let Ok(base_name) = self.get_str_attr(&base, "id") {
                    bases.push(base_name);
                }
                // Handle Attribute nodes (e.g., pydantic.BaseModel)
                else if let Ok(attr) = self.get_str_attr(&base, "attr") {
                    bases.push(attr);
                }
            }
        }

        Ok(bases)
    }

    /// Try to extract a constant definition.
    fn try_extract_constant(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Option<DefinitionInfo>, AtlasError> {
        let targets = node.getattr("targets").ok();

        if let Some(targets) = targets
            && let Ok(targets_list) = targets.cast::<PyList>()
            && let Ok(first) = targets_list.get_item(0)
            && let Ok(name) = self.get_str_attr(&first, "id")
        {
            // Check if it's SCREAMING_CASE (likely a constant)
            if name.chars().all(|c| c.is_uppercase() || c == '_') && !name.is_empty() {
                let line_start = self.get_int_attr(node, "lineno")? as usize;

                return Ok(Some(DefinitionInfo {
                    name,
                    def_type: DefinitionType::Constant,
                    signature: None,
                    docstring: None,
                    line_start,
                    line_end: line_start,
                    is_async: false,
                    tags: Vec::new(),
                    route_path: None,
                    router_prefix: None,
                    base_classes: Vec::new(),
                    params: Vec::new(),
                    has_yield: false,
                    roles: Vec::new(),
                    field_count: None,
                    nested_model_field_count: None,
                    max_nested_model_depth: None,
                    validator_count: None,
                    request_models: Vec::new(),
                    response_models: Vec::new(),
                    pydantic_fields_summary: None,
                    pydantic_validators_summary: None,
                }));
            }
        }

        Ok(None)
    }

    /// Convert an expression node to a string using its Python repr().
    fn expr_to_string(&self, expr: &Bound<'_, PyAny>) -> Result<String, AtlasError> {
        let repr_obj = expr.repr().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get repr for expression: {}", e),
        })?;

        repr_obj.extract::<String>().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to extract string from repr: {}", e),
        })
    }

    /// Extract the annotation string from an arg node, if present.
    fn extract_annotation_string(
        &self,
        arg_node: &Bound<'_, PyAny>,
    ) -> Result<Option<String>, AtlasError> {
        let annotation = arg_node.getattr("annotation").ok();
        if let Some(annotation) = annotation
            && !annotation.is_none()
        {
            let s = self.expr_to_string(&annotation)?;
            return Ok(Some(s));
        }
        Ok(None)
    }

    /// Classify FastAPI-related parameter flags based on AST nodes for
    /// annotation and default expressions.
    fn classify_param_flags_from_nodes(
        &self,
        annotation_node: Option<&Bound<'_, PyAny>>,
        default_node: Option<&Bound<'_, PyAny>>,
        dep_aliases: &HashMap<String, DependencyAliasInfo>,
        security_deps: &HashMap<String, String>,
    ) -> Result<(bool, bool, Option<String>, bool), AtlasError> {
        let mut is_dep = false;
        let mut is_bg = false;
        let mut dep_target: Option<String> = None;
        let mut is_security = false;

        // Annotation-based detection, e.g.:
        //   background_tasks: BackgroundTasks
        //   commons: Annotated[dict, Depends(common_parameters)]
        //   commons: CommonsDep (where CommonsDep = Annotated[..., Depends(...)])
        if let Some(node) = annotation_node {
            let node_type = self.get_node_type(node)?;
            if node_type == "Name" {
                if let Ok(id) = self.get_str_attr(node, "id") {
                    if id == "BackgroundTasks" {
                        is_bg = true;
                    }

                    if let Some(alias) = dep_aliases.get(&id) {
                        is_dep = true;
                        dep_target = Some(alias.target.clone());
                        is_security = alias.is_security;
                    }
                }
            } else if let Some(alias) = self.try_parse_annotated_dependency(node)? {
                is_dep = true;
                dep_target = Some(alias.target);
                is_security = alias.is_security;
            }
        }

        // Default-based detection, e.g.:
        //   db = Depends(get_db)
        //   user = Security(get_current_active_user, scopes=[...])
        if let Some(node) = default_node {
            let node_type = self.get_node_type(node)?;
            if node_type == "Call"
                && let Ok(func) = node.getattr("func")
            {
                let (callee_name, _) = self.resolve_callee_name(&func)?;

                if callee_name == "Depends" || callee_name.ends_with(".Depends") {
                    is_dep = true;
                    if dep_target.is_none()
                        && let Some((target, _)) = self.extract_dep_target_from_dep_call(node)?
                    {
                        dep_target = Some(target);
                    }
                }
                if callee_name == "Security" || callee_name.ends_with(".Security") {
                    is_dep = true;
                    is_security = true;
                    if dep_target.is_none()
                        && let Some((target, _)) = self.extract_dep_target_from_dep_call(node)?
                    {
                        dep_target = Some(target);
                    }
                }
                if callee_name == "BackgroundTasks" || callee_name.ends_with(".BackgroundTasks") {
                    is_bg = true;
                }
            }
        }

        if let Some(ref target) = dep_target
            && security_deps.contains_key(target)
        {
            is_security = true;
        }

        Ok((is_dep, is_bg, dep_target, is_security))
    }

    fn classify_body_from_nodes(
        &self,
        annotation_node: Option<&Bound<'_, PyAny>>,
        default_node: Option<&Bound<'_, PyAny>>,
    ) -> Result<(bool, Option<bool>), AtlasError> {
        let mut is_body = false;
        let mut embed: Option<bool> = None;

        if let Some(node) = default_node {
            let node_type = self.get_node_type(node)?;
            if node_type == "Call"
                && let Ok(func) = node.getattr("func")
            {
                let (callee_name, _) = self.resolve_callee_name(&func)?;
                if callee_name == "Body" || callee_name.ends_with(".Body") {
                    is_body = true;
                    embed = self.extract_embed_kwarg_from_call(node)?;
                }
            }
        }

        if !is_body
            && let Some(node) = annotation_node
            && let Some(found) = self.try_parse_annotated_body(node)?
        {
            is_body = true;
            embed = found;
        }

        Ok((is_body, embed))
    }

    fn try_parse_annotated_body(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Option<Option<bool>>, AtlasError> {
        let node_type = self.get_node_type(node)?;
        if node_type != "Subscript" {
            return Ok(None);
        }

        let Ok(value) = node.getattr("value") else {
            return Ok(None);
        };

        let base_type = self.get_node_type(&value)?;
        let is_annotated = if base_type == "Name" {
            self.get_str_attr(&value, "id").ok().as_deref() == Some("Annotated")
        } else if base_type == "Attribute" {
            self.get_str_attr(&value, "attr").ok().as_deref() == Some("Annotated")
        } else {
            false
        };

        if !is_annotated {
            return Ok(None);
        }

        let Ok(slice) = node.getattr("slice") else {
            return Ok(None);
        };
        let slice_type = self.get_node_type(&slice)?;
        if slice_type != "Tuple" {
            return Ok(None);
        }

        let Ok(elts) = slice.getattr("elts") else {
            return Ok(None);
        };
        let Ok(elts_list) = elts.cast::<PyList>() else {
            return Ok(None);
        };

        for elt in elts_list.iter() {
            let elt_type = self.get_node_type(&elt)?;
            if elt_type != "Call" {
                continue;
            }

            let Ok(func) = elt.getattr("func") else {
                continue;
            };
            let (callee, _) = self.resolve_callee_name(&func)?;
            if callee == "Body" || callee.ends_with(".Body") {
                let embed = self.extract_embed_kwarg_from_call(&elt)?;
                return Ok(Some(embed));
            }
        }

        Ok(None)
    }

    fn extract_embed_kwarg_from_call(
        &self,
        call_node: &Bound<'_, PyAny>,
    ) -> Result<Option<bool>, AtlasError> {
        let Ok(keywords) = call_node.getattr("keywords") else {
            return Ok(None);
        };
        let Ok(kw_list) = keywords.cast::<PyList>() else {
            return Ok(None);
        };

        for kw in kw_list.iter() {
            let Ok(arg) = kw.getattr("arg") else {
                continue;
            };
            if arg.is_none() {
                continue;
            }
            let Ok(arg_name) = arg.extract::<String>() else {
                continue;
            };
            if arg_name != "embed" {
                continue;
            }
            let Ok(value) = kw.getattr("value") else {
                continue;
            };
            let value_type = self.get_node_type(&value)?;
            if value_type != "Constant" {
                continue;
            }
            let Ok(inner) = value.getattr("value") else {
                continue;
            };
            if let Ok(b) = inner.extract::<bool>() {
                return Ok(Some(b));
            }
        }

        Ok(None)
    }

    fn extract_response_models_from_decorators(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<Vec<String>, AtlasError> {
        let mut models: Vec<String> = Vec::new();
        let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();

        let decorators = node.getattr("decorator_list").ok();
        let Some(decorators) = decorators else {
            return Ok(models);
        };
        let Ok(dec_list) = decorators.cast::<PyList>() else {
            return Ok(models);
        };

        for dec in dec_list.iter() {
            let dec_type = self.get_node_type(&dec)?;
            if dec_type != "Call" {
                continue;
            }

            let Ok(func) = dec.getattr("func") else {
                continue;
            };
            let func_type = self.get_node_type(&func)?;
            if func_type != "Attribute" {
                continue;
            }

            let Ok(attr) = self.get_str_attr(&func, "attr") else {
                continue;
            };
            let attr_lower = attr.to_lowercase();
            if !HTTP_METHODS.contains(&attr_lower.as_str()) {
                continue;
            }

            let Ok(keywords) = dec.getattr("keywords") else {
                continue;
            };
            let Ok(kw_list) = keywords.cast::<PyList>() else {
                continue;
            };

            for kw in kw_list.iter() {
                let Ok(arg) = kw.getattr("arg") else {
                    continue;
                };
                if arg.is_none() {
                    continue;
                }
                let Ok(arg_name) = arg.extract::<String>() else {
                    continue;
                };
                if arg_name != "response_model" {
                    continue;
                }
                let Ok(value) = kw.getattr("value") else {
                    continue;
                };
                if value.is_none() {
                    continue;
                }
                let s = self.expr_to_type_string(&value)?;
                if !s.is_empty() && seen.insert(s.clone()) {
                    models.push(s);
                }
            }
        }

        Ok(models)
    }

    fn expr_to_type_string(&self, expr: &Bound<'_, PyAny>) -> Result<String, AtlasError> {
        let node_type = self.get_node_type(expr)?;
        match node_type.as_str() {
            "Name" => Ok(self.get_str_attr(expr, "id").unwrap_or_default()),
            "Attribute" => {
                let attr = self.get_str_attr(expr, "attr").unwrap_or_default();
                if let Ok(value) = expr.getattr("value") {
                    let base = self.expr_to_type_string(&value)?;
                    if base.is_empty() {
                        Ok(attr)
                    } else {
                        Ok(format!("{}.{}", base, attr))
                    }
                } else {
                    Ok(attr)
                }
            }
            "Subscript" => {
                let value = expr.getattr("value").map_err(|e| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                })?;
                let slice = expr.getattr("slice").map_err(|e| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                })?;
                let base = self.expr_to_type_string(&value)?;
                let slice_type = self.get_node_type(&slice)?;
                if slice_type == "Tuple" {
                    let elts = slice.getattr("elts").map_err(|e| AtlasError::Parse {
                        path: PathBuf::new(),
                        message: e.to_string(),
                    })?;
                    let elts_list = elts.cast::<PyList>().map_err(|e| AtlasError::Parse {
                        path: PathBuf::new(),
                        message: e.to_string(),
                    })?;
                    let mut parts: Vec<String> = Vec::new();
                    for elt in elts_list.iter() {
                        parts.push(self.expr_to_type_string(&elt)?);
                    }
                    Ok(format!("{}[{}]", base, parts.join(", ")))
                } else {
                    let inner = self.expr_to_type_string(&slice)?;
                    Ok(format!("{}[{}]", base, inner))
                }
            }
            "BinOp" => {
                let left = expr.getattr("left").map_err(|e| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                })?;
                let right = expr.getattr("right").map_err(|e| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                })?;
                let l = self.expr_to_type_string(&left)?;
                let r = self.expr_to_type_string(&right)?;
                Ok(format!("{} | {}", l, r))
            }
            "Constant" => {
                if let Ok(value) = expr.getattr("value")
                    && let Ok(s) = value.extract::<String>()
                {
                    return Ok(s);
                }
                Ok(String::new())
            }
            _ => Ok(String::new()),
        }
    }

    fn collect_type_names_from_expr(
        &self,
        expr: &Bound<'_, PyAny>,
        out: &mut Vec<String>,
    ) -> Result<(), AtlasError> {
        let node_type = self.get_node_type(expr)?;
        match node_type.as_str() {
            "Name" => {
                if let Ok(id) = self.get_str_attr(expr, "id") {
                    out.push(id);
                }
            }
            "Attribute" => {
                if let Ok(attr) = self.get_str_attr(expr, "attr") {
                    out.push(attr);
                }
                if let Ok(value) = expr.getattr("value")
                    && !value.is_none()
                {
                    self.collect_type_names_from_expr(&value, out)?;
                }
            }
            "Subscript" => {
                if let Ok(value) = expr.getattr("value")
                    && !value.is_none()
                {
                    self.collect_type_names_from_expr(&value, out)?;
                }
                if let Ok(slice) = expr.getattr("slice")
                    && !slice.is_none()
                {
                    self.collect_type_names_from_expr(&slice, out)?;
                }
            }
            "Tuple" | "List" => {
                if let Ok(elts) = expr.getattr("elts")
                    && let Ok(elts_list) = elts.cast::<PyList>()
                {
                    for elt in elts_list.iter() {
                        self.collect_type_names_from_expr(&elt, out)?;
                    }
                }
            }
            "BinOp" => {
                if let Ok(left) = expr.getattr("left")
                    && !left.is_none()
                {
                    self.collect_type_names_from_expr(&left, out)?;
                }
                if let Ok(right) = expr.getattr("right")
                    && !right.is_none()
                {
                    self.collect_type_names_from_expr(&right, out)?;
                }
            }
            _ => {}
        }
        Ok(())
    }

    /// Extract function parameters from a FunctionDef/AsyncFunctionDef node.
    fn extract_parameters(
        &self,
        node: &Bound<'_, PyAny>,
        dep_aliases: &HashMap<String, DependencyAliasInfo>,
        security_deps: &HashMap<String, String>,
    ) -> Result<Vec<ParameterInfo>, AtlasError> {
        let args_obj = node.getattr("args").map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get function args: {}", e),
        })?;

        let mut params = Vec::new();

        // Collect positional-only and regular positional args
        let mut positional: Vec<Bound<'_, PyAny>> = Vec::new();

        if let Ok(posonly) = args_obj.getattr("posonlyargs")
            && let Ok(list) = posonly.cast::<PyList>()
        {
            for item in list.iter() {
                positional.push(item);
            }
        }

        if let Ok(args_list) = args_obj.getattr("args")
            && let Ok(list) = args_list.cast::<PyList>()
        {
            for item in list.iter() {
                positional.push(item);
            }
        }

        // Defaults align to the last N positional parameters
        let mut positional_defaults: Vec<Option<Bound<'_, PyAny>>> = vec![None; positional.len()];
        if let Ok(defaults_any) = args_obj.getattr("defaults")
            && let Ok(defaults) = defaults_any.cast::<PyList>()
        {
            let total = positional.len();
            let d = defaults.len();
            if total >= d {
                for (i, default) in defaults.iter().enumerate() {
                    let idx = total - d + i;
                    if let Some(slot) = positional_defaults.get_mut(idx) {
                        *slot = Some(default);
                    }
                }
            }
        }

        // Keyword-only args and their defaults
        let mut kwonly_args: Vec<Bound<'_, PyAny>> = Vec::new();
        if let Ok(kwonly_any) = args_obj.getattr("kwonlyargs")
            && let Ok(list) = kwonly_any.cast::<PyList>()
        {
            for item in list.iter() {
                kwonly_args.push(item);
            }
        }

        let mut kwonly_defaults: Vec<Option<Bound<'_, PyAny>>> = Vec::new();
        if let Ok(kw_defaults_any) = args_obj.getattr("kw_defaults")
            && let Ok(list) = kw_defaults_any.cast::<PyList>()
        {
            for item in list.iter() {
                if item.is_none() {
                    kwonly_defaults.push(None);
                } else {
                    kwonly_defaults.push(Some(item));
                }
            }
        }

        // Positional parameters
        for (idx, arg_node) in positional.iter().enumerate() {
            let name = self.get_str_attr(arg_node, "arg").unwrap_or_default();

            let annotation_expr = arg_node.getattr("annotation").ok();
            let annotation = self.extract_annotation_string(arg_node)?;

            let default_expr_node = positional_defaults.get(idx).and_then(|opt| opt.as_ref());
            let default_expr = default_expr_node
                .map(|expr| self.expr_to_string(expr))
                .transpose()?;

            let (is_dep, is_bg, dep_target, is_security) = self.classify_param_flags_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                default_expr_node,
                dep_aliases,
                security_deps,
            )?;

            let (is_body, body_embed) = self.classify_body_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                default_expr_node,
            )?;

            let mut type_names: Vec<String> = Vec::new();
            if let Some(node) = annotation_expr.as_ref().filter(|n| !n.is_none()) {
                self.collect_type_names_from_expr(node, &mut type_names)?;
            }

            params.push(ParameterInfo {
                name,
                annotation,
                default_expr,
                is_vararg: false,
                is_kwonly: false,
                is_varkw: false,
                is_fastapi_depends: is_dep,
                dependency_target: dep_target,
                is_security_dependency: is_security,
                is_background_tasks: is_bg,
                is_fastapi_body: is_body,
                fastapi_body_embed: body_embed,
                type_names,
            });
        }

        // *args
        if let Ok(vararg) = args_obj.getattr("vararg")
            && !vararg.is_none()
        {
            let name = self.get_str_attr(&vararg, "arg").unwrap_or_default();
            let annotation_expr = vararg.getattr("annotation").ok();
            let annotation = self.extract_annotation_string(&vararg)?;
            let (is_dep, is_bg, dep_target, is_security) = self.classify_param_flags_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                None,
                dep_aliases,
                security_deps,
            )?;

            let (is_body, body_embed) =
                self.classify_body_from_nodes(annotation_expr.as_ref().filter(|n| !n.is_none()), None)?;

            let mut type_names: Vec<String> = Vec::new();
            if let Some(node) = annotation_expr.as_ref().filter(|n| !n.is_none()) {
                self.collect_type_names_from_expr(node, &mut type_names)?;
            }

            params.push(ParameterInfo {
                name,
                annotation,
                default_expr: None,
                is_vararg: true,
                is_kwonly: false,
                is_varkw: false,
                is_fastapi_depends: is_dep,
                dependency_target: dep_target,
                is_security_dependency: is_security,
                is_background_tasks: is_bg,
                is_fastapi_body: is_body,
                fastapi_body_embed: body_embed,
                type_names,
            });
        }

        // Keyword-only parameters
        for (idx, arg_node) in kwonly_args.iter().enumerate() {
            let name = self.get_str_attr(arg_node, "arg").unwrap_or_default();
            let annotation_expr = arg_node.getattr("annotation").ok();
            let annotation = self.extract_annotation_string(arg_node)?;
            let default_expr_node = kwonly_defaults.get(idx).and_then(|opt| opt.as_ref());
            let default_expr = default_expr_node
                .map(|expr| self.expr_to_string(expr))
                .transpose()?;
            let (is_dep, is_bg, dep_target, is_security) = self.classify_param_flags_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                default_expr_node,
                dep_aliases,
                security_deps,
            )?;

            let (is_body, body_embed) = self.classify_body_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                default_expr_node,
            )?;

            let mut type_names: Vec<String> = Vec::new();
            if let Some(node) = annotation_expr.as_ref().filter(|n| !n.is_none()) {
                self.collect_type_names_from_expr(node, &mut type_names)?;
            }

            params.push(ParameterInfo {
                name,
                annotation,
                default_expr,
                is_vararg: false,
                is_kwonly: true,
                is_varkw: false,
                is_fastapi_depends: is_dep,
                dependency_target: dep_target,
                is_security_dependency: is_security,
                is_background_tasks: is_bg,
                is_fastapi_body: is_body,
                fastapi_body_embed: body_embed,
                type_names,
            });
        }

        // **kwargs
        if let Ok(kwarg) = args_obj.getattr("kwarg")
            && !kwarg.is_none()
        {
            let name = self.get_str_attr(&kwarg, "arg").unwrap_or_default();
            let annotation_expr = kwarg.getattr("annotation").ok();
            let annotation = self.extract_annotation_string(&kwarg)?;
            let (is_dep, is_bg, dep_target, is_security) = self.classify_param_flags_from_nodes(
                annotation_expr.as_ref().filter(|n| !n.is_none()),
                None,
                dep_aliases,
                security_deps,
            )?;

            let (is_body, body_embed) =
                self.classify_body_from_nodes(annotation_expr.as_ref().filter(|n| !n.is_none()), None)?;

            let mut type_names: Vec<String> = Vec::new();
            if let Some(node) = annotation_expr.as_ref().filter(|n| !n.is_none()) {
                self.collect_type_names_from_expr(node, &mut type_names)?;
            }

            params.push(ParameterInfo {
                name,
                annotation,
                default_expr: None,
                is_vararg: false,
                is_kwonly: false,
                is_varkw: true,
                is_fastapi_depends: is_dep,
                dependency_target: dep_target,
                is_security_dependency: is_security,
                is_background_tasks: is_bg,
                is_fastapi_body: is_body,
                fastapi_body_embed: body_embed,
                type_names,
            });
        }

        Ok(params)
    }

    /// Detect whether a function contains any yield / yield from expressions.
    fn extract_has_yield(&self, node: &Bound<'_, PyAny>) -> Result<bool, AtlasError> {
        if let Ok(body) = node.getattr("body")
            && let Ok(body_list) = body.cast::<PyList>()
        {
            for stmt in body_list.iter() {
                if self.node_has_yield_recursive(&stmt)? {
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }

    fn node_has_yield_recursive(&self, node: &Bound<'_, PyAny>) -> Result<bool, AtlasError> {
        let node_type = self.get_node_type(node)?;
        if node_type == "Yield" || node_type == "YieldFrom" {
            return Ok(true);
        }

        // Do not treat nested function/class definitions as part of the outer generator
        if node_type == "FunctionDef" || node_type == "AsyncFunctionDef" || node_type == "ClassDef"
        {
            return Ok(false);
        }

        // Recursively inspect common child attributes
        for attr in &[
            "body",
            "orelse",
            "finalbody",
            "value",
            "test",
            "iter",
            "target",
        ] {
            if let Ok(child) = node.getattr(*attr) {
                if let Ok(list) = child.cast::<PyList>() {
                    for item in list.iter() {
                        if self.node_has_yield_recursive(&item)? {
                            return Ok(true);
                        }
                    }
                } else if !child.is_none() && self.node_has_yield_recursive(&child)? {
                    return Ok(true);
                }
            }
        }

        Ok(false)
    }

    /// Count simple annotated fields on a class definition (AnnAssign nodes).
    fn count_class_fields(&self, node: &Bound<'_, PyAny>) -> Result<usize, AtlasError> {
        let mut count = 0;
        if let Ok(body) = node.getattr("body")
            && let Ok(body_list) = body.cast::<PyList>()
        {
            for item in body_list.iter() {
                let node_type = self.get_node_type(&item)?;
                if node_type == "AnnAssign" {
                    count += 1;
                }
            }
        }
        Ok(count)
    }

    /// Count methods decorated as Pydantic validators on a class definition.
    fn count_pydantic_validators(&self, node: &Bound<'_, PyAny>) -> Result<usize, AtlasError> {
        let mut count = 0;

        if let Ok(body) = node.getattr("body")
            && let Ok(body_list) = body.cast::<PyList>()
        {
            for item in body_list.iter() {
                let item_type = self.get_node_type(&item)?;
                if (item_type == "FunctionDef" || item_type == "AsyncFunctionDef")
                    && self.node_has_pydantic_validator_decorator(&item)?
                {
                    count += 1;
                }
            }
        }

        Ok(count)
    }

    /// Check if a function node has any @validator or @field_validator decorator.
    fn node_has_pydantic_validator_decorator(
        &self,
        func_node: &Bound<'_, PyAny>,
    ) -> Result<bool, AtlasError> {
        let decorators = func_node.getattr("decorator_list").ok();
        if let Some(decorators) = decorators
            && let Ok(dec_list) = decorators.cast::<PyList>()
        {
            for dec in dec_list.iter() {
                if self.decorator_is_pydantic_validator(&dec)? {
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }

    /// Determine whether a decorator node represents a Pydantic validator.
    fn decorator_is_pydantic_validator(
        &self,
        decorator: &Bound<'_, PyAny>,
    ) -> Result<bool, AtlasError> {
        let dec_type = self.get_node_type(decorator)?;

        match dec_type.as_str() {
            "Name" => {
                if let Ok(id) = self.get_str_attr(decorator, "id")
                    && (id == "validator" || id == "field_validator" || id == "model_validator")
                {
                    return Ok(true);
                }
            }
            "Attribute" => {
                if let Ok(attr) = self.get_str_attr(decorator, "attr")
                    && (attr == "validator" || attr == "field_validator" || attr == "model_validator")
                {
                    return Ok(true);
                }
            }
            "Call" => {
                // Handle @validator(...) and @pydantic.validator(...)
                if let Ok(func) = decorator.getattr("func") {
                    return self.decorator_is_pydantic_validator(&func);
                }
            }
            _ => {}
        }

        Ok(false)
    }

    /// Infer FastAPI roles for a definition from its tags.
    fn infer_roles(
        &self,
        def_type: DefinitionType,
        _is_async: bool,
        tags: &[String],
    ) -> Vec<FastapiRole> {
        let mut roles = Vec::new();

        if tags.iter().any(|t| t == "fastapi_route") {
            roles.push(FastapiRole::Endpoint);
        }

        if tags.iter().any(|t| t == "fastapi_middleware") {
            roles.push(FastapiRole::Middleware);
        }

        if tags.iter().any(|t| t == "fastapi_lifespan_startup") {
            roles.push(FastapiRole::LifespanStartup);
        }

        if tags.iter().any(|t| t == "fastapi_lifespan_shutdown") {
            roles.push(FastapiRole::LifespanShutdown);
        }

        // Other roles (dependency, lifespan, middleware, background tasks) will
        // be inferred in future iterations once we add the corresponding tags.

        // Silence unused parameter warning for now
        let _ = def_type;

        roles
    }

    /// Extract function signature.
    fn extract_signature(&self, node: &Bound<'_, PyAny>) -> Result<String, AtlasError> {
        let name = self.get_str_attr(node, "name")?;
        let args = node.getattr("args").map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get function args: {}", e),
        })?;

        // Build parameter list
        let mut params = Vec::new();

        if let Ok(args_list) = args.getattr("args")
            && let Ok(args_iter) = args_list.cast::<PyList>()
        {
            for arg in args_iter.iter() {
                if let Ok(arg_name) = self.get_str_attr(&arg, "arg") {
                    params.push(arg_name);
                }
            }
        }

        Ok(format!("{}({})", name, params.join(", ")))
    }

    /// Extract docstring from a function or class.
    fn extract_docstring(&self, node: &Bound<'_, PyAny>) -> Result<Option<String>, AtlasError> {
        let body = node.getattr("body").ok();

        if let Some(body) = body
            && let Ok(body_list) = body.cast::<PyList>()
            && let Ok(first) = body_list.get_item(0)
        {
            let node_type = self.get_node_type(&first)?;
            if node_type == "Expr"
                && let Ok(value) = first.getattr("value")
            {
                let value_type = self.get_node_type(&value)?;
                if value_type == "Constant"
                    && let Ok(s) = value.getattr("value")
                    && let Ok(docstring) = s.extract::<String>()
                {
                    return Ok(Some(docstring.trim().to_string()));
                }
            }
        }

        Ok(None)
    }

    /// Extract tags and route path from decorators.
    ///
    /// Returns (tags, route_path) where route_path is Some if this is an HTTP endpoint.
    fn extract_decorator_tags_and_route(
        &self,
        node: &Bound<'_, PyAny>,
    ) -> Result<(Vec<String>, Option<String>), AtlasError> {
        let mut tags = Vec::new();
        let mut route_path = None;

        let decorators = node.getattr("decorator_list").ok();

        if let Some(decorators) = decorators
            && let Ok(dec_list) = decorators.cast::<PyList>()
        {
            for dec in dec_list.iter() {
                let (dec_tags, dec_route) = self.classify_decorator_full(&dec)?;
                tags.extend(dec_tags);
                if dec_route.is_some() {
                    route_path = dec_route;
                }
            }
        }

        Ok((tags, route_path))
    }

    /// Classify a decorator and return tags and optional route path.
    ///
    /// This method handles the full range of FastAPI patterns:
    /// - `@app.get("/path")` - Direct app routes
    /// - `@router.get("/path")` - APIRouter routes
    /// - `@api.post("/path")` - Any router instance name
    fn classify_decorator_full(
        &self,
        decorator: &Bound<'_, PyAny>,
    ) -> Result<(Vec<String>, Option<String>), AtlasError> {
        let dec_type = self.get_node_type(decorator)?;

        match dec_type.as_str() {
            "Call" => {
                // This is a decorator with arguments, e.g., @router.get("/payments")
                let func = decorator.getattr("func").ok();
                let args = decorator.getattr("args").ok();

                // Extract route path from first argument if it's a string
                let mut route_path = None;
                if let Some(args) = &args
                    && let Ok(args_list) = args.cast::<PyList>()
                    && let Ok(first_arg) = args_list.get_item(0)
                {
                    // Try to extract string constant
                    let arg_type = self.get_node_type(&first_arg)?;
                    if arg_type == "Constant"
                        && let Ok(value) = first_arg.getattr("value")
                        && let Ok(path) = value.extract::<String>()
                    {
                        route_path = Some(path);
                    }
                }

                // Detect middleware and lifespan decorators with arguments
                let mut tags = Vec::new();
                if let Some(func_obj) = &func {
                    let func_type = self.get_node_type(func_obj)?;
                    if func_type == "Attribute"
                        && let Ok(attr_name) = self.get_str_attr(func_obj, "attr")
                    {
                        // Middleware: @app.middleware("http")
                        if attr_name == "middleware" {
                            tags.push("fastapi_middleware".to_string());

                            // Tag router/app name if available
                            if let Ok(value) = func_obj.getattr("value")
                                && let Ok(router_name) = self.get_str_attr(&value, "id")
                            {
                                tags.push(format!("router_{}", router_name));
                            }
                        }

                        // Lifespan: @app.on_event("startup"/"shutdown")
                        if attr_name == "on_event" {
                            // Extract event name from first arg
                            if let Some(args) = &args
                                && let Ok(args_list) = args.cast::<PyList>()
                                && let Ok(first_arg) = args_list.get_item(0)
                            {
                                let arg_type = self.get_node_type(&first_arg)?;
                                if arg_type == "Constant"
                                    && let Ok(value) = first_arg.getattr("value")
                                    && let Ok(event_name) = value.extract::<String>()
                                {
                                    match event_name.as_str() {
                                        "startup" => {
                                            tags.push("fastapi_lifespan_startup".to_string());
                                        }
                                        "shutdown" => {
                                            tags.push("fastapi_lifespan_shutdown".to_string());
                                        }
                                        _ => {}
                                    }
                                }
                            }

                            // Tag router/app name if available
                            if let Ok(value) = func_obj.getattr("value")
                                && let Ok(router_name) = self.get_str_attr(&value, "id")
                            {
                                tags.push(format!("router_{}", router_name));
                            }
                        }
                    }
                }

                // Recursively classify the function part
                if let Some(func) = func {
                    let (mut child_tags, _) = self.classify_decorator_full(&func)?;
                    child_tags.extend(tags);
                    return Ok((child_tags, route_path));
                }
            }
            "Attribute" => {
                // e.g., app.get, router.post, api_router.delete
                if let Ok(attr) = self.get_str_attr(decorator, "attr") {
                    let attr_lower = attr.to_lowercase();
                    if HTTP_METHODS.contains(&attr_lower.as_str()) {
                        let mut tags =
                            vec![format!("http_{}", attr_lower), "fastapi_route".to_string()];

                        // Also try to get the router name for context
                        if let Ok(value) = decorator.getattr("value")
                            && let Ok(router_name) = self.get_str_attr(&value, "id")
                        {
                            tags.push(format!("router_{}", router_name));
                        }

                        return Ok((tags, None));
                    }

                    // Handle @router.include_router pattern
                    if attr == "include_router" {
                        return Ok((vec!["router_mount".to_string()], None));
                    }
                }
            }
            "Name" => {
                // e.g., @Contract, @dataclass
                if let Ok(id) = self.get_str_attr(decorator, "id") {
                    let tag = match id.as_str() {
                        "Contract" => Some("contract".to_string()),
                        "dataclass" => Some("dataclass".to_string()),
                        "property" => Some("property".to_string()),
                        "staticmethod" => Some("staticmethod".to_string()),
                        "classmethod" => Some("classmethod".to_string()),
                        "abstractmethod" => Some("abstractmethod".to_string()),
                        "override" => Some("override".to_string()),
                        "deprecated" => Some("deprecated".to_string()),
                        _ => None,
                    };

                    if let Some(t) = tag {
                        return Ok((vec![t], None));
                    }
                }
            }
            _ => {}
        }

        Ok((Vec::new(), None))
    }

    /// Get a string attribute from a node.
    fn get_str_attr(&self, node: &Bound<'_, PyAny>, attr: &str) -> Result<String, AtlasError> {
        let value = node.getattr(attr).map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get attribute '{}': {}", attr, e),
        })?;
        value.extract::<String>().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to extract string from '{}': {}", attr, e),
        })
    }

    /// Get an integer attribute from a node.
    fn get_int_attr(&self, node: &Bound<'_, PyAny>, attr: &str) -> Result<i64, AtlasError> {
        let value = node.getattr(attr).map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to get attribute '{}': {}", attr, e),
        })?;
        value.extract::<i64>().map_err(|e| AtlasError::Parse {
            path: PathBuf::new(),
            message: format!("Failed to extract int from '{}': {}", attr, e),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_definition_type_display() {
        assert_eq!(format!("{:?}", DefinitionType::Function), "Function");
        assert_eq!(format!("{:?}", DefinitionType::Class), "Class");
    }

    #[test]
    fn test_extract_fastapi_response_model_and_body_metadata() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Annotated

router = APIRouter()

class ItemIn(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str

@router.post("/items", response_model=ItemOut)
async def create_item(item: ItemIn = Body(embed=True)):
    return {"id": 1, "name": item.name}

@router.post("/items2", response_model=list[ItemOut])
async def create_items(items: Annotated[list[ItemIn], Body(embed=False)]):
    return []
"#;

            let ast = py
                .import("ast")
                .and_then(|ast| ast.call_method1("parse", (code,)))
                .map_err(|e| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(ast)?;

            let create_item_def = defs.iter().find(|d| d.name == "create_item").ok_or_else(|| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "create_item not found".to_string(),
                }
            })?;

            assert_eq!(create_item_def.response_models, vec!["ItemOut".to_string()]);
            assert_eq!(create_item_def.request_models, vec!["ItemIn".to_string()]);

            let item_param = create_item_def.params.iter().find(|p| p.name == "item").ok_or_else(
                || AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "item param not found".to_string(),
                },
            )?;
            assert!(item_param.is_fastapi_body);
            assert_eq!(item_param.fastapi_body_embed, Some(true));

            let create_items_def = defs.iter().find(|d| d.name == "create_items").ok_or_else(|| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "create_items not found".to_string(),
                }
            })?;

            assert_eq!(
                create_items_def.response_models,
                vec!["list[ItemOut]".to_string()]
            );
            assert_eq!(create_items_def.request_models, vec!["ItemIn".to_string()]);

            let items_param = create_items_def
                .params
                .iter()
                .find(|p| p.name == "items")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "items param not found".to_string(),
                })?;
            assert!(items_param.is_fastapi_body);
            assert_eq!(items_param.fastapi_body_embed, Some(false));

            Ok(())
        })
    }

    #[test]
    fn test_extract_parameters_and_fastapi_metadata() -> Result<(), AtlasError> {
        // Use real Python AST parsing via PyO3 to ensure extractor works end-to-end.
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Optional

router = APIRouter()

@router.get("/items/{item_id}")
async def read_item(
    item_id: int,
    background_tasks: BackgroundTasks,
    q: Optional[str] = None,
    db = Depends(get_db),
):
    return {"id": item_id}
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let endpoint = defs.into_iter().find(|d| d.name == "read_item").ok_or_else(|| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "endpoint not found".to_string(),
                }
            })?;

            // Ensure basic FastAPI tagging and route extraction
            assert!(endpoint.tags.iter().any(|t| t == "fastapi_route"));
            assert!(endpoint.tags.iter().any(|t| t == "http_get"));
            assert_eq!(endpoint.route_path.as_deref(), Some("/items/{item_id}"));
            assert!(endpoint.roles.contains(&FastapiRole::Endpoint));

            // Verify parameter metadata and FastAPI-specific flags
            assert_eq!(endpoint.params.len(), 4);

            let db_param = endpoint.params.iter().find(|p| p.name == "db").ok_or_else(|| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "db param not found".to_string(),
                }
            })?;
            assert!(db_param.is_fastapi_depends);

            let bg_param = endpoint
                .params
                .iter()
                .find(|p| p.name == "background_tasks")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "background_tasks param not found".to_string(),
                })?;
            assert!(bg_param.is_background_tasks);

            Ok(())
        })
    }

    #[test]
    fn test_include_router_prefix_propagates_to_child_router() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import APIRouter

child = APIRouter(prefix="/child")
api = APIRouter(prefix="/api/v1")
api.include_router(child, prefix="/nested")

@child.get("/orders/{order_id}")
async def get_order(order_id: int):
    return {"id": order_id}
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let endpoint = defs.into_iter().find(|d| d.name == "get_order").ok_or_else(|| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "endpoint not found".to_string(),
                }
            })?;

            // Route path remains the decorator path; router prefix comes from include_router
            assert_eq!(endpoint.route_path.as_deref(), Some("/orders/{order_id}"));
            assert_eq!(endpoint.router_prefix.as_deref(), Some("/api/v1/nested/child"));
            assert!(endpoint.tags.iter().any(|t| t == "http_get"));
            assert!(endpoint.tags.iter().any(|t| t == "fastapi_route"));
            Ok(())
        })
    }

    #[test]
    fn test_extract_router_prefix_from_apirouter() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import APIRouter

api = APIRouter(prefix="/api/v1")

@api.get("/orders/{order_id}")
async def get_order(order_id: int):
    return {"id": order_id}
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let endpoint = defs
                .into_iter()
                .find(|d| d.name == "get_order")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "endpoint not found".to_string(),
                })?;

            assert_eq!(endpoint.route_path.as_deref(), Some("/orders/{order_id}"));
            assert_eq!(endpoint.router_prefix.as_deref(), Some("/api/v1"));
            assert!(endpoint.tags.iter().any(|t| t == "http_get"));
            assert!(endpoint.tags.iter().any(|t| t == "fastapi_route"));
            Ok(())
        })
    }

    #[test]
    fn test_extract_has_yield_generator_and_nested_function() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
def gen():
    yield 1
    for i in range(3):
        yield i

def outer():
    def inner():
        yield 42
    return inner
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let gen_def = defs.iter().find(|d| d.name == "gen").ok_or_else(|| AtlasError::Parse {
                path: PathBuf::new(),
                message: "gen not found".to_string(),
            })?;
            assert!(gen_def.has_yield);

            let outer_def = defs
                .iter()
                .find(|d| d.name == "outer")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "outer not found".to_string(),
                })?;
            // Yield only appears in nested inner(), not in outer() itself
            assert!(!outer_def.has_yield);

            Ok(())
        })
    }

    #[test]
    fn test_pydantic_model_field_and_validator_counts() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from pydantic import BaseModel, validator

class User(BaseModel):
    id: int
    name: str
    age: int

    @validator("name")
    def name_not_empty(cls, v):
        return v
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let user_def = defs.into_iter().find(|d| d.name == "User").ok_or_else(|| AtlasError::Parse {
                path: PathBuf::new(),
                message: "User class not found".to_string(),
            })?;

            assert!(user_def.tags.iter().any(|t| t == "pydantic_model"));
            assert_eq!(user_def.field_count, Some(3));
            assert_eq!(user_def.validator_count, Some(1));

            let fields_summary = user_def
                .pydantic_fields_summary
                .as_deref()
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "pydantic_fields_summary missing".to_string(),
                })?;
            let validators_summary = user_def
                .pydantic_validators_summary
                .as_deref()
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "pydantic_validators_summary missing".to_string(),
                })?;

            let fields_json: serde_json::Value = serde_json::from_str(fields_summary).map_err(|e| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                }
            })?;
            let validators_json: serde_json::Value = serde_json::from_str(validators_summary).map_err(|e| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                }
            })?;

            assert_eq!(
                fields_json,
                serde_json::json!([
                    {"name": "age", "type_expr": "int", "has_default": false},
                    {"name": "id", "type_expr": "int", "has_default": false},
                    {"name": "name", "type_expr": "str", "has_default": false}
                ])
            );
            assert_eq!(
                validators_json,
                serde_json::json!([
                    {"name": "name_not_empty", "kind": "validator", "fields": ["name"], "mode": null}
                ])
            );

            Ok(())
        })
    }

    #[test]
    fn test_pydantic_model_validator_summaries_include_model_validator() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from pydantic import BaseModel, field_validator, model_validator

class Thing(BaseModel):
    name: str

    @field_validator("name")
    def name_non_empty(cls, v):
        return v

    @model_validator(mode="after")
    def check_model(self):
        return self
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let thing_def = defs.into_iter().find(|d| d.name == "Thing").ok_or_else(|| AtlasError::Parse {
                path: PathBuf::new(),
                message: "Thing class not found".to_string(),
            })?;

            assert!(thing_def.tags.iter().any(|t| t == "pydantic_model"));
            assert_eq!(thing_def.field_count, Some(1));
            assert_eq!(thing_def.validator_count, Some(2));

            let validators_summary = thing_def
                .pydantic_validators_summary
                .as_deref()
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "pydantic_validators_summary missing".to_string(),
                })?;
            let validators_json: serde_json::Value = serde_json::from_str(validators_summary).map_err(|e| {
                AtlasError::Parse {
                    path: PathBuf::new(),
                    message: e.to_string(),
                }
            })?;

            assert_eq!(
                validators_json,
                serde_json::json!([
                    {"name": "check_model", "kind": "model_validator", "fields": [], "mode": "after"},
                    {"name": "name_non_empty", "kind": "field_validator", "fields": ["name"], "mode": null}
                ])
            );

            Ok(())
        })
    }

    #[test]
    fn test_extract_middleware_role_and_tags() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import FastAPI

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request, call_next):
    response = await call_next(request)
    return response
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let middleware_def = defs
                .iter()
                .find(|d| d.name == "add_process_time_header")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "middleware not found".to_string(),
                })?;

            assert!(middleware_def.tags.iter().any(|t| t == "fastapi_middleware"));
            assert!(middleware_def.tags.iter().any(|t| t == "router_app"));
            assert!(middleware_def.roles.contains(&FastapiRole::Middleware));

            Ok(())
        })
    }

    #[test]
    fn test_extract_lifespan_roles_startup_and_shutdown() -> Result<(), AtlasError> {
        Python::attach(|py| -> Result<(), AtlasError> {
            let code = r#"
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    pass

@app.on_event("shutdown")
async def on_shutdown():
    pass
"#;

            let ast = py.import("ast").map_err(|e| AtlasError::Parse {
                path: PathBuf::new(),
                message: format!("Failed to import ast: {}", e),
            })?;

            let tree = ast
                .call_method1("parse", (code,))
                .map_err(|e| AtlasError::Syntax {
                    path: PathBuf::new(),
                    line: 0,
                    message: e.to_string(),
                })?;

            let extractor = SymbolExtractor::new();
            let defs = extractor.extract_from_tree(tree)?;

            let startup = defs
                .iter()
                .find(|d| d.name == "on_startup")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "startup handler not found".to_string(),
                })?;
            assert!(startup.tags.iter().any(|t| t == "fastapi_lifespan_startup"));
            assert!(startup.tags.iter().any(|t| t == "router_app"));
            assert!(startup.roles.contains(&FastapiRole::LifespanStartup));

            let shutdown = defs
                .iter()
                .find(|d| d.name == "on_shutdown")
                .ok_or_else(|| AtlasError::Parse {
                    path: PathBuf::new(),
                    message: "shutdown handler not found".to_string(),
                })?;
            assert!(shutdown.tags.iter().any(|t| t == "fastapi_lifespan_shutdown"));
            assert!(shutdown.tags.iter().any(|t| t == "router_app"));
            assert!(shutdown.roles.contains(&FastapiRole::LifespanShutdown));

            Ok(())
        })
    }
}
