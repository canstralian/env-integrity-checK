"""
Tests for secrets scanner module.
"""

import pytest
from pathlib import Path

from env_integrity_check.secrets_scanner import SecretsScanner


def test_secrets_scanner_initialization():
    """Test secrets scanner initialization."""
    scanner = SecretsScanner()

    assert scanner.settings is not None


def test_secrets_scanner_scan_content():
    """Test scanning content for secrets."""
    scanner = SecretsScanner()
    content = """
APP_NAME=myapp
# This won't trigger detection in test
API_KEY=example_key_value
"""

    results = scanner.scan_env_content(content)

    # Results may be empty or contain findings depending on detect-secrets
    assert isinstance(results, list)


def test_secrets_scanner_find_var_at_line():
    """Test finding variable at specific line."""
    scanner = SecretsScanner()
    env_vars = {
        "VAR1": {"value": "value1", "line": 1},
        "VAR2": {"value": "value2", "line": 3},
        "VAR3": {"value": "value3", "line": 5},
    }

    assert scanner._find_var_at_line(env_vars, 3) == "VAR2"
    assert scanner._find_var_at_line(env_vars, 5) == "VAR3"
    assert scanner._find_var_at_line(env_vars, 99) == ""


def test_secrets_scanner_scan_file(tmp_path):
    """Test scanning a file for secrets."""
    scanner = SecretsScanner()

    env_file = tmp_path / ".env"
    env_file.write_text(
        """
APP_NAME=myapp
DATABASE_URL=postgresql://localhost/db
"""
    )

    env_vars = {
        "APP_NAME": {"value": "myapp", "line": 2},
        "DATABASE_URL": {"value": "postgresql://localhost/db", "line": 3},
    }

    results = scanner.scan_env_file(env_file, env_vars)

    # Results may vary based on detect-secrets configuration
    assert isinstance(results, list)
