"""
env-integrity-check
-------------------
A deterministic environment validation tool that combines Pydantic schema
introspection, secrets scanning, and SARIF reporting.
"""

from .version import __version__

__all__ = ["__version__"]
