"""Configuration loader."""

from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG = {
    "version": "2.0",
    "tools": {
        "semgrep": {
            "enabled": True,
            "config": "p/owasp-top-ten",
        },
        "gitleaks": {
            "enabled": True,
        },
        "radon": {
            "enabled": True,
            "thresholds": {
                "cyclomatic_max": 10,
            },
        },
        "pip_audit": {
            "enabled": True,
        },
    },
    "gates": {
        "pr": {
            "critical": 0,
            "high": 0,
            "secrets": 0,
            "score_min": 80,
        },
    },
}


def load_config(path: str = ".") -> Dict[str, Any]:
    """Load configuration from qodabit.yaml and .env."""
    # Load .env
    load_dotenv()

    # Load qodabit.yaml if exists
    config_path = Path(path) / "qodabit.yaml"
    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f)
            return {**DEFAULT_CONFIG, **user_config}

    return DEFAULT_CONFIG


def create_default_config(path: str = ".") -> None:
    """Create default qodabit.yaml file."""
    config_path = Path(path) / "qodabit.yaml"

    # Create parent directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    content = """# QodaBit Configuration
version: "2.0"

tools:
  semgrep:
    enabled: true
    config: "p/owasp-top-ten"
  gitleaks:
    enabled: true
  radon:
    enabled: true
    thresholds:
      cyclomatic_max: 10
  pip_audit:
    enabled: true

gates:
  pr:
    critical: 0      # FAIL if > 0
    high: 0          # FAIL if > 0
    secrets: 0       # FAIL if > 0
    score_min: 80    # FAIL if score < 80
"""

    with open(config_path, "w") as f:
        f.write(content)
