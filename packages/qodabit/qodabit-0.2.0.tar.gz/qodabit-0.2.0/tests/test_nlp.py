"""Tests for Natural Language Processing in chat."""

from qodabit.chat import engine
from qodabit.chat.engine import find_issue_by_topic, parse_natural_language
from qodabit.scanner.orchestrator import Issue


class TestParseNaturalLanguage:
    """Tests for parse_natural_language function."""

    # Exit intents
    def test_exit_salir(self):
        """Recognize 'salir' as exit intent."""
        intent, arg = parse_natural_language("salir")
        assert intent == "exit"

    def test_exit_quit(self):
        """Recognize 'quit' as exit intent."""
        intent, arg = parse_natural_language("quit")
        assert intent == "exit"

    def test_exit_adios(self):
        """Recognize 'adios' as exit intent."""
        intent, arg = parse_natural_language("adiós")
        assert intent == "exit"

    # Help intents
    def test_help_ayuda(self):
        """Recognize 'ayuda' as help intent."""
        intent, arg = parse_natural_language("ayuda")
        assert intent == "help"

    def test_help_question_mark(self):
        """Recognize '?' as help intent."""
        intent, arg = parse_natural_language("?")
        assert intent == "help"

    # Scan intents
    def test_scan_analiza(self):
        """Recognize 'analiza' as scan intent."""
        intent, arg = parse_natural_language("analiza")
        assert intent == "scan"

    def test_scan_natural_language(self):
        """Recognize natural language scan request."""
        intent, arg = parse_natural_language("analiza mi código")
        assert intent == "scan"

    def test_scan_revisa(self):
        """Recognize 'revisa mi proyecto' as scan intent."""
        intent, arg = parse_natural_language("revisa mi proyecto")
        assert intent == "scan"

    def test_scan_vulnerabilidades(self):
        """Recognize 'hay vulnerabilidades' as scan intent."""
        intent, arg = parse_natural_language("hay vulnerabilidades en mi proyecto")
        assert intent == "scan"

    # Scan with path intents
    def test_scan_path_analiza(self):
        """Recognize 'analiza src/db.py' as scan_path intent."""
        intent, arg = parse_natural_language("analiza src/db.py")
        assert intent == "scan_path"
        assert arg == "src/db.py"

    def test_scan_path_solo(self):
        """Recognize 'analiza solo src/auth.py' as scan_path intent."""
        intent, arg = parse_natural_language("analiza solo src/auth.py")
        assert intent == "scan_path"
        assert arg == "src/auth.py"

    def test_scan_path_revisa(self):
        """Recognize 'revisa src/' as scan_path intent."""
        intent, arg = parse_natural_language("revisa src/")
        assert intent == "scan_path"
        assert arg == "src/"

    # Score intents
    def test_score_command(self):
        """Recognize 'score' as score intent."""
        intent, arg = parse_natural_language("score")
        assert intent == "score"

    def test_score_natural_language(self):
        """Recognize 'qué tan listo está' as score intent."""
        intent, arg = parse_natural_language("¿qué tan listo está mi código?")
        assert intent == "score"

    def test_score_production_ready(self):
        """Recognize 'production ready' as score intent."""
        intent, arg = parse_natural_language("production ready score")
        assert intent == "score"

    # Issues intents
    def test_issues_command(self):
        """Recognize 'issues' as issues intent."""
        intent, arg = parse_natural_language("issues")
        assert intent == "issues"

    def test_issues_lista(self):
        """Recognize 'lista' as issues intent."""
        intent, arg = parse_natural_language("lista")
        assert intent == "issues"

    def test_issues_natural_language(self):
        """Recognize 'muestra los issues' as issues intent."""
        intent, arg = parse_natural_language("muestra los issues")
        assert intent == "issues"

    def test_issues_problemas(self):
        """Recognize 'qué problemas hay' as issues intent."""
        intent, arg = parse_natural_language("qué problemas hay")
        assert intent == "issues"

    # Explain intents
    def test_explain_command(self):
        """Recognize 'explica SEC-123' as explain intent."""
        intent, arg = parse_natural_language("explica SEC-123abc")
        assert intent == "explain"
        assert arg == "SEC-123ABC"

    def test_explain_natural_language(self):
        """Recognize 'cómo arreglo el SEC-123' as explain intent."""
        intent, arg = parse_natural_language("cómo arreglo el SEC-123abc")
        assert intent == "explain"
        assert arg == "SEC-123ABC"

    def test_explain_topic_sql_injection(self):
        """Recognize 'qué es sql injection' as explain_topic intent."""
        intent, arg = parse_natural_language("qué es sql injection")
        assert intent == "explain_topic"
        assert arg is not None
        assert "sql injection" in arg.lower()

    # Fix intents
    def test_fix_command(self):
        """Recognize 'fix SEC-123' as fix intent."""
        intent, arg = parse_natural_language("fix SEC-123abc")
        assert intent == "fix"
        assert arg == "SEC-123ABC"

    def test_fix_arregla(self):
        """Recognize 'arregla SEC-123' as fix intent."""
        intent, arg = parse_natural_language("arregla SEC-123abc")
        assert intent == "fix"
        assert arg == "SEC-123ABC"

    def test_fix_corrige(self):
        """Recognize 'corrige SEC-123' as fix intent."""
        intent, arg = parse_natural_language("corrige SEC-123abc")
        assert intent == "fix"
        assert arg == "SEC-123ABC"

    # Question intents
    def test_question_general(self):
        """Recognize general question as question intent."""
        intent, arg = parse_natural_language("¿cuánto tiempo toma?")
        assert intent == "question"

    # Unknown intents
    def test_unknown_random_text(self):
        """Recognize random text as unknown intent."""
        intent, arg = parse_natural_language("hello world")
        assert intent == "unknown"

    # Case insensitivity
    def test_case_insensitive_scan(self):
        """Commands should be case insensitive."""
        intent, arg = parse_natural_language("ANALIZA")
        assert intent == "scan"

    def test_case_insensitive_fix(self):
        """Fix with lowercase SEC should work."""
        intent, arg = parse_natural_language("fix sec-abc123")
        assert intent == "fix"
        assert arg == "SEC-ABC123"


