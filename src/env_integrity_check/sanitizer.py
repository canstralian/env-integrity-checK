from pathlib import Path

SENSITIVE_KEYS = frozenset([
    "password", "passwd", "pwd", "secret", "token", "key", "api_key",
    "auth", "credential", "private", "cert", "certificate"
])

def is_sensitive_key(key: str) -> bool:
    k = key.lower()
    return any(s in k for s in SENSITIVE_KEYS)

def _sanitize_snippet(value: str, rule_id: str) -> str:
    if rule_id == "SEC001":
        return "[REDACTED]"
    if len(value) > 100:
        return value[:100] + "..."
    return value

def sanitize_for_sarif(key: str, value: str, rule_id: str) -> str:
    if is_sensitive_key(key):
        return "[REDACTED]"
    return _sanitize_snippet(value, rule_id)
