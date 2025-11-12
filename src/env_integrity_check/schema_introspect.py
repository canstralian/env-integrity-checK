from importlib import import_module
from pathlib import Path
from typing import Type
from pydantic import BaseModel, ValidationError
import json
from .policy_loader import load_policy

def load_model(schema_path: str) -> Type[BaseModel]:
    module_name, class_name = schema_path.split(":")
    mod = import_module(module_name)
    return getattr(mod, class_name)

def parse_env(file_path: Path) -> dict:
    env = {}
    for line in file_path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env

def validate_env(file_path: Path, schema_path: str) -> tuple[dict, dict]:
    """Validate environment file against Pydantic schema."""
    model = load_model(schema_path)
    env = parse_env(file_path)
    findings = {"errors": [], "warnings": []}

    try:
        model(**env)
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(l) for l in err["loc"])
            findings["errors"].append({
                "key": loc,
                "message": err["msg"],
                "type": err["type"],
            })

    # Placeholder detection (simple baseline)
    for key, val in env.items():
        if val.strip().upper() in ("TODO", "CHANGEME", "XXX", ""):
            findings["warnings"].append({
                "key": key,
                "message": "Contains placeholder or empty value.",
            })

    # Load default policy
    policy = load_policy()
    return findings, policy
