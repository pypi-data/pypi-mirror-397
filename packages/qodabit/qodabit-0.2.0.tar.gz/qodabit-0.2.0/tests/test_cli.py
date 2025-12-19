"""Tests for CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from qodabit.cli import EXIT_FAIL, EXIT_PASS, main
from qodabit.scanner.orchestrator import Issue, ScanResult


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_scan_no_issues():
    """Mock scan with no issues."""
    return ScanResult(
        issues=[],
        tools_run=["semgrep", "gitleaks"],
        duration_ms=100,
        errors=[],
    )


@pytest.fixture
def mock_scan_with_issues():
    """Mock scan with issues."""
    return ScanResult(
        issues=[
            Issue(
                id="SEC-001",
                tool="semgrep",
                rule="sql-injection",
                severity="CRITICAL",
                file="test.py",
                line=10,
                message="SQL injection detected",
                snippet="query = f'SELECT * FROM users WHERE id = {id}'",
            ),
            Issue(
                id="SEC-002",
                tool="gitleaks",
                rule="generic-api-key",
                severity="CRITICAL",
                file="config.py",
                line=5,
                message="API key exposed",
                snippet="API_KEY = 'sk-1234567890'",
            ),
        ],
        tools_run=["semgrep", "gitleaks"],
        duration_ms=150,
        errors=[],
    )


class TestCheckCommand:
    """Tests for qodabit check command."""

    def test_check_pass_no_issues(self, runner, mock_scan_no_issues):
        """Check passes when no issues found."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_no_issues

            result = runner.invoke(main, ["check"])

            assert result.exit_code == EXIT_PASS
            assert "PASS" in result.output

    def test_check_fail_with_critical(self, runner, mock_scan_with_issues):
        """Check fails when critical issues found."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_with_issues

            result = runner.invoke(main, ["check"])

            assert result.exit_code == EXIT_FAIL
            assert "FAIL" in result.output

    def test_check_with_path(self, runner, mock_scan_no_issues):
        """Check accepts --path option."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_no_issues

            result = runner.invoke(main, ["check", "--path", "/tmp"])

            assert result.exit_code == EXIT_PASS
            mock_scan.assert_called_once_with("/tmp")


class TestAuditCommand:
    """Tests for qodabit audit command."""

    def test_audit_json_output(self, runner, mock_scan_with_issues):
        """Audit outputs valid JSON."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_with_issues

            result = runner.invoke(main, ["audit", "--json"])

            assert result.exit_code == 0
            output = json.loads(result.output)
            assert "score" in output
            assert "category" in output
            assert "issues" in output
            assert len(output["issues"]) == 2

    def test_audit_json_with_gate(self, runner, mock_scan_with_issues):
        """Audit with gate includes gate result."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_with_issues

            result = runner.invoke(main, ["audit", "--json", "--gate", "pr"])

            output = json.loads(result.output)
            assert "gates" in output
            assert output["gates"]["status"] == "FAIL"
            assert result.exit_code == EXIT_FAIL

    def test_audit_human_readable(self, runner, mock_scan_no_issues):
        """Audit without --json shows human readable output."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_no_issues

            result = runner.invoke(main, ["audit"])

            assert result.exit_code == 0
            assert "Production-Ready Score" in result.output or "Score" in result.output


class TestScoreCommand:
    """Tests for qodabit score command."""

    def test_score_json_output(self, runner, mock_scan_no_issues):
        """Score outputs JSON when --json flag is used."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_no_issues

            result = runner.invoke(main, ["score", "--json"])

            assert result.exit_code == 0
            output = json.loads(result.output)
            assert output["score"] == 100
            assert output["category"] == "PRODUCTION_READY"

    def test_score_with_issues(self, runner, mock_scan_with_issues):
        """Score reflects penalties from issues."""
        with patch("qodabit.cli.scan_project", new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = mock_scan_with_issues

            result = runner.invoke(main, ["score", "--json"])

            output = json.loads(result.output)
            # 2 critical issues = -30 points = 70%
            assert output["score"] == 70


class TestInitCommand:
    """Tests for qodabit init command."""

    def test_init_creates_config(self, runner):
        """Init creates qodabit.yaml file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(main, ["init", "--path", tmpdir])

            assert result.exit_code == 0
            config_path = Path(tmpdir) / "qodabit.yaml"
            assert config_path.exists()
            assert "gates:" in config_path.read_text()

    def test_init_does_not_overwrite(self, runner):
        """Init does not overwrite existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "qodabit.yaml"
            config_path.write_text("existing: config")

            result = runner.invoke(main, ["init", "--path", tmpdir])

            assert result.exit_code == 0
            assert "already exists" in result.output
            assert config_path.read_text() == "existing: config"


class TestVersionOption:
    """Tests for version option."""

    def test_version_option(self, runner):
        """--version shows version."""
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "qodabit" in result.output.lower()
        assert "0.2.0" in result.output or "version" in result.output.lower()
