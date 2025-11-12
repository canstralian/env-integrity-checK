# env-integrity-checK

[![License](https://img.shields.io/github/license/canstralian/env-integrity-checK)](LICENSE)
[![Tests](https://github.com/canstralian/env-integrity-checK/actions/workflows/tests.yml/badge.svg)](https://github.com/canstralian/env-integrity-checK/actions)
[![Coverage](https://img.shields.io/codecov/c/github/canstralian/env-integrity-checK)](https://codecov.io/gh/canstralian/env-integrity-checK)
[![Version](https://img.shields.io/github/v/release/canstralian/env-integrity-checK)](https://github.com/canstralian/env-integrity-checK/releases)
[![Issues](https://img.shields.io/github/issues/canstralian/env-integrity-checK)](https://github.com/canstralian/env-integrity-checK/issues)

Environment configuration compliance framework with SARIF output.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Schema Definition](#schema-definition)
- [Policy Definition](#policy-definition)
- [SARIF Output](#sarif-output)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

`env-integrity-checK` is a Python CLI tool that validates `.env` files against Pydantic schemas, detects secrets using `detect-secrets`, sanitizes sensitive values, and emits deterministic SARIF reports for CI/CD integration. The tool generates reports in the Static Analysis Results Interchange Format (SARIF), making it compatible with numerous development tools and CI/CD pipelines.

## Key Features

- 🔍 **Schema Validation**: Validate environment variables against Pydantic models
- 🔐 **Secret Detection**: Detect secrets and credentials using `detect-secrets`
- 📋 **Policy Enforcement**: Define and enforce custom policies for environment variables
- 📊 **SARIF Output**: Generate SARIF 2.1.0 compliant reports for CI/CD integration
- 🧹 **Sanitization**: Automatically sanitize sensitive values in output
- 📈 **Metrics**: Track validation metrics for reporting
- ✅ **Cross-Platform**: Supports Linux, macOS, and Windows

## Installation

### Using pip

```bash
pip install env-integrity-check
```

### From source

```bash
git clone https://github.com/canstralian/env-integrity-checK.git
cd env-integrity-checK
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
env-integrity-check path/to/.env
```

### With Schema Validation

```bash
env-integrity-check path/to/.env --schema path/to/schema.py
```

### With Policy Enforcement

```bash
env-integrity-check path/to/.env --policy path/to/policy.yaml
```

### Full Example

```bash
env-integrity-check examples/example.env \
  --schema examples/schema.py \
  --policy examples/policy.yaml \
  --output report.sarif \
  --metrics
```

### Command Options

| Flag | Description |
|------|-------------|
| `--schema PATH` | Path to Pydantic schema module (Python file) |
| `--policy PATH` | Path to policy YAML file |
| `--output PATH, -o PATH` | Output SARIF report file (default: stdout) |
| `--sanitize/--no-sanitize` | Sanitize sensitive values in output (default: enabled) |
| `--detect-secrets/--no-detect-secrets` | Run detect-secrets scanner (default: enabled) |
| `--metrics/--no-metrics` | Include metrics in output (default: disabled) |
| `--version` | Show version and exit |
| `--help` | Show help message and exit |

## Schema Definition

Define a Pydantic model to validate your environment variables:

```python
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    app_name: str = Field(..., description="Application name")
    app_env: str = Field(..., description="Environment (dev, staging, prod)")
    database_url: str = Field(..., description="Database connection URL")
    api_key: str = Field(..., description="API key")
    debug: bool = Field(default=False, description="Debug mode")
    port: int = Field(default=8000, description="Application port")
```

## Policy Definition

Define policies in YAML format:

```yaml
metadata:
  name: Environment Policy
  version: 1.0.0

required:
  - APP_NAME
  - DATABASE_URL

forbidden:
  - DEBUG_MODE
  - UNSAFE_SETTING

patterns:
  - regex: ".*_PROD_.*"
    action: warn
    message: Production variables should not be in .env files
```

## SARIF Output

The tool generates SARIF 2.1.0 compliant reports that can be consumed by CI/CD systems:

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "env-integrity-check",
          "version": "0.1.0",
          "rules": [...]
        }
      },
      "results": [...]
    }
  ]
}
```

## Development

### Running Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=env_integrity_check --cov-report=html
```

### Code Formatting

```bash
black env_integrity_check tests
```

### Linting

```bash
ruff check env_integrity_check tests
```

## Contributing

We welcome contributions! To get started:

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Please make sure to update tests as appropriate.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
