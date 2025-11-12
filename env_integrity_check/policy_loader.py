"""
Policy file loader and validator.
"""

from pathlib import Path
from typing import Any, Dict, List

import yaml


class PolicyLoader:
    """Load and validate policy files."""

    def __init__(self, policy_path: Path):
        """
        Initialize policy loader.

        Args:
            policy_path: Path to YAML policy file
        """
        self.policy_path = policy_path

    def load(self) -> Dict[str, Any]:
        """
        Load policy from YAML file.

        Returns:
            Policy dictionary

        Raises:
            ValueError: If policy file is invalid
        """
        try:
            with open(self.policy_path, "r") as f:
                policy = yaml.safe_load(f)

            if policy is None:
                raise ValueError("Policy file is empty")

            # Validate policy structure
            self._validate_policy(policy)

            return policy

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading policy: {e}")

    def _validate_policy(self, policy: Dict[str, Any]) -> None:
        """
        Validate policy structure.

        Args:
            policy: Policy dictionary to validate

        Raises:
            ValueError: If policy is invalid
        """
        # Check for valid sections
        valid_sections = {"required", "forbidden", "patterns", "metadata"}
        for section in policy.keys():
            if section not in valid_sections:
                raise ValueError(f"Invalid policy section: {section}")

        # Validate 'required' section
        if "required" in policy:
            if not isinstance(policy["required"], list):
                raise ValueError("'required' section must be a list")
            for item in policy["required"]:
                if not isinstance(item, str):
                    raise ValueError("Items in 'required' must be strings")

        # Validate 'forbidden' section
        if "forbidden" in policy:
            if not isinstance(policy["forbidden"], list):
                raise ValueError("'forbidden' section must be a list")
            for item in policy["forbidden"]:
                if not isinstance(item, str):
                    raise ValueError("Items in 'forbidden' must be strings")

        # Validate 'patterns' section
        if "patterns" in policy:
            if not isinstance(policy["patterns"], list):
                raise ValueError("'patterns' section must be a list")
            for pattern in policy["patterns"]:
                if not isinstance(pattern, dict):
                    raise ValueError("Items in 'patterns' must be dictionaries")
                if "regex" not in pattern:
                    raise ValueError("Pattern must have 'regex' field")
                if not isinstance(pattern["regex"], str):
                    raise ValueError("Pattern 'regex' must be a string")

                # Validate regex is compilable
                import re

                try:
                    re.compile(pattern["regex"])
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{pattern['regex']}': {e}")

    @staticmethod
    def create_example_policy(output_path: Path) -> None:
        """
        Create an example policy file.

        Args:
            output_path: Path where to create example policy
        """
        example_policy = {
            "metadata": {
                "name": "Example Environment Policy",
                "version": "1.0.0",
                "description": "Example policy for environment variable validation",
            },
            "required": [
                "APP_NAME",
                "APP_ENV",
                "DATABASE_URL",
            ],
            "forbidden": [
                "DEBUG",
                "UNSAFE_MODE",
            ],
            "patterns": [
                {
                    "regex": ".*_PROD_.*",
                    "action": "warn",
                    "message": "Production variables should not be in .env files",
                },
                {
                    "regex": "^TEST_.*",
                    "action": "warn",
                    "message": "Test variables detected",
                },
            ],
        }

        with open(output_path, "w") as f:
            yaml.dump(example_policy, f, default_flow_style=False, sort_keys=False)
