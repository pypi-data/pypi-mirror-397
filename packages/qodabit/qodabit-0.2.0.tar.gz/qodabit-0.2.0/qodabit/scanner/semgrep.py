"""Semgrep SAST scanner."""

import asyncio
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def generate_issue_id(file: str, line: int, rule: str) -> str:
    """Generate deterministic issue ID based on file, line, and rule.

    Same issue = same ID across multiple runs.
    """
    # Normalize file path (use basename to avoid path differences)
    file_normalized = Path(file).name
    key = f"{file_normalized}:{line}:{rule}"
    hash_value = hashlib.md5(key.encode()).hexdigest()[:8]
    return f"SEC-{hash_value}"


def find_semgrep() -> Optional[str]:
    """Find semgrep/pysemgrep executable."""
    # First try shutil.which
    cmd = shutil.which("pysemgrep") or shutil.which("semgrep")
    if cmd:
        return cmd

    # Check common Python user install locations
    user_bin = (
        Path(sys.prefix).parent
        / "Python"
        / f"{sys.version_info.major}.{sys.version_info.minor}"
        / "bin"
    )
    for name in ["pysemgrep", "semgrep"]:
        candidate = user_bin / name
        if candidate.exists():
            return str(candidate)

    # Check ~/Library/Python/X.Y/bin (macOS)
    home = Path.home()
    for ver in ["3.9", "3.10", "3.11", "3.12"]:
        candidate = home / "Library" / "Python" / ver / "bin" / "pysemgrep"
        if candidate.exists():
            return str(candidate)

    # Check ~/.local/bin (Linux)
    candidate = home / ".local" / "bin" / "pysemgrep"
    if candidate.exists():
        return str(candidate)

    return None


async def run_semgrep(path: str = ".") -> Dict[str, Any]:
    """Run Semgrep SAST scan.

    Returns unified format:
    {
        "tool": "semgrep",
        "issues": [
            {
                "id": "SEC-001",
                "rule": "python.lang.security.audit.dangerous-system-call",
                "severity": "HIGH",
                "file": "src/utils.py",
                "line": 45,
                "message": "...",
                "snippet": "..."
            }
        ]
    }
    """
    # Check if semgrep is available
    semgrep_cmd = find_semgrep()
    if not semgrep_cmd:
        return {
            "tool": "semgrep",
            "issues": [],
            "error": "semgrep not found. Install with: pip install semgrep",
        }

    try:
        # Run semgrep with auto config (best coverage)
        proc = await asyncio.create_subprocess_exec(
            semgrep_cmd,
            "--config",
            "auto",
            "--json",
            "--quiet",
            path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if not stdout:
            return {"tool": "semgrep", "issues": []}

        # Parse JSON output
        data = json.loads(stdout.decode())
        results = data.get("results", [])

        # Convert to unified format
        issues = []
        for result in results:
            file_path = result.get("path", "unknown")
            line = result.get("start", {}).get("line", 0)
            rule = result.get("check_id", "unknown")
            severity = map_semgrep_severity(
                result.get("extra", {}).get("severity", "WARNING")
            )
            issues.append(
                {
                    "id": generate_issue_id(file_path, line, rule),
                    "tool": "semgrep",
                    "rule": rule,
                    "severity": severity,
                    "file": file_path,
                    "line": line,
                    "message": result.get("extra", {}).get(
                        "message", "Security issue detected"
                    ),
                    "snippet": result.get("extra", {}).get("lines", ""),
                }
            )

        return {"tool": "semgrep", "issues": issues}

    except json.JSONDecodeError:
        return {
            "tool": "semgrep",
            "issues": [],
            "error": "Failed to parse semgrep output",
        }
    except Exception as e:
        return {"tool": "semgrep", "issues": [], "error": str(e)}


def map_semgrep_severity(severity: str) -> str:
    """Map Semgrep severity to unified severity."""
    mapping = {
        "ERROR": "CRITICAL",
        "WARNING": "HIGH",
        "INFO": "MEDIUM",
    }
    return mapping.get(severity.upper(), "LOW")