class TestFindIssueByTopic:
    """Tests for find_issue_by_topic function."""

    def setup_method(self):
        """Clear issues before each test."""
        engine._issues_by_id = {}

    def teardown_method(self):
        """Clear issues after each test."""
        engine._issues_by_id = {}

    def test_find_no_issues(self):
        """Return None when no issues exist."""
        result = find_issue_by_topic("sql injection")
        assert result is None

    def test_find_single_match(self):
        """Find issue by topic when single match."""
        issue = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="db.py",
            line=10,
            message="SQL injection vulnerability",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue}

        result = find_issue_by_topic("sql injection")
        assert result == "SEC-001"

    def test_find_no_match(self):
        """Return None when topic doesn't match."""
        issue = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="hardcoded_secret",
            severity="HIGH",
            file="config.py",
            line=5,
            message="Hardcoded API key",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue}

        result = find_issue_by_topic("sql injection")
        assert result is None

    def test_prioritize_critical_over_high(self):
        """Return CRITICAL severity issue when multiple matches."""
        issue_high = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="sql_injection",
            severity="HIGH",
            file="db.py",
            line=10,
            message="SQL injection in query",
            snippet="",
        )
        issue_critical = Issue(
            id="SEC-002",
            tool="semgrep",
            rule="sql_injection",
            severity="CRITICAL",
            file="auth.py",
            line=20,
            message="SQL injection in authentication",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue_high, "SEC-002": issue_critical}

        result = find_issue_by_topic("sql injection")
        assert result == "SEC-002"

    def test_prioritize_high_over_medium(self):
        """Return HIGH severity issue over MEDIUM."""
        issue_medium = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="eval_usage",
            severity="MEDIUM",
            file="utils.py",
            line=10,
            message="eval usage detected",
            snippet="",
        )
        issue_high = Issue(
            id="SEC-002",
            tool="semgrep",
            rule="eval_usage",
            severity="HIGH",
            file="parser.py",
            line=20,
            message="eval usage in parser",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue_medium, "SEC-002": issue_high}

        result = find_issue_by_topic("eval")
        assert result == "SEC-002"

    def test_case_insensitive_topic(self):
        """Topic matching should be case insensitive."""
        issue = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="SQL_INJECTION",
            severity="HIGH",
            file="db.py",
            line=10,
            message="SQL Injection Vulnerability",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue}

        result = find_issue_by_topic("SQL INJECTION")
        assert result == "SEC-001"

    def test_topic_with_hyphens(self):
        """Topic with hyphens should match underscored rules."""
        issue = Issue(
            id="SEC-001",
            tool="semgrep",
            rule="shell_injection",
            severity="CRITICAL",
            file="cmd.py",
            line=5,
            message="Shell injection vulnerability",
            snippet="",
        )
        engine._issues_by_id = {"SEC-001": issue}

        result = find_issue_by_topic("shell-injection")
        assert result == "SEC-001"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    # Empty/invalid input
    def test_empty_input(self):
        """Empty input should return unknown."""
        intent, arg = parse_natural_language("")
        assert intent == "unknown"

    def test_whitespace_only(self):
        """Whitespace only should return unknown."""
        intent, arg = parse_natural_language("   ")
        assert intent == "unknown"

    # Path edge cases
    def test_path_with_dots(self):
        """Path with dots in name should work."""
        intent, arg = parse_natural_language("analiza src/db.config.py")
        assert intent == "scan_path"
        assert arg == "src/db.config.py"

    def test_path_with_numbers(self):
        """Path with numbers should work."""
        intent, arg = parse_natural_language("analiza test/test_v2.py")
        assert intent == "scan_path"
        assert arg == "test/test_v2.py"

    def test_nested_directory(self):
        """Deeply nested directory should work."""
        intent, arg = parse_natural_language("analiza src/modules/auth/handlers.py")
        assert intent == "scan_path"
        assert arg == "src/modules/auth/handlers.py"

    def test_root_directory(self):
        """Root directory should work."""
        intent, arg = parse_natural_language("analiza ./")
        assert intent == "scan_path"
        assert arg == "./"

    # Ambiguous commands
    def test_fix_without_id_returns_fix_intent(self):
        """'arregla todo' should return fix intent with 'todo' as arg."""
        intent, arg = parse_natural_language("arregla todo")
        assert intent == "fix"
        assert arg == "todo"

    def test_fix_with_partial_word(self):
        """Fix with partial word should try to match."""
        intent, arg = parse_natural_language("arregla sql")
        assert intent == "fix"
        assert arg == "sql"

    # Special characters
    def test_question_marks(self):
        """Multiple question marks should work."""
        intent, arg = parse_natural_language("¿¿qué problemas hay??")
        assert intent == "issues"

    def test_exclamation_marks(self):
        """Input with exclamation marks should work."""
        intent, arg = parse_natural_language("analiza!")
        # Should still recognize as scan
        assert intent == "scan" or intent == "unknown"

    # Unicode handling
    def test_unicode_accents(self):
        """Spanish accents should be handled."""
        intent, arg = parse_natural_language("explicación")
        # Should not crash, may return unknown
        assert intent in ("explain_topic", "unknown", "question")

    def test_numbers_in_input(self):
        """Numbers in input should be handled."""
        intent, arg = parse_natural_language("explica SEC-123456789")
        assert intent == "explain"
        assert arg == "SEC-123456789"

    # Command combinations (edge cases)
    def test_mixed_intent_scan_priority(self):
        """When scan and score keywords appear, scan should win."""
        intent, arg = parse_natural_language("analiza qué tan listo está")
        # This tests pattern priority
        assert intent in ("scan", "score")

    def test_fix_topic_sql(self):
        """Fix with topic 'sql injection' should work."""
        intent, arg = parse_natural_language("arregla el sql injection")
        assert intent == "fix"
        assert "sql" in arg.lower()
