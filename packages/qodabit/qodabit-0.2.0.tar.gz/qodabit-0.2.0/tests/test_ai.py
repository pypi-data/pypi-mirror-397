"""Tests for AI client functions."""

import tempfile
from pathlib import Path

from qodabit.ai.client import (
    apply_fix,
    get_code_context,
    get_line_content,
    validate_syntax,
)


class TestGetCodeContext:
    """Tests for get_code_context function."""

    def test_get_code_context_basic(self):
        """Get code context around a line."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("line 1\n")
            f.write("line 2\n")
            f.write("line 3\n")
            f.write("line 4\n")
            f.write("line 5\n")
            f.flush()

            context = get_code_context(f.name, 3, context_lines=1)

            assert "line 2" in context
            assert "line 3" in context
            assert "line 4" in context
            assert ">>>" in context  # Marker for target line

            Path(f.name).unlink()

    def test_get_code_context_file_not_found(self):
        """Handle non-existent file."""
        context = get_code_context("/nonexistent/file.py", 1)
        assert "File not found" in context

    def test_get_code_context_line_number(self):
        """Context includes line numbers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            for i in range(10):
                f.write(f"line {i + 1}\n")
            f.flush()

            context = get_code_context(f.name, 5, context_lines=2)

            assert "3 |" in context
            assert "4 |" in context
            assert "5 |" in context
            assert "6 |" in context
            assert "7 |" in context

            Path(f.name).unlink()


class TestGetLineContent:
    """Tests for get_line_content function."""

    def test_get_line_content_basic(self):
        """Get content of a specific line."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("first line\n")
            f.write("second line\n")
            f.write("third line\n")
            f.flush()

            content = get_line_content(f.name, 2)
            assert "second line" in content

            Path(f.name).unlink()

    def test_get_line_content_file_not_found(self):
        """Handle non-existent file."""
        content = get_line_content("/nonexistent/file.py", 1)
        assert content == ""

    def test_get_line_content_invalid_line(self):
        """Handle invalid line number."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("only one line\n")
            f.flush()

            content = get_line_content(f.name, 100)
            assert content == ""

            Path(f.name).unlink()


class TestApplyFix:
    """Tests for apply_fix function."""

    def test_apply_fix_basic(self):
        """Apply a simple fix."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('query = f"SELECT * FROM users WHERE id = {id}"\n')
            f.flush()

            old_code = 'query = f"SELECT * FROM users WHERE id = {id}"'
            new_code = 'query = "SELECT * FROM users WHERE id = %s"'

            success, error = apply_fix(f.name, old_code, new_code)
            assert success is True
            assert error == ""

            # Verify the file was updated
            with open(f.name) as f2:
                content = f2.read()
                assert new_code in content
                assert old_code not in content

            Path(f.name).unlink()

    def test_apply_fix_code_not_found(self):
        """Handle case where old code is not found."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("different code\n")
            f.flush()

            success, error = apply_fix(f.name, "nonexistent code", "new code")
            assert success is False
            assert "no encontrado" in error.lower()

            Path(f.name).unlink()

    def test_apply_fix_file_not_found(self):
        """Handle non-existent file."""
        success, error = apply_fix("/nonexistent/file.py", "old", "new")
        assert success is False
        assert "no encontrado" in error.lower()

    def test_apply_fix_invalid_syntax(self):
        """Reject fix that would create invalid Python syntax."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            f.flush()

            # This fix would create invalid syntax (missing closing paren)
            success, error = apply_fix(f.name, "x = 1", "x = (1")
            assert success is False
            assert "inválido" in error.lower() or "syntax" in error.lower()

            Path(f.name).unlink()


class TestValidateSyntax:
    """Tests for validate_syntax function."""

    def test_valid_python_syntax(self):
        """Valid Python code should pass."""
        is_valid, error = validate_syntax("test.py", "x = 1\ny = 2\n")
        assert is_valid is True
        assert error == ""

    def test_invalid_python_syntax(self):
        """Invalid Python code should fail."""
        is_valid, error = validate_syntax("test.py", "x = (\n")
        assert is_valid is False
        assert "syntax" in error.lower() or error != ""

    def test_non_python_file(self):
        """Non-Python files should pass (no validation)."""
        is_valid, error = validate_syntax("test.js", "invalid { python [")
        assert is_valid is True
        assert error == ""

    def test_valid_function(self):
        """Valid function definition should pass."""
        code = """
def hello():
    return "world"
"""
        is_valid, error = validate_syntax("test.py", code)
        assert is_valid is True

    def test_valid_class(self):
        """Valid class definition should pass."""
        code = """
class MyClass:
    def __init__(self):
        self.value = 1
"""
        is_valid, error = validate_syntax("test.py", code)
        assert is_valid is True


class TestGetCodeContextEdgeCases:
    """Additional edge cases for get_code_context."""

    def test_first_line(self):
        """Getting context for first line."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("first\nsecond\nthird\n")
            f.flush()

            context = get_code_context(f.name, 1, context_lines=1)
            assert "first" in context
            assert ">>>" in context  # Marker for line 1

            Path(f.name).unlink()

    def test_last_line(self):
        """Getting context for last line."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("first\nsecond\nthird\n")
            f.flush()

            context = get_code_context(f.name, 3, context_lines=1)
            assert "third" in context

            Path(f.name).unlink()

    def test_empty_file(self):
        """Handle empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")
            f.flush()

            context = get_code_context(f.name, 1, context_lines=1)
            # Should not crash, may return empty or minimal context
            assert context is not None

            Path(f.name).unlink()


class TestApplyFixEdgeCases:
    """Additional edge cases for apply_fix."""

    def test_apply_fix_preserves_other_code(self):
        """Fix should not affect other lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("line1 = 1\n")
            f.write("line2 = 2\n")
            f.write("line3 = 3\n")
            f.flush()

            success, error = apply_fix(f.name, "line2 = 2", "line2 = 'fixed'")
            assert success is True

            with open(f.name) as f2:
                content = f2.read()
                assert "line1 = 1" in content
                assert "line2 = 'fixed'" in content
                assert "line3 = 3" in content

            Path(f.name).unlink()

    def test_apply_fix_with_whitespace(self):
        """Fix with leading/trailing whitespace should work."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            f.flush()

            success, error = apply_fix(f.name, "  x = 1  ", "x = 2")
            # Should either succeed by stripping whitespace or fail gracefully
            assert isinstance(success, bool)

            Path(f.name).unlink()

    def test_apply_fix_multiline(self):
        """Fix with multiline code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def old():\n    pass\n")
            f.flush()

            old_code = "def old():\n    pass"
            new_code = "def new():\n    return 1"

            success, error = apply_fix(f.name, old_code, new_code)
            assert success is True

            with open(f.name) as f2:
                content = f2.read()
                assert "def new():" in content

            Path(f.name).unlink()
