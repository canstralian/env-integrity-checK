"""
SARIF 2.1.0 report generator for deterministic CI/CD integration.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class SARIFReporter:
    """Generate SARIF 2.1.0 compliant reports."""

    def __init__(self, tool_name: str, tool_version: str):
        """
        Initialize SARIF reporter.

        Args:
            tool_name: Name of the analysis tool
            tool_version: Version of the analysis tool
        """
        self.tool_name = tool_name
        self.tool_version = tool_version

    def generate_report(
        self,
        results: List[Dict[str, Any]],
        source_file: str,
        metrics_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate SARIF 2.1.0 report.

        Args:
            results: List of validation/scanning results
            source_file: Path to the analyzed file
            metrics_data: Optional metrics to include in report

        Returns:
            SARIF report as dictionary
        """
        # Build rules dictionary
        rules = self._extract_rules(results)

        # Convert results to SARIF format
        sarif_results = []
        for result in results:
            sarif_result = self._convert_to_sarif_result(result, source_file)
            sarif_results.append(sarif_result)

        # Sort results for deterministic output
        sarif_results.sort(key=lambda x: (x["ruleId"], x["locations"][0]["physicalLocation"]["region"]["startLine"]))

        # Build SARIF structure
        sarif_report = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "version": self.tool_version,
                            "informationUri": "https://github.com/canstralian/env-integrity-checK",
                            "rules": rules,
                        }
                    },
                    "results": sarif_results,
                    "columnKind": "utf16CodeUnits",
                }
            ],
        }

        # Add metrics as properties if provided
        if metrics_data:
            sarif_report["runs"][0]["properties"] = {
                "metrics": metrics_data
            }

        return sarif_report

    def _extract_rules(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique rules from results."""
        rules_dict = {}

        for result in results:
            rule_id = result.get("rule_id", "unknown")
            if rule_id not in rules_dict:
                rules_dict[rule_id] = {
                    "id": rule_id,
                    "name": self._rule_id_to_name(rule_id),
                    "shortDescription": {
                        "text": self._get_rule_description(rule_id)
                    },
                    "help": {
                        "text": self._get_rule_help(rule_id)
                    },
                    "defaultConfiguration": {
                        "level": self._map_level(result.get("level", "warning"))
                    },
                }

        # Sort rules by ID for deterministic output
        return sorted(rules_dict.values(), key=lambda x: x["id"])

    def _convert_to_sarif_result(
        self, result: Dict[str, Any], source_file: str
    ) -> Dict[str, Any]:
        """Convert internal result format to SARIF result."""
        rule_id = result.get("rule_id", "unknown")
        level = self._map_level(result.get("level", "warning"))
        message = result.get("message", "Validation error")
        location = result.get("location", {})

        sarif_result = {
            "ruleId": rule_id,
            "level": level,
            "message": {"text": message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": source_file,
                        },
                        "region": {
                            "startLine": location.get("line", 1),
                            "startColumn": location.get("column", 1),
                        },
                    }
                }
            ],
        }

        # Add fingerprint for deterministic matching
        sarif_result["fingerprints"] = {
            "primary": self._generate_fingerprint(rule_id, source_file, location)
        }

        # Add additional properties if present
        if "details" in result:
            sarif_result["properties"] = result["details"]

        return sarif_result

    def _map_level(self, level: str) -> str:
        """Map internal level to SARIF level."""
        level_map = {
            "error": "error",
            "warning": "warning",
            "info": "note",
            "note": "note",
        }
        return level_map.get(level.lower(), "warning")

    def _rule_id_to_name(self, rule_id: str) -> str:
        """Convert rule ID to human-readable name."""
        return rule_id.replace("-", " ").replace("_", " ").title()

    def _get_rule_description(self, rule_id: str) -> str:
        """Get short description for rule."""
        descriptions = {
            "schema-validation": "Schema validation error",
            "missing-required-field": "Required field is missing",
            "missing-required-var": "Required environment variable is missing",
            "forbidden-var": "Forbidden environment variable detected",
            "pattern-match": "Environment variable matches warning pattern",
            "secret-detected": "Potential secret detected in environment file",
        }
        return descriptions.get(rule_id, f"Rule {rule_id}")

    def _get_rule_help(self, rule_id: str) -> str:
        """Get help text for rule."""
        help_texts = {
            "schema-validation": "Environment variable does not match expected schema type or format.",
            "missing-required-field": "A required field defined in the schema is not present in the environment file.",
            "missing-required-var": "A required environment variable specified in policy is missing.",
            "forbidden-var": "An environment variable that is forbidden by policy is present.",
            "pattern-match": "Environment variable name matches a pattern defined in policy.",
            "secret-detected": "Potential secret or sensitive credential detected by secrets scanner.",
        }
        return help_texts.get(rule_id, f"Validation rule: {rule_id}")

    def _generate_fingerprint(
        self, rule_id: str, file_path: str, location: Dict[str, Any]
    ) -> str:
        """Generate deterministic fingerprint for result."""
        # Create a stable identifier based on rule, file, and location
        fingerprint_data = f"{rule_id}:{file_path}:{location.get('line', 1)}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
