#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entrypoint for env-integrity-check
--------------------------------------
Validates environment files against Pydantic schemas, detects secrets,
and emits deterministic SARIF or JSON reports.
"""

import click
import json
import time
from pathlib import Path
from .schema_introspect import validate_env
from .secrets_scanner import secrets_scan as run_secrets_scan
from .sarif_reporter import emit_sarif
from .policy_loader import load_policy
from .metrics import emit_metrics


@click.group()
def cli():
    """Environment integrity validation tool."""
    pass


@cli.command("audit")
@click.option("--example", type=click.Path(exists=True), required=True,
              help="Path to example .env file to audit.")
@click.option("--schema", type=str, required=True,
              help="Python path to Pydantic model (e.g. myapp.config:Settings).")
@click.option("--report", type=click.Choice(["json", "sarif"]), default="sarif",
              help="Output report format.")
@click.option("--out", type=click.Path(), default="audit.sarif.json",
              help="Output file path.")
@click.option("--fail-on", default="error,warning",
              help="Comma-separated severities to fail on.")
@click.option("--secrets-scan/--no-secrets-scan", default=True,
              help="Run detect-secrets scan (slow).")
def audit(example, schema, report, out, fail_on, secrets_scan):
    """Audit environment configuration for compliance."""
    start_time = time.time()

    file_path = Path(example)
    findings, policy = validate_env(file_path, schema)

    if secrets_scan:
        _, secrets = run_secrets_scan(file_path)
        findings["secrets"] = secrets

    if report == "sarif":
        sarif_doc = emit_sarif(findings, file_path, policy)
        Path(out).write_text(json.dumps(sarif_doc, indent=2))
        click.echo(f"SARIF report written to {out}")
    else:
        Path(out).write_text(json.dumps(findings, indent=2))
        click.echo(f"JSON report written to {out}")

    duration_ms = (time.time() - start_time) * 1000
    emit_metrics(findings, policy, duration_ms)

    fail_levels = set(x.strip() for x in fail_on.split(","))
    has_error = any(k in fail_levels and len(v) > 0 for k, v in findings.items())
    if has_error:
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
