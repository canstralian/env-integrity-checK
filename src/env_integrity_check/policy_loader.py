import json
from pathlib import Path

def load_policy() -> dict:
    """Load built-in or custom policy definition."""
    default = {
        "errors": {"level": "error"},
        "warnings": {"level": "warning"},
        "secrets": {"level": "error"},
    }
    path = Path("policy.json")
    if path.exists():
        return json.loads(path.read_text())
    return default
