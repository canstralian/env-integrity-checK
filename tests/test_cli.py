"""
Tests for CLI module.
"""

import pytest
from click.testing import CliRunner

from env_integrity_check.cli import main, parse_env_file, validate_policy


def test_parse_env_file_basic():
    """Test basic .env file parsing."""
    content = """
# Comment
APP_NAME=myapp
DATABASE_URL=postgresql://localhost/db
DEBUG=true
"""
    result = parse_env_file(content)

    assert len(result) == 3
    assert result["APP_NAME"]["value"] == "myapp"
    assert result["DATABASE_URL"]["value"] == "postgresql://localhost/db"
    assert result["DEBUG"]["value"] == "true"


def test_parse_env_file_with_quotes():
    """Test parsing with quoted values."""
    content = 'SECRET_KEY="my secret value"\nAPI_KEY=\'another-key\''
    result = parse_env_file(content)

    assert result["SECRET_KEY"]["value"] == "my secret value"
    assert result["API_KEY"]["value"] == "another-key"


def test_parse_env_file_empty_lines():
    """Test parsing with empty lines."""
    content = "\n\nVAR1=value1\n\n\nVAR2=value2\n\n"
    result = parse_env_file(content)

    assert len(result) == 2
    assert result["VAR1"]["value"] == "value1"
    assert result["VAR2"]["value"] == "value2"


def test_validate_policy_required():
    """Test policy validation for required variables."""
    env_vars = {
        "APP_NAME": {"value": "test", "line": 1},
    }
    policy = {
        "required": ["APP_NAME", "DATABASE_URL"],
    }

    results = validate_policy(env_vars, policy)

    assert len(results) == 1
    assert results[0]["rule_id"] == "missing-required-var"
    assert "DATABASE_URL" in results[0]["message"]


def test_validate_policy_forbidden():
    """Test policy validation for forbidden variables."""
    env_vars = {
        "DEBUG": {"value": "true", "line": 2},
    }
    policy = {
        "forbidden": ["DEBUG"],
    }

    results = validate_policy(env_vars, policy)

    assert len(results) == 1
    assert results[0]["rule_id"] == "forbidden-var"
    assert "DEBUG" in results[0]["message"]


def test_validate_policy_pattern():
    """Test policy validation for patterns."""
    env_vars = {
        "TEST_VAR": {"value": "test", "line": 1},
    }
    policy = {
        "patterns": [
            {
                "regex": "^TEST_.*",
                "action": "warn",
                "message": "Test variable found",
            }
        ],
    }

    results = validate_policy(env_vars, policy)

    assert len(results) == 1
    assert results[0]["rule_id"] == "pattern-match"
    assert results[0]["level"] == "warning"


def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "env-integrity-check" in result.output or "Validate .env files" in result.output
