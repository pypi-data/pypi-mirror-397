FIREWALL_YAML_TEMPLATE = '''version: "1.0"
mode: strict

allowed_packages:
  - requests
  - fastapi
  - pydantic

blocked_patterns:
  - pattern: "os.system"
    reason: "Command injection risk"
    severity: Critical
    alternatives:
      - subprocess.run

# Optional: tighten/relax typosquat sensitivity
# This checks suspicious imports like "requsets" -> "requests"
typo_detection:
  enabled: true
  max_edit_distance: 2

# Internal import prefixes (your own app code). These are validated differently
# than third-party packages.
internal_prefixes:
  - "app."
  - "src."
'''
