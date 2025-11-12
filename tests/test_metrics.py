"""
Tests for metrics module.
"""

import pytest

from env_integrity_check.metrics import Metrics


def test_metrics_initialization():
    """Test metrics initialization."""
    metrics = Metrics()

    assert metrics.metrics["file_size_bytes"] == 0
    assert metrics.metrics["env_var_count"] == 0
    assert metrics.metrics["schema_violations"] == 0
    assert metrics.metrics["secrets_found"] == 0
    assert metrics.metrics["policy_violations"] == 0
    assert metrics.metrics["policy_loaded"] is False
    assert "timestamp" in metrics.metrics


def test_metrics_recording():
    """Test recording metrics."""
    metrics = Metrics()

    metrics.record_file_size(1024)
    metrics.record_env_var_count(10)
    metrics.record_schema_violations(2)
    metrics.record_secrets_found(1)
    metrics.record_policy_violations(3)
    metrics.record_policy_loaded()

    assert metrics.metrics["file_size_bytes"] == 1024
    assert metrics.metrics["env_var_count"] == 10
    assert metrics.metrics["schema_violations"] == 2
    assert metrics.metrics["secrets_found"] == 1
    assert metrics.metrics["policy_violations"] == 3
    assert metrics.metrics["policy_loaded"] is True


def test_metrics_total_violations():
    """Test total violations calculation."""
    metrics = Metrics()

    metrics.record_schema_violations(2)
    metrics.record_secrets_found(1)
    metrics.record_policy_violations(3)

    assert metrics.get_total_violations() == 6


def test_metrics_to_dict():
    """Test metrics export to dictionary."""
    metrics = Metrics()
    metrics.record_file_size(512)
    metrics.record_env_var_count(5)

    data = metrics.to_dict()

    assert isinstance(data, dict)
    assert data["file_size_bytes"] == 512
    assert data["env_var_count"] == 5


def test_metrics_str():
    """Test metrics string representation."""
    metrics = Metrics()
    metrics.record_file_size(256)
    metrics.record_env_var_count(3)

    output = str(metrics)

    assert "256 bytes" in output
    assert "3" in output
