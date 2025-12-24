# ranex-firewall

Dependency firewall and import validation for Ranex.

## Overview

`ranex-firewall` provides enterprise-grade dependency validation for Python applications:

- **Rules Engine**: Allowlist/blocklist for dependencies
- **Import Analysis**: Parse and validate Python import statements
- **Typosquatting Detection**: Detect malicious packages with similar names to popular packages
- **Violation Reporting**: Generate detailed reports of policy violations

## Features

- ✅ Simple allowlist/blocklist rules with wildcard support
- ✅ Levenshtein distance-based typosquatting detection
- ✅ Standard library detection (skips stdlib imports by default)
- ✅ Relative import handling
- ✅ Star import warnings
- ✅ Detailed violation and warning reports

## Usage

```rust
use ranex_firewall::{FirewallAnalyzer, AnalyzerConfig, RulesEngine};
use std::path::Path;

// Create a rules engine
let mut rules = RulesEngine::new();
rules.allow("requests");
rules.allow("fastapi");
rules.block("os");
rules.block("subprocess");

// Configure the analyzer
let config = AnalyzerConfig {
    rules,
    check_typosquats: true,
    typosquat_threshold: 0.8,
    skip_stdlib: true,
    skip_relative: true,
};

// Analyze a file
let analyzer = FirewallAnalyzer::new(config);
let report = analyzer.analyze_file(Path::new("app.py"))?;

// Check the results
if !report.is_clean {
    for violation in &report.violations {
        println!("{}:{} - {}", violation.file.display(), violation.line, violation.message);
    }
}
```

## Rules File Format

Create a `.ranex/firewall.rules` file:

```
# Allowed packages
allow requests
allow fastapi
allow pydantic

# Blocked packages
block os
block subprocess

# Warned packages (non-blocking)
warn deprecated_package
```

Load rules from a file:

```rust
use ranex_firewall::RulesEngine;

let rules = RulesEngine::load_from_file(Path::new(".ranex/firewall.rules"))?;
```

## Wildcard Patterns

Use custom rules with wildcard patterns:

```rust
use ranex_firewall::{RulesEngine, FirewallRule, RuleAction};

let mut rules = RulesEngine::new();
rules.add_rule(FirewallRule {
    name: "block_private".to_string(),
    action: RuleAction::Block,
    patterns: vec!["_internal*".to_string()],
    reason: Some("Private packages blocked".to_string()),
    priority: 100,
});
```

## Error Handling

This crate uses `ranex_core::FirewallError` for all error conditions:

- `RulesNotFound`: Rules file doesn't exist
- `InvalidRule`: Malformed rule syntax
- `PolicyViolation`: Import violates policy
- `AnalysisError`: Failed to analyze file
- `Io`: I/O error

## Architecture

The firewall analyzer processes imports through a pipeline:

1. **Parse**: Extract imports from Python source using `python_imports::parse_imports`
2. **Filter**: Skip stdlib and relative imports (if configured)
3. **Check Rules**: Apply allowlist/blocklist rules
4. **Typosquat Detection**: Check for suspicious package names
5. **Report**: Generate detailed violation and warning reports

## Integration

This crate is designed to integrate with:

- `ranex-core`: Shared error types and configuration
- `ranex-cli`: CLI commands for firewall checks
- `ranex-py`: Python bindings for runtime validation

## Testing

Run the test suite:

```bash
cargo test -p ranex-firewall
```

All tests should pass with 100% success rate.

## License

Same as the parent Ranex project.
