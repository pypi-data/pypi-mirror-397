# ranex-atlas

Atlas codebase indexing system for Ranex.

## Overview

Atlas scans Python projects, extracts symbols (functions, classes, endpoints), and stores them in SQLite for fast retrieval. This enables AI coding tools to find existing code instead of hallucinating or duplicating.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scanner   │───▶│   Parser    │───▶│   Storage   │
│  (walker)   │    │ (python_ast)│    │  (sqlite)   │
└─────────────┘    └─────────────┘    └─────────────┘
      │                   │                  │
      ▼                   ▼                  ▼
  Find .py files    Parse AST &        Store artifacts
  Respect ignore    Extract symbols    in atlas.sqlite
```

## Usage

```rust
use ranex_atlas::Atlas;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize Atlas for a project
    let mut atlas = Atlas::new(Path::new("/path/to/project"))?;

    // Scan the project
    let result = atlas.scan()?;
    println!("Found {} artifacts in {} files",
             result.stats.artifacts_found,
             result.stats.files_parsed);

    // Search for symbols
    let matches = atlas.search("payment", 10)?;
    for artifact in matches {
        println!("  {} ({}) - {}:{}",
                 artifact.symbol_name,
                 artifact.kind,
                 artifact.file_path.display(),
                 artifact.line_start);
    }

    Ok(())
}
```

## Module Structure

```
ranex-atlas/
├── src/
│   ├── lib.rs           # Public API: Atlas struct
│   ├── artifact.rs      # Artifact processing
│   ├── query.rs         # Query builder
│   ├── scanner/
│   │   ├── mod.rs
│   │   ├── walker.rs    # File discovery
│   │   └── filter.rs    # .ranexignore support
│   ├── parser/
│   │   ├── mod.rs
│   │   ├── python_ast.rs  # PyO3 → Python ast
│   │   └── extractor.rs   # Symbol extraction
│   └── storage/
│       ├── mod.rs
│       ├── schema.rs      # SQL schema
│       ├── repository.rs  # CRUD operations
│       └── migrations.rs  # Schema upgrades
└── Cargo.toml
```

## Features

- **Incremental Scanning**: Only re-parses changed files (hash-based detection)
- **Python AST**: Uses Python's `ast` module via PyO3 for 100% accuracy
- **FastAPI Detection**: Recognizes `@app.get`, `@router.post`, etc.
- **Contract Detection**: Recognizes `@Contract` decorators
- **Feature Extraction**: Infers feature names from directory structure

## Artifact Kinds

| Kind | Description |
|------|-------------|
| `Function` | Regular function definition |
| `AsyncFunction` | Async function (`async def`) |
| `Class` | Class definition |
| `Method` | Method inside a class |
| `Endpoint` | HTTP route (FastAPI) |
| `Contract` | Contract-decorated function |
| `Model` | Pydantic model |
| `Constant` | Module-level constant |

## License

MIT
