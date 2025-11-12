"""
Tests for schema introspection module.
"""

import pytest
from pathlib import Path
from pydantic import BaseModel

from env_integrity_check.schema_introspect import SchemaIntrospector


def test_schema_introspector_load_schema(tmp_path):
    """Test loading Pydantic schema."""
    schema_file = tmp_path / "schema.py"
    schema_file.write_text(
        """
from pydantic import BaseModel

class AppConfig(BaseModel):
    app_name: str
    debug: bool = False
"""
    )

    introspector = SchemaIntrospector(schema_file)

    assert introspector.model_class is not None
    assert introspector.model_class.__name__ == "AppConfig"


def test_schema_introspector_validate_env_vars(tmp_path):
    """Test validation of environment variables."""
    schema_file = tmp_path / "schema.py"
    schema_file.write_text(
        """
from pydantic import BaseModel

class AppConfig(BaseModel):
    app_name: str
    port: int
"""
    )

    introspector = SchemaIntrospector(schema_file)
    env_vars = {
        "app_name": {"value": "myapp", "line": 1},
        "port": {"value": "not_a_number", "line": 2},
    }

    results = introspector.validate_env_vars(env_vars)

    assert len(results) > 0
    # Should have validation error for port
    assert any("port" in r["message"].lower() for r in results)


def test_schema_introspector_missing_required(tmp_path):
    """Test detection of missing required fields."""
    schema_file = tmp_path / "schema.py"
    schema_file.write_text(
        """
from pydantic import BaseModel

class AppConfig(BaseModel):
    app_name: str
    database_url: str
"""
    )

    introspector = SchemaIntrospector(schema_file)
    env_vars = {
        "app_name": {"value": "myapp", "line": 1},
    }

    results = introspector.validate_env_vars(env_vars)

    assert len(results) > 0
    # Should have error for missing database_url
    assert any("database_url" in r["message"].lower() for r in results)


def test_schema_introspector_get_schema_info(tmp_path):
    """Test getting schema info."""
    schema_file = tmp_path / "schema.py"
    schema_file.write_text(
        """
from pydantic import BaseModel

class AppConfig(BaseModel):
    app_name: str
    port: int = 8000
"""
    )

    introspector = SchemaIntrospector(schema_file)
    info = introspector.get_schema_info()

    assert info["model_name"] == "AppConfig"
    assert "fields" in info
    assert "app_name" in info["fields"]
    assert "port" in info["fields"]


def test_schema_introspector_no_model(tmp_path):
    """Test error when no Pydantic model found."""
    schema_file = tmp_path / "schema.py"
    schema_file.write_text(
        """
# No Pydantic model here
def some_function():
    pass
"""
    )

    with pytest.raises(ValueError, match="No Pydantic BaseModel found"):
        SchemaIntrospector(schema_file)
