# ranex-core

Core types, errors, configuration, and logging for the Ranex project.

## Overview

This crate provides foundational abstractions used by all other Ranex crates:

- **Types**: `Artifact`, `ArtifactKind`, `FileInfo` - core domain models
- **Errors**: `RanexError`, `AtlasError`, `ConfigError` - unified error handling
- **Config**: `RanexConfig` - centralized configuration management
- **Logging**: Tracing-based structured logging setup

## Usage

```rust
use ranex_core::{Artifact, ArtifactKind, RanexError, RanexConfig};
use ranex_core::logging;

fn main() -> Result<(), RanexError> {
    // Initialize logging once at startup
    logging::init_logging(logging::LogConfig::default());

    // Load configuration from project root
    let config = RanexConfig::load(std::path::Path::new("."))?;
    
    tracing::info!(
        db = %config.atlas.db_filename,
        "Configuration loaded"
    );
    
    Ok(())
}
```

## Module Structure

```
ranex-core/
├── src/
│   ├── lib.rs        # Crate root, re-exports
│   ├── types.rs      # Artifact, ArtifactKind, FileInfo, ScanResult
│   ├── error.rs      # RanexError, AtlasError, ConfigError
│   ├── config.rs     # RanexConfig, AtlasConfig, LoggingConfig
│   ├── logging.rs    # Tracing subscriber setup
│   └── constants.rs  # VERSION, defaults, magic strings
└── Cargo.toml
```

## Design Principles

1. **No PyO3**: This crate is pure Rust with no Python dependencies
2. **No I/O Heavy Operations**: Just types, errors, and config loading
3. **Minimal Dependencies**: Only essential crates (serde, thiserror, tracing)
4. **Downstream Compatible**: Other crates depend on this, not vice versa

## License

MIT
