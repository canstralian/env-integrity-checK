
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
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

`env-integrity-checK` is a lightweight, extensible framework for ensuring that your environment configurations comply with your organization's policies. The tool generates reports in the Static Analysis Results Interchange Format (SARIF), making it compatible with numerous development tools and CI/CD pipelines.

## Key Features

- 🔍 **Environment Compliance Auditing**: Validate configuration files for compliance with best practices.
- 🛠️ **SARIF Reporting**: Output results in SARIF format for easy integration with tools like GitHub Advanced Security.
- 🚀 **CI/CD Integration**: Easily add to workflows to automate environment integrity checks.
- ✅ **Cross-Platform**: Supports Linux, macOS, and Windows.

## Getting Started

These instructions will help you set up and use `env-integrity-checK` in your project.

### Prerequisites

Ensure you have the following dependencies installed:

- Python 3.8+
- pip
- Git

### Installation

You can install `env-integrity-checK` using `pip`:

```bash
pip install env-integrity-check
```

Or clone the repository directly:

```bash
git clone https://github.com/canstralian/env-integrity-checK.git
cd env-integrity-checK
pip install -r requirements.txt
```

### Usage

Run the following command to audit an environment configuration file:

```bash
env-integrity-check --config <path-to-config-file> --output sarif
```

#### Example

```bash
env-integrity-check --config ./example.env --output results.sarif
```

### Options

| Flag       | Description                          |
|------------|--------------------------------------|
| `--config` | Path to the environment config file. |
| `--output` | Output format (`sarif`, `json`).     |

## Contributing

We welcome contributions! To get started, check out our [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Please make sure to update tests as appropriate.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
```

---
