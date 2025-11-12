"""
Tests for policy loader module.
"""

import pytest
from pathlib import Path

from env_integrity_check.policy_loader import PolicyLoader


def test_policy_loader_valid_policy(tmp_path):
    """Test loading valid policy."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
required:
  - APP_NAME
  - DATABASE_URL
forbidden:
  - DEBUG
"""
    )

    loader = PolicyLoader(policy_file)
    policy = loader.load()

    assert "required" in policy
    assert "APP_NAME" in policy["required"]
    assert "forbidden" in policy
    assert "DEBUG" in policy["forbidden"]


def test_policy_loader_with_patterns(tmp_path):
    """Test loading policy with patterns."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
patterns:
  - regex: "^TEST_.*"
    action: warn
    message: Test variable found
"""
    )

    loader = PolicyLoader(policy_file)
    policy = loader.load()

    assert "patterns" in policy
    assert len(policy["patterns"]) == 1
    assert policy["patterns"][0]["regex"] == "^TEST_.*"


def test_policy_loader_invalid_yaml(tmp_path):
    """Test loading invalid YAML."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("invalid: yaml: content:")

    loader = PolicyLoader(policy_file)

    with pytest.raises(ValueError, match="Invalid YAML"):
        loader.load()


def test_policy_loader_empty_file(tmp_path):
    """Test loading empty file."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("")

    loader = PolicyLoader(policy_file)

    with pytest.raises(ValueError, match="empty"):
        loader.load()


def test_policy_loader_invalid_section(tmp_path):
    """Test policy with invalid section."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
invalid_section:
  - value
"""
    )

    loader = PolicyLoader(policy_file)

    with pytest.raises(ValueError, match="Invalid policy section"):
        loader.load()


def test_policy_loader_invalid_required_type(tmp_path):
    """Test policy with invalid required type."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
required: not_a_list
"""
    )

    loader = PolicyLoader(policy_file)

    with pytest.raises(ValueError, match="must be a list"):
        loader.load()


def test_policy_loader_invalid_pattern_regex(tmp_path):
    """Test policy with invalid regex pattern."""
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
patterns:
  - regex: "[invalid(regex"
    action: warn
"""
    )

    loader = PolicyLoader(policy_file)

    with pytest.raises(ValueError, match="Invalid regex pattern"):
        loader.load()


def test_create_example_policy(tmp_path):
    """Test creating example policy."""
    policy_file = tmp_path / "example.yaml"

    PolicyLoader.create_example_policy(policy_file)

    assert policy_file.exists()
    loader = PolicyLoader(policy_file)
    policy = loader.load()

    assert "required" in policy
    assert "forbidden" in policy
    assert "patterns" in policy
    assert "metadata" in policy
