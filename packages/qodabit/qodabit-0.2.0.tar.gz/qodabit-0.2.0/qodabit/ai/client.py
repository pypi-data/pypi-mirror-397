"""AI client - Claude/OpenAI integration."""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Literal, Optional

Provider = Literal["anthropic", "openai"]

# API Configuration
API_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds (doubles each retry)

# Default models per provider
MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-20250514",
}


def get_default_provider() -> Provider:
    """Auto-detect provider based on available API keys.

    Priority: QODABIT_AI_PROVIDER env > OpenAI key > Anthropic key
    """
    # Check explicit config first
    configured = os.getenv("QODABIT_AI_PROVIDER", "").lower()
    if configured in ("openai", "anthropic"):
        return configured  # type: ignore

    # Auto-detect based on available keys
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"

    # Default to OpenAI (more common for production)
    return "openai"


class AIClient:
    """Unified AI client for Claude and OpenAI.

    Supports multiple providers - configurable via:
    - QODABIT_AI_PROVIDER env var ("openai" or "anthropic")
    - Auto-detects based on available API keys
    """

    def __init__(self, provider: Optional[Provider] = None) -> None:
        self.provider = provider or get_default_provider()
        self._client = None

    def _get_client(self):
        """Lazy load the appropriate client."""
        if self._client:
            return self._client

        if self.provider == "anthropic":
            import anthropic

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not set. Add it to .env or environment."
                )
            self._client = anthropic.Anthropic(
                api_key=api_key,
                timeout=API_TIMEOUT,
            )
        else:
            import openai

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not set. Add it to .env or environment."
                )
            self._client = openai.OpenAI(
                api_key=api_key,
                timeout=API_TIMEOUT,
            )

        return self._client

    def explain_issue(self, issue: dict, code_context: str) -> str:
        """Get AI explanation for a security issue.

        Args:
            issue: The issue dict with id, rule, severity, file, line, message
            code_context: The surrounding code from the file

        Returns:
            Formatted explanation string
        """
        prompt = f"""Explica este problema de seguridad de forma clara y concisa en español.

Archivo: {issue.get("file", "unknown")}:{issue.get("line", 0)}
Regla: {issue.get("rule", "unknown")}
Severidad: {issue.get("severity", "unknown")}
Mensaje: {issue.get("message", "")}

Código:
```
{code_context}
```

Responde con este formato exacto:

**Problema:** [1-2 oraciones explicando qué es el problema]

**Riesgo:** [Ejemplo concreto de cómo un atacante podría explotar esto]

**Solución:**
```python
[código corregido]
```

**Por qué funciona:** [1 oración explicando por qué el fix resuelve el problema]"""

        return self._call_api(prompt)

    def generate_fix(self, issue: dict, code_context: str) -> Optional[str]:
        """Generate fix for an issue.

        Args:
            issue: The issue dict
            code_context: The code that needs fixing

        Returns:
            The fixed code or None if fix cannot be generated
        """
        prompt = f"""Genera el código corregido para este problema de seguridad.

Archivo: {issue.get("file", "unknown")}:{issue.get("line", 0)}
Regla: {issue.get("rule", "unknown")}
Problema: {issue.get("message", "")}

Código actual:
```
{code_context}
```

IMPORTANTE:
1. Devuelve SOLO el código corregido, sin explicaciones
2. Mantén el mismo estilo e indentación
3. Corrige únicamente el problema de seguridad
4. No cambies nada más del código

Código corregido:"""

        response = self._call_api(prompt)

        # Extract code from response (handle markdown code blocks)
        if "```" in response:
            # Find code between backticks
            lines = response.split("\n")
            in_code = False
            code_lines = []
            for line in lines:
                if line.startswith("```"):
                    in_code = not in_code
                    continue
                if in_code:
                    code_lines.append(line)
            return "\n".join(code_lines) if code_lines else None

        return response.strip() if response else None

    def _call_api(self, prompt: str) -> str:
        """Make API call to Claude or OpenAI with retry logic."""
        client = self._get_client()
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                model = MODELS.get(self.provider, MODELS["openai"])

                if self.provider == "anthropic":
                    response = client.messages.create(
                        model=model,
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return response.content[0].text

                else:  # OpenAI
                    response = client.chat.completions.create(
                        model=model,
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return response.choices[0].message.content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Handle specific API errors
                if "401" in error_str or "authentication" in error_str:
                    raise ValueError(
                        "API key inválida. Verifica tu ANTHROPIC_API_KEY."
                    ) from e

                if "429" in error_str or "rate" in error_str:
                    # Rate limit - wait and retry
                    wait_time = RETRY_DELAY * (2**attempt)
                    time.sleep(wait_time)
                    continue

                if "timeout" in error_str:
                    raise TimeoutError(
                        f"Request timeout después de {API_TIMEOUT}s. Intenta de nuevo."
                    ) from e

                if "500" in error_str or "502" in error_str or "503" in error_str:
                    # Server error - retry with backoff
                    wait_time = RETRY_DELAY * (2**attempt)
                    time.sleep(wait_time)
                    continue

                # Unknown error - don't retry
                raise

        # All retries exhausted
        raise RuntimeError(
            f"API no disponible después de {MAX_RETRIES} intentos: {last_error}"
        )


def get_code_context(file_path: str, line: int, context_lines: int = 10) -> str:
    """Get code context around a specific line.

    Args:
        file_path: Path to the file
        line: The line number (1-indexed)
        context_lines: Number of lines before and after to include (default: 10)

    Returns:
        Code snippet with line numbers, max ~100KB to avoid OOM
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"[File not found: {file_path}]"

        # Check file size to avoid OOM (max 100KB)
        file_size = path.stat().st_size
        if file_size > 100_000:
            # For large files, read only around the target line
            with open(path) as f:
                all_lines = []
                for i, line_content in enumerate(f, 1):
                    if abs(i - line) <= context_lines:
                        all_lines.append((i, line_content))
                    if i > line + context_lines:
                        break

                # Build context from collected lines
                result = []
                for line_num, content in all_lines:
                    marker = ">>>" if line_num == line else "   "
                    result.append(f"{marker} {line_num:4d} | {content.rstrip()}")
                return "\n".join(result)

        with open(path) as f:
            all_lines = f.readlines()

        # Calculate range (0-indexed)
        start = max(0, line - context_lines - 1)
        end = min(len(all_lines), line + context_lines)

        # Build context with line numbers
        result = []
        for i in range(start, end):
            line_num = i + 1
            marker = ">>>" if line_num == line else "   "
            result.append(f"{marker} {line_num:4d} | {all_lines[i].rstrip()}")

        return "\n".join(result)

    except Exception as e:
        return f"[Error reading file: {e}]"


def get_line_content(file_path: str, line: int) -> str:
    """Get the content of a specific line.

    Args:
        file_path: Path to the file
        line: The line number (1-indexed)

    Returns:
        The line content
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return ""

        with open(path) as f:
            all_lines = f.readlines()

        if 0 < line <= len(all_lines):
            return all_lines[line - 1]

        return ""

    except Exception:
        return ""


def validate_syntax(file_path: str, content: str) -> tuple[bool, str]:
    """Validate syntax of code before applying fix.

    Args:
        file_path: Path to determine file type
        content: The code content to validate

    Returns:
        (is_valid, error_message)
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".py":
        # Validate Python syntax
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(content)
                temp_path = f.name

            result = subprocess.run(
                [sys.executable, "-m", "py_compile", temp_path],
                capture_output=True,
                text=True,
            )
            Path(temp_path).unlink()

            if result.returncode != 0:
                return False, f"Syntax error: {result.stderr}"
            return True, ""

        except Exception as e:
            return False, f"Validation error: {e}"

    # For other languages, skip validation (can be extended)
    return True, ""


def apply_fix(file_path: str, old_code: str, new_code: str) -> tuple[bool, str]:
    """Apply a fix to a file with syntax validation.

    Args:
        file_path: Path to the file
        old_code: The original code to replace
        new_code: The new code

    Returns:
        (success, error_message) tuple
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False, "Archivo no encontrado"

        content = path.read_text()

        # Check if old code exists
        if old_code.strip() not in content:
            return False, "Código original no encontrado (puede haber cambiado)"

        # Create new content
        new_content = content.replace(old_code.strip(), new_code.strip(), 1)

        # Validate syntax before applying
        is_valid, error = validate_syntax(file_path, new_content)
        if not is_valid:
            return False, f"Fix genera código inválido: {error}"

        # Apply the fix
        path.write_text(new_content)
        return True, ""

    except Exception as e:
        return False, f"Error aplicando fix: {e}"
