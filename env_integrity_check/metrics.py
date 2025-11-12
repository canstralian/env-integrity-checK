"""
Metrics collection and reporting.
"""

from datetime import datetime, timezone
from typing import Any, Dict


class Metrics:
    """Collect and report metrics about validation run."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_size_bytes": 0,
            "env_var_count": 0,
            "schema_violations": 0,
            "secrets_found": 0,
            "policy_violations": 0,
            "policy_loaded": False,
        }

    def record_file_size(self, size: int) -> None:
        """Record size of analyzed file."""
        self.metrics["file_size_bytes"] = size

    def record_env_var_count(self, count: int) -> None:
        """Record number of environment variables."""
        self.metrics["env_var_count"] = count

    def record_schema_violations(self, count: int) -> None:
        """Record number of schema validation violations."""
        self.metrics["schema_violations"] = count

    def record_secrets_found(self, count: int) -> None:
        """Record number of secrets detected."""
        self.metrics["secrets_found"] = count

    def record_policy_violations(self, count: int) -> None:
        """Record number of policy violations."""
        self.metrics["policy_violations"] = count

    def record_policy_loaded(self) -> None:
        """Record that a policy was loaded."""
        self.metrics["policy_loaded"] = True

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return self.metrics.copy()

    def get_total_violations(self) -> int:
        """Get total number of violations across all categories."""
        return (
            self.metrics["schema_violations"]
            + self.metrics["secrets_found"]
            + self.metrics["policy_violations"]
        )

    def __str__(self) -> str:
        """String representation of metrics."""
        return (
            f"Metrics:\n"
            f"  File size: {self.metrics['file_size_bytes']} bytes\n"
            f"  Environment variables: {self.metrics['env_var_count']}\n"
            f"  Schema violations: {self.metrics['schema_violations']}\n"
            f"  Secrets found: {self.metrics['secrets_found']}\n"
            f"  Policy violations: {self.metrics['policy_violations']}\n"
            f"  Total violations: {self.get_total_violations()}\n"
        )
