# QodaBit

**Security Copilot for AI Devs** - Chat-based code auditor with deterministic gates.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-123%20passing-brightgreen.svg)]()

## Features

- **Chat Mode** - Natural language security queries ("scan for secrets", "check my auth")
- **NLP Support** - English and Spanish commands with typo tolerance
- **AI-Powered Explanations** - Get detailed explanations and fix suggestions
- **Deterministic Gates** - Binary PASS/FAIL for CI/CD pipelines
- **Security Score** - A-F grading based on findings
- **Multi-Provider AI** - Supports OpenAI and Anthropic APIs

## Installation

```bash
pip install qodabit
```

## Quick Start

```bash
# Initialize configuration
qodabit init

# Interactive chat mode
qodabit

# Run security audit
qodabit audit

# CI/CD gate check
qodabit check
```

## Chat Mode Examples

QodaBit understands natural language:

```bash
> scan for secrets
> check my authentication
> fix the sql injection in db.py
> explain the vulnerability at line 42
> show security score
```

Works in English and Spanish:

```bash
> escanea secretos
> revisa mi código
> arregla la inyección sql
```

## Commands

| Command | Description |
|---------|-------------|
| `qodabit` | Interactive chat mode |
| `qodabit audit` | Run full security audit |
| `qodabit check` | CI/CD gate check (PASS/FAIL) |
| `qodabit init` | Create configuration file |
| `qodabit version` | Show version |

## Configuration

### Environment Variables

```bash
# Required: At least one AI provider key
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Force specific provider
QODABIT_AI_PROVIDER=openai  # or anthropic
```

### Configuration File (qodabit.yaml)

```yaml
gates:
  max_critical: 0
  max_high: 5
  max_medium: 20

include:
  - "**/*.py"
  - "**/*.js"

exclude:
  - "**/node_modules/**"
  - "**/.venv/**"
```

## Security Rules

QodaBit detects:

| Rule | Severity | Description |
|------|----------|-------------|
| `HARDCODED_SECRET` | CRITICAL | API keys, passwords in code |
| `SQL_INJECTION` | CRITICAL | Unsafe SQL query construction |
| `EVAL_USAGE` | HIGH | Dangerous eval() calls |
| `SHELL_INJECTION` | HIGH | Unsafe shell command execution |
| `PICKLE_USAGE` | MEDIUM | Insecure deserialization |

## CI/CD Integration

### GitHub Actions

```yaml
- name: Security Check
  run: |
    pip install qodabit
    qodabit check
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Gates PASSED |
| 1 | Gates FAILED |
| 2 | Configuration error |
| 3 | Runtime error |

## Output Formats

```bash
# Terminal (default)
qodabit audit

# JSON output
qodabit audit --json

# Quiet mode (errors only)
qodabit audit --quiet
```

## Security Score

QodaBit calculates a security score (A-F) based on findings:

| Grade | Description |
|-------|-------------|
| A | Excellent - No critical/high issues |
| B | Good - Minor issues only |
| C | Fair - Some medium issues |
| D | Poor - High severity issues |
| F | Critical - Immediate action required |

## Requirements

- Python 3.9+
- OpenAI API key or Anthropic API key

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/qodabit.git
cd qodabit

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check .
ruff format .
```

## Architecture

```
AI = SURGEON     → Suggests fixes, never decides
GATES = JUDGE    → Deterministic PASS/FAIL
```

QodaBit separates concerns:
- **Scanners** detect issues deterministically
- **Gates** evaluate pass/fail criteria
- **AI** provides explanations and suggestions

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read our contributing guidelines first.

---

**QodaBit** - Security that speaks your language.
