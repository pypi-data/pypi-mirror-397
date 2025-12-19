"""Tests for score calculator."""

from qodabit.score.calculator import calculate_score


def test_perfect_score_no_issues():
    """No issues = 100% score."""
    result = calculate_score([])
    assert result.score == 100
    assert result.category == "PRODUCTION_READY"


def test_critical_issue_penalty():
    """Critical issues subtract 15 points."""
    issues = [{"severity": "CRITICAL"}]
    result = calculate_score(issues)
    assert result.score == 85
    assert result.category == "ALMOST_READY"


def test_multiple_issues():
    """Multiple issues stack penalties."""
    issues = [
        {"severity": "CRITICAL"},  # -15
        {"severity": "HIGH"},  # -8
        {"severity": "MEDIUM"},  # -3
    ]
    result = calculate_score(issues)
    assert result.score == 74  # 100 - 15 - 8 - 3
    assert result.category == "ALMOST_READY"


def test_score_minimum_zero():
    """Score cannot go below 0."""
    issues = [{"severity": "CRITICAL"} for _ in range(10)]
    result = calculate_score(issues)
    assert result.score == 0
    assert result.category == "NOT_READY"


def test_categories():
    """Test score categories."""
    # PRODUCTION_READY: >= 90
    assert calculate_score([]).category == "PRODUCTION_READY"  # 100
    assert calculate_score([{"severity": "HIGH"}]).category == "PRODUCTION_READY"  # 92

    # ALMOST_READY: 70-89
    assert calculate_score([{"severity": "CRITICAL"}]).category == "ALMOST_READY"  # 85
    assert (
        calculate_score([{"severity": "CRITICAL"}, {"severity": "CRITICAL"}]).category
        == "ALMOST_READY"
    )  # 70

    # NEEDS_WORK: 50-69
    assert (
        calculate_score([{"severity": "CRITICAL"} for _ in range(3)]).category
        == "NEEDS_WORK"
    )  # 55

    # NOT_READY: < 50
    assert (
        calculate_score([{"severity": "CRITICAL"} for _ in range(5)]).category
        == "NOT_READY"
    )  # 25
