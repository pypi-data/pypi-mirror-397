//! Firewall policy data structures and loader.

use ranex_core::{FirewallError, FirewallResult};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::path::Path;

/// Severity level for policy violations
#[derive(Debug, Clone, Copy, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "PascalCase")]
pub enum Severity {
    Critical,
    High,
    #[default]
    Medium,
    Low,
}

/// Main firewall policy
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Policy {
    #[serde(default = "default_version")]
    pub version: String,

    #[serde(default)]
    pub mode: PolicyMode,

    #[serde(default)]
    pub allowed_packages: Vec<String>,

    #[serde(default)]
    pub blocked_patterns: Vec<BlockedPattern>,

    #[serde(default)]
    pub allowed_internal_patterns: Vec<String>,

    #[serde(default)]
    pub typo_detection: TypoDetectionConfig,

    #[serde(default)]
    pub atlas: AtlasConfig,

    #[serde(default)]
    pub internal_prefixes: Vec<String>,
}

#[derive(Debug, Clone, Copy, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum PolicyMode {
    #[default]
    Strict,
    AuditOnly,
    Disabled,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct BlockedPattern {
    pub pattern: String,
    pub reason: String,
    #[serde(default)]
    pub severity: Severity,
    #[serde(default)]
    pub alternatives: Vec<String>,
    #[serde(default)]
    pub is_prefix_match: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct TypoDetectionConfig {
    #[serde(default = "default_true")]
    pub enabled: bool,
    #[serde(default = "default_max_distance")]
    pub max_edit_distance: usize,
    #[serde(default)]
    pub known_typos: Vec<KnownTypo>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct KnownTypo {
    pub actual: String,
    pub typos: Vec<String>,
}

/// Atlas configuration for internal import validation
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct AtlasConfig {
    /// Enable Atlas integration for internal imports
    #[serde(default = "default_true")]
    pub enabled: bool,

    /// Path to Atlas database (relative to .ranex/)
    #[serde(default = "default_atlas_path")]
    pub db_path: String,

    /// Cache TTL in seconds
    #[serde(default = "default_cache_ttl")]
    pub cache_ttl: u64,

    /// Whether internal imports should **fail open** on Atlas errors.
    ///
    /// - true  (default): Atlas errors/circuit-open are treated as "allow" to
    ///   prioritize availability.
    /// - false: Atlas errors/circuit-open are treated as unknown/blocked so
    ///   that missing Atlas data cannot silently weaken enforcement.
    #[serde(default = "default_true")]
    pub fail_open: bool,
}

fn default_atlas_path() -> String {
    "atlas.sqlite".to_string()
}

fn default_cache_ttl() -> u64 {
    300 // 5 minutes
}

impl Default for AtlasConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            db_path: default_atlas_path(),
            cache_ttl: default_cache_ttl(),
            fail_open: true,
        }
    }
}

impl Policy {
    /// Load policy from YAML file
    pub fn load<P: AsRef<Path>>(path: P) -> FirewallResult<Self> {
        let path = path.as_ref();
        let contents = std::fs::read_to_string(path).map_err(|e| FirewallError::PolicyError {
            config_path: path.display().to_string(),
            reason: e.to_string(),
        })?;

        let policy: Policy =
            serde_yaml::from_str(&contents).map_err(|e| FirewallError::YamlParse(e.to_string()))?;
        policy.validate()?;
        Ok(policy)
    }

    /// Validate policy configuration
    pub fn validate(&self) -> FirewallResult<()> {
        // Ensure at least one allowed package or audit-only mode
        if self.allowed_packages.is_empty() && self.mode == PolicyMode::Strict {
            return Err(FirewallError::PolicyError {
                config_path: "config".to_string(),
                reason: "No allowed packages in strict mode".to_string(),
            });
        }

        // Guard against obviously invalid allowed package entries
        if self
            .allowed_packages
            .iter()
            .any(|p| normalize_package_name(p).is_empty())
        {
            return Err(FirewallError::PolicyError {
                config_path: "config".to_string(),
                reason: "allowed_packages contains empty or invalid entries".to_string(),
            });
        }

        Ok(())
    }

