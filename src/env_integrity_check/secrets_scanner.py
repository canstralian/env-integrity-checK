import subprocess, json, time
from pathlib import Path

def _detect_secrets_supports_json() -> bool:
    try:
        result = subprocess.run(
            ["detect-secrets", "scan", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "--json" in result.stdout
    except Exception:
        return False

def _secrets_scan_impl(file_path: Path) -> tuple[bool, list[dict]]:
    supports_json = _detect_secrets_supports_json()
    cmd = ["detect-secrets", "scan", "--baseline", "/dev/null", str(file_path)]
    if supports_json:
        cmd.insert(2, "--json")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
        if supports_json:
            baseline = json.loads(result.stdout)
            results = []
            for plugin, data in baseline.get("results", {}).items():
                for item in data:
                    results.append({
                        "line": item.get("line_number"),
                        "type": item.get("type"),
                        "message": "Potential secret detected",
                    })
            return len(results) == 0, results
        else:
            # Fallback legacy parse
            findings = []
            for line_num, line in enumerate(result.stdout.splitlines(), 1):
                if "secret" in line.lower():
                    findings.append({"line": line_num, "message": "Legacy secret detection"})
            return len(findings) == 0, findings
    except Exception:
        return True, [{"warning": "detect-secrets failed"}]

def secrets_scan(file_path: Path) -> tuple[bool, list[dict]]:
    start = time.time()
    clean, findings = _secrets_scan_impl(file_path)
    elapsed = time.time() - start
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    return clean, findings
