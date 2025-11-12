"""
Tests for sanitizer module.
"""

import pytest

from env_integrity_check.sanitizer import Sanitizer


def test_sanitizer_basic():
    """Test basic sanitization."""
    sanitizer = Sanitizer()
    result = {
        "message": "API_KEY=secret123",
        "details": {"input": "secret123"},
    }

    sanitized = sanitizer.sanitize_result(result)

    assert "***REDACTED***" in sanitized["message"]
    assert "secret123" not in sanitized["message"]


def test_sanitizer_sensitive_keys():
    """Test sanitization of sensitive keys."""
    sanitizer = Sanitizer()
    result = {
        "details": {
            "password": "mypassword",
            "username": "admin",
            "api_key": "key123",
        }
    }

    sanitized = sanitizer.sanitize_result(result)

    assert sanitized["details"]["password"] == "***REDACTED***"
    assert sanitized["details"]["username"] == "admin"
    assert sanitized["details"]["api_key"] == "***REDACTED***"


def test_sanitizer_nested_dict():
    """Test sanitization of nested dictionaries."""
    sanitizer = Sanitizer()
    result = {
        "details": {
            "config": {
                "secret_key": "secret123",
                "app_name": "myapp",
            }
        }
    }

    sanitized = sanitizer.sanitize_result(result)

    assert sanitized["details"]["config"]["secret_key"] == "***REDACTED***"
    assert sanitized["details"]["config"]["app_name"] == "myapp"


def test_sanitizer_env_vars():
    """Test sanitization of environment variables."""
    sanitizer = Sanitizer()
    env_vars = {
        "API_KEY": {"value": "key123", "line": 1},
        "APP_NAME": {"value": "myapp", "line": 2},
        "PASSWORD": {"value": "secret", "line": 3},
    }

    sanitized = sanitizer.sanitize_env_vars(env_vars)

    assert sanitized["API_KEY"]["value"] == "***REDACTED***"
    assert sanitized["APP_NAME"]["value"] == "myapp"
    assert sanitized["PASSWORD"]["value"] == "***REDACTED***"


def test_is_sensitive_key():
    """Test sensitive key detection."""
    sanitizer = Sanitizer()

    assert sanitizer._is_sensitive_key("password")
    assert sanitizer._is_sensitive_key("API_KEY")
    assert sanitizer._is_sensitive_key("secret_token")
    assert not sanitizer._is_sensitive_key("username")
    assert not sanitizer._is_sensitive_key("app_name")


def test_sanitizer_custom_redaction():
    """Test custom redaction text."""
    sanitizer = Sanitizer(redaction_text="[HIDDEN]")
    result = {
        "details": {"password": "secret123"}
    }

    sanitized = sanitizer.sanitize_result(result)

    assert sanitized["details"]["password"] == "[HIDDEN]"
