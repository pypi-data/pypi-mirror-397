"""Gate evaluator - deterministic PASS/FAIL for CI."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GateResult:
    """Gate evaluation result."""

    passed: bool
    failed_gates: List[str]
    details: Dict[str, dict]


def evaluate_gates(
    issues: List[dict],
    score: int,
    gate_config: dict,
) -> GateResult:
    """Evaluate gates based on issues and score.

    Gates are 100% deterministic - no AI involved.

    Example gate_config:
    {
        "critical": 0,     # FAIL if > 0 critical issues
        "high": 0,         # FAIL if > 0 high issues
        "secrets": 0,      # FAIL if > 0 secrets
        "score_min": 80,   # FAIL if score < 80
    }
    """
    failed_gates = []
    details = {}

    # Count issues by severity
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "secrets": 0}
    for issue in issues:
        severity = issue.get("severity", "LOW")
        counts[severity] = counts.get(severity, 0) + 1
        if issue.get("tool") == "gitleaks":
            counts["secrets"] += 1

    # Check each gate
    if "critical" in gate_config:
        threshold = gate_config["critical"]
        actual = counts["CRITICAL"]
        passed = actual <= threshold
        details["critical"] = {
            "threshold": threshold,
            "actual": actual,
            "passed": passed,
        }
        if not passed:
            failed_gates.append("critical")

    if "high" in gate_config:
        threshold = gate_config["high"]
        actual = counts["HIGH"]
        passed = actual <= threshold
        details["high"] = {"threshold": threshold, "actual": actual, "passed": passed}
        if not passed:
            failed_gates.append("high")

    if "secrets" in gate_config:
        threshold = gate_config["secrets"]
        actual = counts["secrets"]
        passed = actual <= threshold
        details["secrets"] = {
            "threshold": threshold,
            "actual": actual,
            "passed": passed,
        }
        if not passed:
            failed_gates.append("secrets")

    if "score_min" in gate_config:
        threshold = gate_config["score_min"]
        passed = score >= threshold
        details["score"] = {"threshold": threshold, "actual": score, "passed": passed}
        if not passed:
            failed_gates.append("score")

    return GateResult(
        passed=len(failed_gates) == 0,
        failed_gates=failed_gates,
        details=details,
    )
