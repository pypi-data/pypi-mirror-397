"""Gitleaks secrets scanner."""

import asyncio
import json
import shutil
import tempfile
from typing import Any, Dict

from qodabit.scanner.semgrep import generate_issue_id


async def run_gitleaks(path: str = ".") -> Dict[str, Any]:
    """Run Gitleaks secrets scan.

    Returns unified format:
    {
        "tool": "gitleaks",
        "issues": [
            {
                "id": "SEC-001",
                "rule": "aws-access-key",
                "severity": "CRITICAL",
                "file": "config.py",
                "line": 12,
                "message": "AWS Access Key detected",
                "snippet": "..."
            }
        ]
    }
    """
    # Check if gitleaks is available
    gitleaks_cmd = shutil.which("gitleaks")
    if not gitleaks_cmd:
        return {
            "tool": "gitleaks",
            "issues": [],
            "error": "gitleaks not found. Install with: brew install gitleaks",
        }

    try:
        # Create temp file for JSON report
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_path = f.name

        # Run gitleaks
        proc = await asyncio.create_subprocess_exec(
            gitleaks_cmd,
            "detect",
            "--source",
            path,
            "--report-format",
            "json",
            "--report-path",
            report_path,
            "--no-git",  # Scan files, not git history
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        # Read report
        try:
            with open(report_path, "r") as f:
                content = f.read()
                if not content.strip():
                    return {"tool": "gitleaks", "issues": []}
                results = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tool": "gitleaks", "issues": []}

        # Convert to unified format
        issues = []
        if results:
            for result in results:
                file_path = result.get("File", "unknown")
                line = result.get("StartLine", 0)
                rule = result.get("RuleID", "unknown")
                issues.append(
                    {
                        "id": generate_issue_id(file_path, line, rule),
                        "tool": "gitleaks",
                        "rule": rule,
                        "severity": "CRITICAL",  # All secrets are critical
                        "file": file_path,
                        "line": line,
                        "message": f"Secret detected: {result.get('Description', 'Hardcoded secret')}",
                        "snippet": result.get("Match", "")[:100],  # Truncate for safety
                    }
                )

        return {"tool": "gitleaks", "issues": issues}

    except Exception as e:
        return {"tool": "gitleaks", "issues": [], "error": str(e)}
