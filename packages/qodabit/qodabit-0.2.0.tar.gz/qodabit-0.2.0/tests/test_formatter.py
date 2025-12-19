"""Tests for reporter formatter functions."""

import json

from qodabit.reporter.formatter import (
    format_json_output,
    get_category,
    get_color,
    group_by_severity,
)


class TestGetCategory:
    """Tests for get_category function."""

    def test_production_ready_100(self):
        """Score 100 should be PRODUCTION_READY."""
        assert get_category(100) == "PRODUCTION_READY"

    def test_production_ready_90(self):
        """Score 90 should be PRODUCTION_READY."""
        assert get_category(90) == "PRODUCTION_READY"

    def test_almost_ready_89(self):
        """Score 89 should be ALMOST_READY."""
        assert get_category(89) == "ALMOST_READY"

    def test_almost_ready_70(self):
        """Score 70 should be ALMOST_READY."""
        assert get_category(70) == "ALMOST_READY"

    def test_needs_work_69(self):
        """Score 69 should be NEEDS_WORK."""
        assert get_category(69) == "NEEDS_WORK"

    def test_needs_work_50(self):
        """Score 50 should be NEEDS_WORK."""
        assert get_category(50) == "NEEDS_WORK"

    def test_not_ready_49(self):
        """Score 49 should be NOT_READY."""
        assert get_category(49) == "NOT_READY"

    def test_not_ready_0(self):
        """Score 0 should be NOT_READY."""
        assert get_category(0) == "NOT_READY"


class TestGetColor:
    """Tests for get_color function."""

    def test_production_ready_green(self):
        """PRODUCTION_READY should be green."""
        assert get_color("PRODUCTION_READY") == "green"

    def test_almost_ready_yellow(self):
        """ALMOST_READY should be yellow."""
        assert get_color("ALMOST_READY") == "yellow"

    def test_needs_work_orange(self):
        """NEEDS_WORK should be orange1."""
        assert get_color("NEEDS_WORK") == "orange1"

    def test_not_ready_red(self):
        """NOT_READY should be red."""
        assert get_color("NOT_READY") == "red"

    def test_unknown_white(self):
        """Unknown category should be white."""
        assert get_color("UNKNOWN") == "white"


class TestGroupBySeverity:
    """Tests for group_by_severity function."""

    def test_empty_list(self):
        """Empty list returns empty dict."""
        assert group_by_severity([]) == {}

    def test_single_issue(self):
        """Single issue groups correctly."""
        issues = [{"id": "SEC-001", "severity": "CRITICAL"}]
        result = group_by_severity(issues)
        assert "CRITICAL" in result
        assert len(result["CRITICAL"]) == 1

    def test_multiple_severities(self):
        """Multiple severities group correctly."""
        issues = [
            {"id": "SEC-001", "severity": "CRITICAL"},
            {"id": "SEC-002", "severity": "HIGH"},
            {"id": "SEC-003", "severity": "HIGH"},
            {"id": "SEC-004", "severity": "LOW"},
        ]
        result = group_by_severity(issues)
        assert len(result["CRITICAL"]) == 1
        assert len(result["HIGH"]) == 2
        assert len(result["LOW"]) == 1
        assert "MEDIUM" not in result

    def test_missing_severity_defaults_to_low(self):
        """Issue without severity defaults to LOW."""
        issues = [{"id": "SEC-001"}]
        result = group_by_severity(issues)
        assert "LOW" in result


class TestFormatJsonOutput:
    """Tests for format_json_output function."""

    def test_valid_json(self):
        """Output should be valid JSON."""
        data = {"score": 85, "issues": []}
        output = format_json_output(data)
        parsed = json.loads(output)
        assert parsed["score"] == 85

    def test_nested_data(self):
        """Nested data should format correctly."""
        data = {
            "score": 75,
            "issues": [
                {"id": "SEC-001", "severity": "HIGH"},
            ],
        }
        output = format_json_output(data)
        parsed = json.loads(output)
        assert len(parsed["issues"]) == 1

    def test_empty_data(self):
        """Empty data should work."""
        data = {}
        output = format_json_output(data)
        assert json.loads(output) == {}
