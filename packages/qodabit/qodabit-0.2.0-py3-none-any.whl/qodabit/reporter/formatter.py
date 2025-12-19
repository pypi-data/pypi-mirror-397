"""Output formatter for terminal and JSON."""

import json
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel

console = Console()


def format_scan_results(issues: List[dict], score: int) -> None:
    """Format and print scan results to terminal."""
    # Score panel
    category = get_category(score)
    color = get_color(category)

    console.print(
        Panel(
            f"[bold {color}]Production-Ready Score: {score}%[/bold {color}]",
            border_style=color,
        )
    )

    # Issues by severity
    grouped = group_by_severity(issues)

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if severity not in grouped:
            continue

        emoji = {
            "CRITICAL": "[red]",
            "HIGH": "[orange1]",
            "MEDIUM": "[yellow]",
            "LOW": "[dim]",
        }
        console.print(
            f"\n{emoji[severity]} {severity} ({len(grouped[severity])})[/{emoji[severity].split('[')[1]}"
        )

        for issue in grouped[severity]:
            console.print(
                f"   {issue['id']}  {issue['message']:<30}  {issue['file']}:{issue['line']}"
            )


def format_json_output(data: Dict[str, Any]) -> str:
    """Format output as JSON for CI."""
    return json.dumps(data, indent=2)


def group_by_severity(issues: List[dict]) -> Dict[str, List[dict]]:
    """Group issues by severity."""
    grouped: Dict[str, List[dict]] = {}
    for issue in issues:
        severity = issue.get("severity", "LOW")
        if severity not in grouped:
            grouped[severity] = []
        grouped[severity].append(issue)
    return grouped


def get_category(score: int) -> str:
    """Get score category."""
    if score >= 90:
        return "PRODUCTION_READY"
    elif score >= 70:
        return "ALMOST_READY"
    elif score >= 50:
        return "NEEDS_WORK"
    return "NOT_READY"


def get_color(category: str) -> str:
    """Get color for category."""
    return {
        "PRODUCTION_READY": "green",
        "ALMOST_READY": "yellow",
        "NEEDS_WORK": "orange1",
        "NOT_READY": "red",
    }.get(category, "white")
