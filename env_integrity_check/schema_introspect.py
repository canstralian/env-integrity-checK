"""
Schema introspection for Pydantic models.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ValidationError


class SchemaIntrospector:
    """Introspect and validate against Pydantic schemas."""

    def __init__(self, schema_path: Path):
        """
        Initialize schema introspector.

        Args:
            schema_path: Path to Python file containing Pydantic model(s)
        """
        self.schema_path = schema_path
        self.model_class = self._load_schema()

    def _load_schema(self) -> type[BaseModel]:
        """Load Pydantic model from schema file."""
        # Load module from file
        spec = importlib.util.spec_from_file_location("schema_module", self.schema_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load schema from {self.schema_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["schema_module"] = module
        spec.loader.exec_module(module)

        # Find first BaseModel subclass
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseModel)
                and attr is not BaseModel
            ):
                return attr

        raise ValueError(f"No Pydantic BaseModel found in {self.schema_path}")

    def validate_env_vars(self, env_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate environment variables against schema.

        Args:
            env_vars: Dictionary of environment variables with metadata

        Returns:
            List of validation results (violations)
        """
        results = []

        # Extract just the values for validation
        env_values = {key: data["value"] for key, data in env_vars.items()}

        try:
            # Try to validate
            self.model_class(**env_values)
        except ValidationError as e:
            # Convert Pydantic errors to our format
            for error in e.errors():
                field = error["loc"][0] if error["loc"] else "unknown"
                line = env_vars.get(field, {}).get("line", 1)

                results.append(
                    {
                        "rule_id": "schema-validation",
                        "level": "error",
                        "message": f"{field}: {error['msg']}",
                        "location": {"line": line},
                        "details": {
                            "field": field,
                            "error_type": error["type"],
                            "input": error.get("input"),
                        },
                    }
                )

        # Check for required fields that are missing
        if hasattr(self.model_class, "model_fields"):
            # Pydantic v2
            model_fields = self.model_class.model_fields
            for field_name, field_info in model_fields.items():
                if field_info.is_required() and field_name not in env_vars:
                    results.append(
                        {
                            "rule_id": "missing-required-field",
                            "level": "error",
                            "message": f"Required field '{field_name}' is missing",
                            "location": {"line": 1},
                            "details": {
                                "field": field_name,
                            },
                        }
                    )
        else:
            # Pydantic v1 fallback
            for field_name, field in self.model_class.__fields__.items():
                if field.required and field_name not in env_vars:
                    results.append(
                        {
                            "rule_id": "missing-required-field",
                            "level": "error",
                            "message": f"Required field '{field_name}' is missing",
                            "location": {"line": 1},
                            "details": {
                                "field": field_name,
                            },
                        }
                    )

        return results

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema metadata information."""
        info = {
            "model_name": self.model_class.__name__,
            "fields": {},
        }

        if hasattr(self.model_class, "model_fields"):
            # Pydantic v2
            for field_name, field_info in self.model_class.model_fields.items():
                info["fields"][field_name] = {
                    "required": field_info.is_required(),
                    "type": str(field_info.annotation),
                }
        else:
            # Pydantic v1
            for field_name, field in self.model_class.__fields__.items():
                info["fields"][field_name] = {
                    "required": field.required,
                    "type": str(field.type_),
                }

        return info
