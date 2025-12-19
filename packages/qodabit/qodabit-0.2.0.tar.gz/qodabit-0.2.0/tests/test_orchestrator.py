"""Tests for scanner orchestrator functions."""

from qodabit.scanner.orchestrator import Issue, count_by_severity, deduplicate_issues


class TestDeduplicateIssues:
    """Tests for deduplicate_issues function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        assert deduplicate_issues([]) == []

    def test_single_issue(self):
        """Single issue returns unchanged."""
        issue = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="SQL injection",
            snippet="",
        )
        result = deduplicate_issues([issue])
        assert len(result) == 1
        assert result[0].id == "SEC-001"

    def test_different_files_not_deduplicated(self):
        """Issues in different files should not be deduplicated."""
        issue1 = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="SQL injection",
            snippet="",
        )
        issue2 = Issue(
            id="SEC-002",
            tool="gitleaks",
            rule="generic-secret",
            severity="HIGH",
            file="src/auth.py",
            line=10,
            message="Secret detected",
            snippet="",
        )
        result = deduplicate_issues([issue1, issue2])
        assert len(result) == 2

    def test_different_lines_not_deduplicated(self):
        """Issues on different lines should not be deduplicated."""
        issue1 = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="SQL injection 1",
            snippet="",
        )
        issue2 = Issue(
            id="SEC-002",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="src/db.py",
            line=20,
            message="SQL injection 2",
            snippet="",
        )
        result = deduplicate_issues([issue1, issue2])
        assert len(result) == 2

    def test_same_file_line_deduplicated(self):
        """Issues on same file/line should be deduplicated."""
        issue1 = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="SQL injection",
            snippet="",
        )
        issue2 = Issue(
            id="SEC-002",
            tool="gitleaks",
            rule="generic",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="Generic issue",
            snippet="",
        )
        result = deduplicate_issues([issue1, issue2])
        assert len(result) == 1

    def test_keeps_higher_severity(self):
        """When deduplicating, keep higher severity issue."""
        issue_low = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="LOW",
            file="src/db.py",
            line=10,
            message="SQL injection",
            snippet="",
        )
        issue_critical = Issue(
            id="SEC-002",
            tool="gitleaks",
            rule="generic-secret",
            severity="CRITICAL",
            file="src/db.py",
            line=10,
            message="Secret detected",
            snippet="",
        )
        # Test both orders
        result1 = deduplicate_issues([issue_low, issue_critical])
        assert len(result1) == 1
        assert result1[0].severity == "CRITICAL"

        result2 = deduplicate_issues([issue_critical, issue_low])
        assert len(result2) == 1
        assert result2[0].severity == "CRITICAL"

    def test_path_normalization(self):
        """Different paths to same file should deduplicate."""
        issue1 = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="./src/db.py",
            line=10,
            message="SQL injection",
            snippet="",
        )
        issue2 = Issue(
            id="SEC-002",
            tool="gitleaks",
            rule="generic",
            severity="HIGH",
            file="src/db.py",
            line=10,
            message="Generic",
            snippet="",
        )
        result = deduplicate_issues([issue1, issue2])
        assert len(result) == 1


class TestCountBySeverity:
    """Tests for count_by_severity function."""

    def test_empty_list(self):
        """Empty list returns zeros."""
        result = count_by_severity([])
        assert result == {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

    def test_single_critical(self):
        """Single CRITICAL issue."""
        issues = [
            Issue(
                id="SEC-001",
                tool="semgrep",
                rule="test",
                severity="CRITICAL",
                file="test.py",
                line=1,
                message="",
                snippet="",
            )
        ]
        result = count_by_severity(issues)
        assert result["CRITICAL"] == 1
        assert result["HIGH"] == 0

    def test_mixed_severities(self):
        """Multiple issues with different severities."""
        issues = [
            Issue(
                id="SEC-001",
                tool="semgrep",
                rule="test",
                severity="CRITICAL",
                file="a.py",
                line=1,
                message="",
                snippet="",
            ),
            Issue(
                id="SEC-002",
                tool="semgrep",
                rule="test",
                severity="CRITICAL",
                file="b.py",
                line=1,
                message="",
                snippet="",
            ),
            Issue(
                id="SEC-003",
                tool="semgrep",
                rule="test",
                severity="HIGH",
                file="c.py",
                line=1,
                message="",
                snippet="",
            ),
            Issue(
                id="SEC-004",
                tool="semgrep",
                rule="test",
                severity="LOW",
                file="d.py",
                line=1,
                message="",
                snippet="",
            ),
        ]
        result = count_by_severity(issues)
        assert result["CRITICAL"] == 2
        assert result["HIGH"] == 1
        assert result["MEDIUM"] == 0
        assert result["LOW"] == 1

    def test_unknown_severity_ignored(self):
        """Unknown severity should not crash."""
        issues = [
            Issue(
                id="SEC-001",
                tool="semgrep",
                rule="test",
                severity="UNKNOWN",
                file="test.py",
                line=1,
                message="",
                snippet="",
            )
        ]
        result = count_by_severity(issues)
        assert result == {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
