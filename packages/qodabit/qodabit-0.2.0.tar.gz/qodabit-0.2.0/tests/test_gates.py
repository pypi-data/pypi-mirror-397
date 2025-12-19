"""Tests for gate evaluator."""

from qodabit.score.gates import evaluate_gates


def test_all_gates_pass():
    """No issues = all gates pass."""
    result = evaluate_gates(
        issues=[],
        score=100,
        gate_config={"critical": 0, "high": 0, "secrets": 0, "score_min": 80},
    )
    assert result.passed is True
    assert result.failed_gates == []


def test_critical_gate_fails():
    """Critical issues fail the critical gate."""
    issues = [{"severity": "CRITICAL", "tool": "semgrep"}]
    result = evaluate_gates(
        issues=issues,
        score=85,
        gate_config={"critical": 0},
    )
    assert result.passed is False
    assert "critical" in result.failed_gates


def test_score_gate_fails():
    """Low score fails the score gate."""
    result = evaluate_gates(
        issues=[],
        score=75,
        gate_config={"score_min": 80},
    )
    assert result.passed is False
    assert "score" in result.failed_gates


def test_secrets_gate():
    """Gitleaks issues fail secrets gate."""
    issues = [{"severity": "HIGH", "tool": "gitleaks"}]
    result = evaluate_gates(
        issues=issues,
        score=92,
        gate_config={"secrets": 0},
    )
    assert result.passed is False
    assert "secrets" in result.failed_gates


def test_multiple_gates_fail():
    """Multiple gates can fail at once."""
    issues = [
        {"severity": "CRITICAL", "tool": "semgrep"},
        {"severity": "HIGH", "tool": "gitleaks"},
    ]
    result = evaluate_gates(
        issues=issues,
        score=50,
        gate_config={"critical": 0, "secrets": 0, "score_min": 80},
    )
    assert result.passed is False
    assert len(result.failed_gates) == 3
