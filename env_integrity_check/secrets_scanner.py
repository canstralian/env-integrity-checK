"""
Secrets detection using detect-secrets library.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List

from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings


class SecretsScanner:
    """Scan for secrets using detect-secrets."""

    def __init__(self):
        """Initialize secrets scanner."""
        self.settings = default_settings

    def scan_env_file(
        self, file_path: Path, env_vars: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Scan environment file for secrets.

        Args:
            file_path: Path to the .env file
            env_vars: Parsed environment variables with metadata

        Returns:
            List of detected secrets as results
        """
        results = []

        try:
            # Create a secrets collection
            secrets = SecretsCollection()

            # Scan the file
            with open(file_path, "r") as f:
                secrets.scan_file(str(file_path))

            # Process detected secrets
            for filename, file_secrets in secrets.data.items():
                for secret in file_secrets:
                    # Find which env var this secret belongs to
                    line_num = secret.line_number
                    var_name = self._find_var_at_line(env_vars, line_num)

                    results.append(
                        {
                            "rule_id": "secret-detected",
                            "level": "error",
                            "message": f"Potential {secret.type} detected in {var_name or 'environment file'}",
                            "location": {
                                "line": line_num,
                            },
                            "details": {
                                "secret_type": secret.type,
                                "variable": var_name,
                            },
                        }
                    )

        except Exception as e:
            # If detect-secrets fails, log but don't fail the entire scan
            results.append(
                {
                    "rule_id": "secrets-scan-error",
                    "level": "warning",
                    "message": f"Secrets scanning encountered an error: {str(e)}",
                    "location": {"line": 1},
                }
            )

        return results

    def scan_env_content(self, env_content: str) -> List[Dict[str, Any]]:
        """
        Scan environment content for secrets.

        Args:
            env_content: Content of .env file as string

        Returns:
            List of detected secrets as results
        """
        results = []

        try:
            # Write content to temporary file for scanning
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".env", delete=False
            ) as tmp_file:
                tmp_file.write(env_content)
                tmp_path = Path(tmp_file.name)

            # Scan temporary file
            secrets = SecretsCollection()
            secrets.scan_file(str(tmp_path))

            # Process detected secrets
            for filename, file_secrets in secrets.data.items():
                for secret in file_secrets:
                    results.append(
                        {
                            "rule_id": "secret-detected",
                            "level": "error",
                            "message": f"Potential {secret.type} detected",
                            "location": {
                                "line": secret.line_number,
                            },
                            "details": {
                                "secret_type": secret.type,
                            },
                        }
                    )

            # Clean up temporary file
            tmp_path.unlink()

        except Exception as e:
            results.append(
                {
                    "rule_id": "secrets-scan-error",
                    "level": "warning",
                    "message": f"Secrets scanning encountered an error: {str(e)}",
                    "location": {"line": 1},
                }
            )

        return results

    def _find_var_at_line(self, env_vars: Dict[str, Any], line_num: int) -> str:
        """Find environment variable name at given line number."""
        for var_name, var_data in env_vars.items():
            if var_data.get("line") == line_num:
                return var_name
        return ""
