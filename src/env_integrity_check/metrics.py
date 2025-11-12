import os
from pathlib import Path

def emit_metrics(findings: dict, policy: dict, duration_ms: float):
    """Emit Prometheus text metrics if enabled."""
    if not os.getenv("ENV_INTEGRITY_METRICS_ENABLED"):
        return

    lines = [f"env_integrity_scan_duration_ms {duration_ms:.2f}"]
    for section, items in findings.items():
        level = policy.get(section, {}).get("level", "note")
        lines.append(f'env_integrity_findings{{section="{section}",level="{level}"}} {len(items)}')

    metrics_file = Path(os.getenv("ENV_INTEGRITY_METRICS_FILE", "/tmp/env_integrity.prom"))
    metrics_file.write_text("\n".join(lines) + "\n")