    /// Create default policy for testing (minimal rules)
    pub fn default_test_policy() -> Self {
        Self {
            version: "1.0".to_string(),
            mode: PolicyMode::Strict,
            allowed_packages: vec![
                "fastapi".to_string(),
                "pydantic".to_string(),
                "requests".to_string(),
            ],
            blocked_patterns: vec![BlockedPattern {
                pattern: "os.system".to_string(),
                reason: "Command injection risk".to_string(),
                severity: Severity::Critical,
                alternatives: vec!["subprocess.run".to_string()],
                is_prefix_match: false,
            }],
            allowed_internal_patterns: vec![],
            typo_detection: TypoDetectionConfig::default(),
            atlas: AtlasConfig::default(),
            internal_prefixes: vec!["app.".to_string()],
        }
    }

    /// Create production-ready policy with comprehensive security rules.
    ///
    /// This policy includes:
    /// - CRITICAL: Code execution, deserialization, system access
    /// - HIGH: Dangerous network, file operations
    /// - MEDIUM: Deprecated or risky patterns
    /// - Safe stdlib and popular packages allowed
    /// - Known typosquat patterns
    pub fn production_policy() -> Self {
        Self {
            version: "2.0".to_string(),
            mode: PolicyMode::Strict,

            // ================================================================
            // ALLOWED PACKAGES - Safe, vetted packages
            // ================================================================
            allowed_packages: vec![
                // === Python Standard Library (commonly imported) ===
                "abc".to_string(),
                "asyncio".to_string(),
                "base64".to_string(),
                "collections".to_string(),
                "contextlib".to_string(),
                "copy".to_string(),
                "csv".to_string(),
                "dataclasses".to_string(),
                "datetime".to_string(),
                "decimal".to_string(),
                "enum".to_string(),
                "functools".to_string(),
                "hashlib".to_string(),
                "hmac".to_string(),
                "http".to_string(),
                "io".to_string(),
                "itertools".to_string(),
                "json".to_string(),
                "logging".to_string(),
                "math".to_string(),
                "operator".to_string(),
                "os.path".to_string(),
                "pathlib".to_string(),
                "random".to_string(),
                "re".to_string(),
                "secrets".to_string(),
                "shutil".to_string(),
                "socket".to_string(),
                "ssl".to_string(),
                "statistics".to_string(),
                "string".to_string(),
                "struct".to_string(),
                "sys".to_string(),
                "tempfile".to_string(),
                "textwrap".to_string(),
                "threading".to_string(),
                "time".to_string(),
                "traceback".to_string(),
                "typing".to_string(),
                "unittest".to_string(),
                "urllib.parse".to_string(),
                "uuid".to_string(),
                "warnings".to_string(),
                "weakref".to_string(),
                "zipfile".to_string(),
                "zlib".to_string(),
                // === Web Frameworks ===
                "fastapi".to_string(),
                "flask".to_string(),
                "django".to_string(),
                "starlette".to_string(),
                "quart".to_string(),
                "uvicorn".to_string(),
                "gunicorn".to_string(),
                // === HTTP & Networking ===
                "requests".to_string(),
                "httpx".to_string(),
                "aiohttp".to_string(),
                "urllib3".to_string(),
                "websockets".to_string(),
                // === Data Validation ===
                "pydantic".to_string(),
                "marshmallow".to_string(),
                "attrs".to_string(),
                "cerberus".to_string(),
                // === Database ===
                "sqlalchemy".to_string(),
                "sqlmodel".to_string(),
                "asyncpg".to_string(),
                "psycopg2".to_string(),
                "pymysql".to_string(),
                "aiosqlite".to_string(),
                "redis".to_string(),
                "pymongo".to_string(),
                "motor".to_string(),
                // === Serialization (Safe) ===
                "orjson".to_string(),
                "ujson".to_string(),
                "msgpack".to_string(),
                "toml".to_string(),
                "pyyaml".to_string(),
                "yaml".to_string(),
                // === Async & Concurrency ===
                "anyio".to_string(),
                "trio".to_string(),
                "celery".to_string(),
                "rq".to_string(),
                "dramatiq".to_string(),
                // === Cryptography ===
                "cryptography".to_string(),
                "bcrypt".to_string(),
                "argon2".to_string(),
                "passlib".to_string(),
                "pyjwt".to_string(),
                "jwt".to_string(), // PyJWT import alias
                "python-jose".to_string(),
                // === Observability ===
                "structlog".to_string(),
                "loguru".to_string(),
                "opentelemetry".to_string(),
                "prometheus_client".to_string(),
                "sentry_sdk".to_string(),
                // === Testing ===
                "pytest".to_string(),
                "pytest_asyncio".to_string(),
                "hypothesis".to_string(),
                "faker".to_string(),
                "factory_boy".to_string(),
                "responses".to_string(),
                "respx".to_string(),
                "freezegun".to_string(),
                // === Data Science (Common) ===
                "numpy".to_string(),
                "pandas".to_string(),
                "scipy".to_string(),
                "matplotlib".to_string(),
                "seaborn".to_string(),
                "scikit-learn".to_string(),
                // === CLI & Config ===
                "click".to_string(),
                "typer".to_string(),
                "rich".to_string(),
                "python-dotenv".to_string(),
                "dynaconf".to_string(),
                // === Utilities ===
                "tenacity".to_string(),
                "cachetools".to_string(),
                "python-dateutil".to_string(),
                "pytz".to_string(),
                "pendulum".to_string(),
                "more-itertools".to_string(),
                "toolz".to_string(),
            ],

            // ================================================================
            // BLOCKED PATTERNS - Dangerous operations
            // ================================================================
            blocked_patterns: vec![
                // === CRITICAL: Remote Code Execution ===
                BlockedPattern {
                    pattern: "pickle".to_string(),
                    reason: "Arbitrary code execution via deserialization - CVE-prone".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec![
                        "json".to_string(),
                        "orjson".to_string(),
                        "msgpack".to_string(),
                    ],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "marshal".to_string(),
                    reason: "Unsafe deserialization, can execute arbitrary code".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["json".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "shelve".to_string(),
                    reason: "Uses pickle internally - same RCE risks".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["sqlite3".to_string(), "redis".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "dill".to_string(),
                    reason: "Extended pickle - same deserialization vulnerabilities".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec![
                        "json".to_string(),
                        "cloudpickle with allowlist".to_string(),
                    ],
                    is_prefix_match: true,
                },
                // === CRITICAL: Code Execution ===
                BlockedPattern {
                    pattern: "eval".to_string(),
                    reason: "Arbitrary code execution from strings".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["ast.literal_eval (for literals only)".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "exec".to_string(),
                    reason: "Arbitrary code execution".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["Avoid dynamic code execution".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "compile".to_string(),
                    reason: "Can compile arbitrary code for execution".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["Static imports, avoid dynamic code".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "__import__".to_string(),
                    reason: "Dynamic imports can load malicious modules".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["importlib.import_module with allowlist".to_string()],
                    is_prefix_match: false,
                },
                // === CRITICAL: System Access ===
                BlockedPattern {
                    pattern: "os.system".to_string(),
                    reason: "Shell injection vulnerability, command execution".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["subprocess.run with shell=False".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "os.popen".to_string(),
                    reason: "Shell injection vulnerability".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["subprocess.run".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "os.spawn".to_string(),
                    reason: "Process spawning without proper sanitization".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["subprocess.run".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "os.exec".to_string(),
                    reason: "Direct process replacement".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["subprocess.run".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "subprocess.Popen".to_string(),
                    reason: "Prefer subprocess.run for safer defaults".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["subprocess.run".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "commands".to_string(),
                    reason: "Deprecated, shell injection risks".to_string(),
                    severity: Severity::Critical,
                    alternatives: vec!["subprocess.run".to_string()],
                    is_prefix_match: true,
                },
                // === HIGH: Network Risks ===
                BlockedPattern {
                    pattern: "telnetlib".to_string(),
                    reason: "Unencrypted protocol, credentials exposed".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["paramiko (SSH)".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "ftplib".to_string(),
                    reason: "Unencrypted FTP, credentials exposed".to_string(),
                    severity: Severity::High,
                    alternatives: vec![
                        "paramiko (SFTP)".to_string(),
                        "ftplib with TLS".to_string(),
                    ],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "smtplib".to_string(),
                    reason: "Requires explicit TLS configuration".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["Use SMTP_SSL or starttls()".to_string()],
                    is_prefix_match: true,
                },
                // === HIGH: Dangerous File Operations ===
                BlockedPattern {
                    pattern: "os.chmod".to_string(),
                    reason: "Can weaken file permissions".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["pathlib.Path.chmod with explicit mode".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "os.chown".to_string(),
                    reason: "Ownership changes can escalate privileges".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["Avoid or use with explicit validation".to_string()],
                    is_prefix_match: false,
                },
                // === MEDIUM: XML Vulnerabilities ===
                BlockedPattern {
                    pattern: "xml.etree".to_string(),
                    reason: "XML parsing vulnerable to XXE attacks by default".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec![
                        "defusedxml".to_string(),
                        "lxml with safe settings".to_string(),
                    ],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "xml.dom".to_string(),
                    reason: "XML parsing vulnerable to XXE attacks".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["defusedxml".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "xml.sax".to_string(),
                    reason: "XML parsing vulnerable to XXE attacks".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["defusedxml".to_string()],
                    is_prefix_match: true,
                },
                // === MEDIUM: Deprecated/Risky ===
                BlockedPattern {
                    pattern: "cgi".to_string(),
                    reason: "Deprecated CGI module, security issues".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec!["FastAPI".to_string(), "Flask".to_string()],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "crypt".to_string(),
                    reason: "Weak cryptography, platform-dependent".to_string(),
                    severity: Severity::High,
                    alternatives: vec![
                        "bcrypt".to_string(),
                        "argon2".to_string(),
                        "passlib".to_string(),
                    ],
                    is_prefix_match: true,
                },
                BlockedPattern {
                    pattern: "md5".to_string(),
                    reason: "MD5 is cryptographically broken".to_string(),
                    severity: Severity::High,
                    alternatives: vec!["hashlib.sha256".to_string(), "hashlib.blake2b".to_string()],
                    is_prefix_match: false,
                },
                BlockedPattern {
                    pattern: "sha1".to_string(),
                    reason: "SHA1 is cryptographically weak".to_string(),
                    severity: Severity::Medium,
                    alternatives: vec![
                        "hashlib.sha256".to_string(),
                        "hashlib.sha3_256".to_string(),
                    ],
                    is_prefix_match: false,
                },
                // === LOW: Code Quality ===
                BlockedPattern {
                    pattern: "assert".to_string(),
                    reason: "Assertions disabled with -O flag, not for validation".to_string(),
                    severity: Severity::Low,
                    alternatives: vec!["Explicit if/raise for validation".to_string()],
                    is_prefix_match: false,
                },
            ],

            allowed_internal_patterns: vec![
                "app.*".to_string(),
                "src.*".to_string(),
                "lib.*".to_string(),
                "tests.*".to_string(),
            ],

            typo_detection: TypoDetectionConfig {
                enabled: true,
                max_edit_distance: 2,
                known_typos: vec![
                    KnownTypo {
                        actual: "requests".to_string(),
                        typos: vec![
                            "reqeusts".to_string(),
                            "requsts".to_string(),
                            "reqests".to_string(),
                            "request".to_string(),
                            "reequests".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "numpy".to_string(),
                        typos: vec![
                            "numby".to_string(),
                            "numppy".to_string(),
                            "nunpy".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "pandas".to_string(),
                        typos: vec![
                            "pandes".to_string(),
                            "pandsa".to_string(),
                            "panda".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "django".to_string(),
                        typos: vec![
                            "djano".to_string(),
                            "djanjo".to_string(),
                            "djnago".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "flask".to_string(),
                        typos: vec![
                            "flaask".to_string(),
                            "flaks".to_string(),
                            "falsk".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "tensorflow".to_string(),
                        typos: vec![
                            "tenserflow".to_string(),
                            "tesnorflow".to_string(),
                            "tensorflwo".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "cryptography".to_string(),
                        typos: vec![
                            "cyptography".to_string(),
                            "crytography".to_string(),
                            "cryptograpy".to_string(),
                        ],
                    },
                    KnownTypo {
                        actual: "pydantic".to_string(),
                        typos: vec![
                            "pydanctic".to_string(),
                            "pydnatic".to_string(),
                            "pydantc".to_string(),
                        ],
                    },
                ],
            },

            atlas: AtlasConfig::default(),
            internal_prefixes: vec!["app.".to_string(), "src.".to_string(), "lib.".to_string()],
        }
    }

    /// Get allowed packages as HashSet for O(1) lookup
    pub fn allowed_packages_set(&self) -> HashSet<String> {
        self
            .allowed_packages
            .iter()
            .map(|p| normalize_package_name(p))
            .collect()
    }
}

fn default_version() -> String {
    "1.0".to_string()
}
fn default_true() -> bool {
    true
}
fn default_max_distance() -> usize {
    2
}

impl Default for Policy {
    fn default() -> Self {
        Self {
            version: default_version(),
            mode: PolicyMode::default(),
            allowed_packages: Vec::new(),
            blocked_patterns: Vec::new(),
            allowed_internal_patterns: Vec::new(),
            typo_detection: TypoDetectionConfig::default(),
            atlas: AtlasConfig::default(),
            internal_prefixes: Vec::new(),
        }
    }
}

/// Normalize a package specification into a bare import name.
///
/// This is intentionally conservative: it strips common version specifiers
/// and extras (`[extra]`) so that entries like `fastapi>=0.115.0` or
/// `uvicorn[standard]>=0.30.0` are treated as `fastapi` / `uvicorn` for
/// import-allowlist purposes.
fn normalize_package_name(name: &str) -> String {
    let trimmed = name.trim();
    if trimmed.is_empty() {
        return String::new();
    }

    // Strip everything from the first occurrence of any of these separators:
    // - space: comments or trailing metadata
    // - '['  : extras, e.g. "uvicorn[standard]"
    // - version operators: <, >, =, !, ~
    let separators: [char; 7] = [' ', '[', '<', '>', '=', '!', '~'];
    let cut_idx = trimmed
        .find(|c: char| separators.contains(&c))
        .unwrap_or(trimmed.len());

    // If everything before the separator is empty, fall back to the original
    // string to avoid turning arbitrary garbage into "".
    let base = &trimmed[..cut_idx];
    if base.is_empty() {
        trimmed.to_string()
    } else {
        base.to_string()
    }
}

impl Default for TypoDetectionConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            max_edit_distance: 2,
            known_typos: vec![],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_parse_minimal_policy() {
        let yaml = r#"
version: "1.0"
mode: strict
allowed_packages:
  - requests
  - flask
"#;
        let policy_res: Result<Policy, _> = serde_yaml::from_str(yaml);
        assert!(policy_res.is_ok(), "Expected policy YAML to parse");
        let Ok(policy) = policy_res else {
            return;
        };
        assert_eq!(policy.allowed_packages.len(), 2);
        assert_eq!(policy.mode, PolicyMode::Strict);
    }

    #[test]
    fn test_parse_blocked_patterns() {
        let yaml = r#"
blocked_patterns:
  - pattern: "os.system"
    reason: "Command injection"
    severity: Critical
"#;
        let policy_res: Result<Policy, _> = serde_yaml::from_str(yaml);
        assert!(policy_res.is_ok(), "Expected policy YAML to parse");
        let Ok(policy) = policy_res else {
            return;
        };
        assert_eq!(policy.blocked_patterns.len(), 1);
        if let Some(pattern) = policy.blocked_patterns.first() {
            assert_eq!(pattern.severity, Severity::Critical);
        }
    }

    #[test]
    fn test_load_from_file() {
        let file_res = NamedTempFile::new();
        assert!(file_res.is_ok(), "Expected temp file to be created");
        let Ok(mut file) = file_res else {
            return;
        };

        let write_res = writeln!(file, "version: '1.0'\nallowed_packages:\n  - test");
        assert!(write_res.is_ok(), "Expected to write policy YAML");

        let policy_res = Policy::load(file.path());
        assert!(policy_res.is_ok(), "Expected policy to load from file");
        let Ok(policy) = policy_res else {
            return;
        };
        assert_eq!(policy.allowed_packages, vec!["test"]);
    }

    #[test]
    fn test_validation_empty_strict() {
        let policy = Policy {
            mode: PolicyMode::Strict,
            allowed_packages: vec![],
            ..Default::default()
        };
        assert!(policy.validate().is_err());
    }
}
