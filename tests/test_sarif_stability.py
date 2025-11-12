import json
from pathlib import Path
from env_integrity_check.sarif_reporter import emit_sarif

def test_deterministic_output(tmp_path):
    findings = {
        "warnings": [{"key": "DATABASE_URL", "message": "Contains placeholder", "line": 1}],
        "errors": []
    }
    sarif1 = emit_sarif(findings, Path(".env.example"), {})
    sarif2 = emit_sarif(findings, Path(".env.example"), {})
    assert json.dumps(sarif1, sort_keys=True) == json.dumps(sarif2, sort_keys=True)
