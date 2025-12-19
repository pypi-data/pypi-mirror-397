"""Production-Ready Score calculator."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScoreResult:
    """Score calculation result."""

    score: int  # 0-100
    category: str  # PRODUCTION_READY, ALMOST_READY, NEEDS_WORK, NOT_READY
    delta: Optional[int]  # Change from previous scan


SEVERITY_PENALTIES = {
    "CRITICAL": 15,
    "HIGH": 8,
    "MEDIUM": 3,
    "LOW": 1,
}


def calculate_score(issues: List[dict]) -> ScoreResult:
    """Calculate Production-Ready Score from issues.

    Score starts at 100 and decreases based on issues:
    - CRITICAL: -15 points
    - HIGH: -8 points
    - MEDIUM: -3 points
    - LOW: -1 point
    """
    base = 100

    for issue in issues:
        severity = issue.get("severity", "LOW")
        penalty = SEVERITY_PENALTIES.get(severity, 1)
        base -= penalty

    score = max(0, base)

    # Determine category
    if score >= 90:
        category = "PRODUCTION_READY"
    elif score >= 70:
        category = "ALMOST_READY"
    elif score >= 50:
        category = "NEEDS_WORK"
    else:
        category = "NOT_READY"

    return ScoreResult(score=score, category=category, delta=None)


def get_score_emoji(category: str) -> str:
    """Get emoji for score category."""
    return {
        "PRODUCTION_READY": "[green]",
        "ALMOST_READY": "[yellow]",
        "NEEDS_WORK": "[orange1]",
        "NOT_READY": "[red]",
    }.get(category, "")
