"""
Tests for SARIF reporter module.
"""

import pytest

from env_integrity_check.sarif_reporter import SARIFReporter


def test_sarif_reporter_initialization():
    """Test SARIF reporter initialization."""
    reporter = SARIFReporter("test-tool", "1.0.0")

    assert reporter.tool_name == "test-tool"
    assert reporter.tool_version == "1.0.0"


def test_sarif_report_structure():
    """Test SARIF report structure."""
    reporter = SARIFReporter("test-tool", "1.0.0")
    results = [
        {
            "rule_id": "test-rule",
            "level": "error",
            "message": "Test error",
            "location": {"line": 1},
        }
    ]

    report = reporter.generate_report(results, "test.env")

    assert report["version"] == "2.1.0"
    assert "$schema" in report
    assert "runs" in report
    assert len(report["runs"]) == 1
    assert report["runs"][0]["tool"]["driver"]["name"] == "test-tool"
    assert report["runs"][0]["tool"]["driver"]["version"] == "1.0.0"


def test_sarif_report_results():
    """Test SARIF report results conversion."""
    reporter = SARIFReporter("test-tool", "1.0.0")
    results = [
        {
            "rule_id": "schema-validation",
            "level": "error",
            "message": "Invalid value",
            "location": {"line": 5, "column": 1},
        }
    ]

    report = reporter.generate_report(results, "test.env")

    assert len(report["runs"][0]["results"]) == 1
    result = report["runs"][0]["results"][0]

    assert result["ruleId"] == "schema-validation"
    assert result["level"] == "error"
    assert result["message"]["text"] == "Invalid value"
    assert result["locations"][0]["physicalLocation"]["region"]["startLine"] == 5


def test_sarif_report_rules():
    """Test SARIF report rules extraction."""
    reporter = SARIFReporter("test-tool", "1.0.0")
    results = [
        {
            "rule_id": "schema-validation",
            "level": "error",
            "message": "Error 1",
            "location": {"line": 1},
        },
        {
            "rule_id": "secret-detected",
            "level": "error",
            "message": "Error 2",
            "location": {"line": 2},
        },
    ]

    report = reporter.generate_report(results, "test.env")

    rules = report["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules) == 2
    rule_ids = [rule["id"] for rule in rules]
    assert "schema-validation" in rule_ids
    assert "secret-detected" in rule_ids


def test_sarif_report_with_metrics():
    """Test SARIF report with metrics."""
    reporter = SARIFReporter("test-tool", "1.0.0")
    results = []
    metrics = {"file_size_bytes": 1024, "env_var_count": 10}

    report = reporter.generate_report(results, "test.env", metrics_data=metrics)

    assert "properties" in report["runs"][0]
    assert "metrics" in report["runs"][0]["properties"]
    assert report["runs"][0]["properties"]["metrics"]["file_size_bytes"] == 1024


def test_level_mapping():
    """Test level mapping."""
    reporter = SARIFReporter("test-tool", "1.0.0")

    assert reporter._map_level("error") == "error"
    assert reporter._map_level("warning") == "warning"
    assert reporter._map_level("info") == "note"
    assert reporter._map_level("note") == "note"
    assert reporter._map_level("unknown") == "warning"


def test_fingerprint_deterministic():
    """Test fingerprint generation is deterministic."""
    reporter = SARIFReporter("test-tool", "1.0.0")

    fp1 = reporter._generate_fingerprint("test-rule", "test.env", {"line": 5})
    fp2 = reporter._generate_fingerprint("test-rule", "test.env", {"line": 5})

    assert fp1 == fp2

    fp3 = reporter._generate_fingerprint("test-rule", "test.env", {"line": 6})
    assert fp1 != fp3
