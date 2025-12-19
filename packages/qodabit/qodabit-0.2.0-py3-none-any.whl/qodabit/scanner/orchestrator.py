"""Scanner orchestrator - runs all tools in parallel."""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from qodabit.scanner.gitleaks import run_gitleaks
from qodabit.scanner.semgrep import run_semgrep


def deduplicate_issues(issues: List["Issue"]) -> List["Issue"]:
    """Remove duplicate issues detected by multiple tools.

    Deduplication key: (file basename, line number)
    When duplicates found, prefer the higher severity one.
    """
    seen: Dict[Tuple[str, int], "Issue"] = {}
    severity_priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    for issue in issues:
        # Use basename to normalize paths
        file_key = Path(issue.file).name
        key = (file_key, issue.line)

        if key not in seen:
            seen[key] = issue
        else:
            # Keep the one with higher severity (lower number = higher priority)
            existing = seen[key]
            existing_priority = severity_priority.get(existing.severity, 4)
            new_priority = severity_priority.get(issue.severity, 4)

            if new_priority < existing_priority:
                seen[key] = issue

    return list(seen.values())


@dataclass
class Issue:
    """Unified issue format."""

    id: str
    tool: str
    rule: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    file: str
    line: int
    message: str
    snippet: str


@dataclass
class ScanResult:
    """Aggregated scan results."""

    issues: List[Issue]
    tools_run: List[str]
    duration_ms: int
    errors: List[str] = field(default_factory=list)


async def scan_project(path: str = ".") -> ScanResult:
    """Run all scanners in parallel and aggregate results.

    Args:
        path: Directory to scan (default: current directory)

    Returns:
        ScanResult with aggregated issues from all tools
    """
    start_time = time.time()

    # Run scanners in parallel
    results = await asyncio.gather(
        run_semgrep(path),
        run_gitleaks(path),
        return_exceptions=True,
    )

    # Aggregate results
    all_issues: List[Issue] = []
    tools_run: List[str] = []
    errors: List[str] = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue

        if not result:
            continue

        tool_name = result.get("tool", "unknown")
        tools_run.append(tool_name)

        # Check for tool-specific errors
        if "error" in result:
            errors.append(f"{tool_name}: {result['error']}")

        # Convert dict issues to Issue objects
        for issue_dict in result.get("issues", []):
            all_issues.append(
                Issue(
                    id=issue_dict.get("id", "UNKNOWN"),
                    tool=issue_dict.get("tool", tool_name),
                    rule=issue_dict.get("rule", "unknown"),
                    severity=issue_dict.get("severity", "LOW"),
                    file=issue_dict.get("file", "unknown"),
                    line=issue_dict.get("line", 0),
                    message=issue_dict.get("message", ""),
                    snippet=issue_dict.get("snippet", ""),
                )
            )

    # Deduplicate issues (same file+line from different tools)
    all_issues = deduplicate_issues(all_issues)

    # Sort by severity (CRITICAL first, then HIGH, MEDIUM, LOW)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_issues.sort(key=lambda x: severity_order.get(x.severity, 4))

    duration_ms = int((time.time() - start_time) * 1000)

    return ScanResult(
        issues=all_issues,
        tools_run=tools_run,
        duration_ms=duration_ms,
        errors=errors,
    )


def count_by_severity(issues: List[Issue]) -> Dict[str, int]:
    """Count issues by severity level."""
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for issue in issues:
        if issue.severity in counts:
            counts[issue.severity] += 1
    return counts
