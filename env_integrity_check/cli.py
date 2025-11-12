"""
CLI interface for env-integrity-check tool.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from .metrics import Metrics
from .policy_loader import PolicyLoader
from .sanitizer import Sanitizer
from .sarif_reporter import SARIFReporter
from .schema_introspect import SchemaIntrospector
from .secrets_scanner import SecretsScanner


@click.command()
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--schema",
    type=click.Path(exists=True, path_type=Path),
    help="Path to Pydantic schema module (Python file)",
)
@click.option(
    "--policy",
    type=click.Path(exists=True, path_type=Path),
    help="Path to policy YAML file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output SARIF report file (default: stdout)",
)
@click.option(
    "--sanitize/--no-sanitize",
    default=True,
    help="Sanitize sensitive values in output (default: enabled)",
)
@click.option(
    "--detect-secrets/--no-detect-secrets",
    default=True,
    help="Run detect-secrets scanner (default: enabled)",
)
@click.option(
    "--metrics/--no-metrics",
    default=False,
    help="Include metrics in output (default: disabled)",
)
@click.version_option()
def main(
    env_file: Path,
    schema: Optional[Path],
    policy: Optional[Path],
    output: Optional[Path],
    sanitize: bool,
    detect_secrets: bool,
    metrics: bool,
) -> None:
    """
    Validate .env files against Pydantic schemas and emit SARIF reports.

    ENV_FILE is the path to the .env file to validate.
    """
    try:
        # Initialize components
        metrics_collector = Metrics()
        sanitizer = Sanitizer() if sanitize else None
        results = []

        # Load .env file
        env_content = env_file.read_text()
        metrics_collector.record_file_size(len(env_content))

        # Parse .env file
        env_vars = parse_env_file(env_content)
        metrics_collector.record_env_var_count(len(env_vars))

        # Load policy if provided
        policy_rules = None
        if policy:
            policy_loader = PolicyLoader(policy)
            policy_rules = policy_loader.load()
            metrics_collector.record_policy_loaded()

        # Schema validation
        if schema:
            introspector = SchemaIntrospector(schema)
            schema_results = introspector.validate_env_vars(env_vars)
            results.extend(schema_results)
            metrics_collector.record_schema_violations(len(schema_results))

        # Secrets detection
        if detect_secrets:
            secrets_scanner = SecretsScanner()
            secrets_results = secrets_scanner.scan_env_file(env_file, env_vars)
            results.extend(secrets_results)
            metrics_collector.record_secrets_found(len(secrets_results))

        # Policy validation
        if policy_rules:
            policy_results = validate_policy(env_vars, policy_rules)
            results.extend(policy_results)
            metrics_collector.record_policy_violations(len(policy_results))

        # Sanitize results if enabled
        if sanitizer:
            results = [sanitizer.sanitize_result(r) for r in results]

        # Generate SARIF report
        reporter = SARIFReporter(
            tool_name="env-integrity-check",
            tool_version="0.1.0",
        )
        sarif_output = reporter.generate_report(
            results=results,
            source_file=str(env_file),
            metrics_data=metrics_collector.to_dict() if metrics else None,
        )

        # Output report
        if output:
            output.write_text(json.dumps(sarif_output, indent=2))
            click.echo(f"Report written to {output}", err=True)
        else:
            click.echo(json.dumps(sarif_output, indent=2))

        # Exit with error code if violations found
        if results:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)


def parse_env_file(content: str) -> dict:
    """Parse .env file content into a dictionary."""
    env_vars = {}
    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Parse KEY=VALUE
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env_vars[key] = {"value": value, "line": line_num}
    return env_vars


def validate_policy(env_vars: dict, policy_rules: dict) -> list:
    """Validate environment variables against policy rules."""
    results = []

    # Check required variables
    if "required" in policy_rules:
        for required_var in policy_rules["required"]:
            if required_var not in env_vars:
                results.append(
                    {
                        "rule_id": "missing-required-var",
                        "level": "error",
                        "message": f"Required environment variable '{required_var}' is missing",
                        "location": {"line": 1},
                    }
                )

    # Check forbidden variables
    if "forbidden" in policy_rules:
        for forbidden_var in policy_rules["forbidden"]:
            if forbidden_var in env_vars:
                results.append(
                    {
                        "rule_id": "forbidden-var",
                        "level": "error",
                        "message": f"Forbidden environment variable '{forbidden_var}' is present",
                        "location": {"line": env_vars[forbidden_var]["line"]},
                    }
                )

    # Check patterns
    if "patterns" in policy_rules:
        import re

        for pattern_rule in policy_rules["patterns"]:
            pattern = re.compile(pattern_rule["regex"])
            for var_name, var_data in env_vars.items():
                if pattern.match(var_name):
                    if pattern_rule.get("action") == "warn":
                        results.append(
                            {
                                "rule_id": "pattern-match",
                                "level": "warning",
                                "message": pattern_rule.get(
                                    "message", f"Variable '{var_name}' matches pattern"
                                ),
                                "location": {"line": var_data["line"]},
                            }
                        )

    return results


if __name__ == "__main__":
    main()
