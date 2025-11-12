import json
from pathlib import Path
from .sanitizer import sanitize_for_sarif

SARIF_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"

def emit_sarif(findings: dict, file_path: Path, policy: dict) -> dict:
    """Produce deterministic SARIF report."""
    results = []
    for level, items in findings.items():
        for item in items:
            results.append({
                "ruleId": item.get("type", "ENV"),
                "level": level,
                "message": {"text": item["message"]},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": str(file_path), "uriBaseId": "%SRCROOT%"},
                        "region": {"startLine": item.get("line", 1),
                                   "snippet": {"text": sanitize_for_sarif(item.get("key", ""), item.get("message", ""), "ENV003")}}
                    }
                }]
            })

    results.sort(key=lambda r: (r["ruleId"], r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                                r["locations"][0]["physicalLocation"]["region"]["startLine"],
                                r["message"]["text"]))

    run = {
        "tool": {"driver": {"name": "env-integrity-check"}},
        "results": results,
    }

    return {"version": "2.1.0", "$schema": SARIF_SCHEMA_URI, "runs": [run]}
