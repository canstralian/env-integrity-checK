"""
Sanitizer for sensitive values in output.
"""

import re
from typing import Any, Dict, List


class Sanitizer:
    """Sanitize sensitive values in validation results."""

    # Patterns that indicate sensitive data
    SENSITIVE_PATTERNS = [
        r"password",
        r"secret",
        r"token",
        r"key",
        r"api[_-]?key",
        r"auth",
        r"credential",
        r"private",
        r"passphrase",
    ]

    def __init__(self, redaction_text: str = "***REDACTED***"):
        """
        Initialize sanitizer.

        Args:
            redaction_text: Text to use for redacted values
        """
        self.redaction_text = redaction_text
        self.sensitive_pattern = re.compile(
            "|".join(self.SENSITIVE_PATTERNS), re.IGNORECASE
        )

    def sanitize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a single result.

        Args:
            result: Result dictionary to sanitize

        Returns:
            Sanitized result
        """
        sanitized = result.copy()

        # Sanitize message
        if "message" in sanitized:
            sanitized["message"] = self._sanitize_text(sanitized["message"])

        # Sanitize details
        if "details" in sanitized:
            sanitized["details"] = self._sanitize_dict(sanitized["details"])

        return sanitized

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text that may contain sensitive values."""
        # Look for patterns like KEY=value or "value"
        # Redact values that appear to be sensitive
        
        # Pattern: KEY=<value>
        text = re.sub(
            r'(\b(?:' + '|'.join(self.SENSITIVE_PATTERNS) + r')[^=\s]*)\s*=\s*["\']?([^"\'\s,;]+)["\']?',
            lambda m: f"{m.group(1)}={self.redaction_text}",
            text,
            flags=re.IGNORECASE
        )
        
        # Pattern: "sensitive_key": "value"
        text = re.sub(
            r'(["\'](?:' + '|'.join(self.SENSITIVE_PATTERNS) + r')[^"\']*["\']\s*:\s*)["\']([^"\']+)["\']',
            lambda m: f"{m.group(1)}\"{self.redaction_text}\"",
            text,
            flags=re.IGNORECASE
        )

        return text

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            # Check if key indicates sensitive data
            if self._is_sensitive_key(key):
                if isinstance(value, str) and value:
                    sanitized[key] = self.redaction_text
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self.redaction_text
                else:
                    sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_text(value)
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Recursively sanitize list values."""
        sanitized = []
        for item in data:
            if isinstance(item, dict):
                sanitized.append(self._sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self._sanitize_list(item))
            elif isinstance(item, str):
                sanitized.append(self._sanitize_text(item))
            else:
                sanitized.append(item)
        return sanitized

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key name indicates sensitive data."""
        return bool(self.sensitive_pattern.search(key))

    def sanitize_env_vars(self, env_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize environment variables dictionary.

        Args:
            env_vars: Dictionary of environment variables

        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in env_vars.items():
            if self._is_sensitive_key(key):
                if isinstance(value, dict) and "value" in value:
                    sanitized[key] = {**value, "value": self.redaction_text}
                else:
                    sanitized[key] = self.redaction_text
            else:
                sanitized[key] = value
        return sanitized
