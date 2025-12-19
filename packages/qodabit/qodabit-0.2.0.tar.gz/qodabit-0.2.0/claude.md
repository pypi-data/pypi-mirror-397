# CLAUDE.md — QodaBit Development Configuration

---

## PROJECT CONTEXT

**Product:** QodaBit - Security-first code auditor with deterministic gates
**Stage:** MVP v0.1 (6 weeks)
**Stack:** Python 3.9+, Click CLI, AST analysis
**Docs:** `qoda.md` (full spec), `mvp.md` (MVP scope)

### Core Principle
```
DETERMINISTA = JUEZ  →  Gates decide PASS/FAIL
AI = CIRUJANO        →  Suggests, never decides
```

### MVP Scope (v0.1)
- CLI: `init`, `audit`, `check`, `version`
- SAST: 5 rules (HARDCODED_SECRET, SQL_INJECTION, EVAL_USAGE, SHELL_INJECTION, PICKLE_USAGE)
- Secrets Scanner: regex patterns
- PR Gates: binary PASS/FAIL
- Output: JSON + Terminal

---

## ARCHITECTURE RULES

### File Structure (ENFORCED)
```
qodabit/
├── __init__.py          # Version only
├── cli.py               # Click commands (thin layer)
├── scanner.py           # File discovery
├── config.py            # YAML parsing + validation
├── gates.py             # Gate evaluation (DETERMINISTIC)
├── reporter.py          # JSON + Terminal output
├── analyzers/
│   ├── __init__.py
│   ├── base.py          # Abstract analyzer
│   ├── sast.py          # AST-based SAST rules
│   └── secrets.py       # Regex-based secrets detection
└── models.py            # Dataclasses: Issue, Finding, GateResult
```

### Code Patterns (MANDATORY)

**1. Type hints everywhere**
```python
def analyze(self, filepath: Path) -> list[Issue]: ...
```

**2. Dataclasses for models**
```python
@dataclass
class Issue:
    rule: str
    severity: Severity
    file: str
    line: int
    message: str
```

**3. No globals, no singletons**
```python
# WRONG
config = load_config()  # global

# RIGHT
def audit(config: Config) -> AuditResult: ...
```

**4. Early returns, no deep nesting**
```python
# WRONG
if condition:
    if another:
        do_thing()

# RIGHT
if not condition:
    return
if not another:
    return
do_thing()
```

**5. Determinism in gates**
```python
# Gates MUST be pure functions
def evaluate_gates(findings: list[Issue], thresholds: GateConfig) -> GateResult:
    # NO external calls
    # NO randomness
    # NO AI
    return GateResult(...)
```

---

## SECURITY RULES (CRITICAL)

### Never expose secrets
```python
# WRONG
print(f"Found secret: {secret_value}")

# RIGHT
print(f"Found secret: {redact(secret_value)}")  # sk-ab...xy89
```

### Redaction function (MANDATORY)
```python
def redact(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"
```

### No secrets in:
- Logs
- Error messages
- JSON output (use redacted snippet)
- Test fixtures (use FAKE_* prefix)

---

## TESTING RULES

### Test naming
```python
def test_<unit>_<scenario>_<expected>():
    # test_gate_evaluator_with_secrets_returns_fail
```

### Coverage requirements
- Overall: >80%
- Gates module: >95% (CRITICAL)
- Analyzers: >90%

### Test determinism
```python
def test_gates_are_deterministic():
    result1 = evaluate_gates(findings, config)
    result2 = evaluate_gates(findings, config)
    assert result1 == result2  # MUST pass
```

---

## CLI CONVENTIONS

### Exit codes
```python
EXIT_PASS = 0      # Gates passed
EXIT_FAIL = 1      # Gates failed
EXIT_CONFIG = 2    # Config error
EXIT_ERROR = 3     # Runtime error
```

### Output modes
```python
--json          # Machine-readable, CI-friendly
--quiet         # Errors only
(default)       # Human-readable with colors
```

### Error handling
```python
# Always use click.echo for output
click.echo("Error: ...", err=True)
sys.exit(EXIT_CONFIG)
```

---

## COMMIT CONVENTIONS

### Format
```
<type>(<scope>): <description>

Types: feat, fix, refactor, test, docs, chore
Scopes: cli, sast, secrets, gates, config, reporter
```

### Examples
```
feat(sast): add SQL injection detection via AST
fix(gates): ensure deterministic evaluation order
test(secrets): add OpenAI key pattern coverage
```

---

## DEVELOPMENT WORKFLOW

### Before implementing ANY feature
1. Read relevant section in `mvp.md`
2. Check if it's in MVP scope (if not, STOP)
3. Write test first
4. Implement
5. Run `pytest` + `ruff check`

### Before ANY commit
```bash
ruff check .
ruff format .
pytest
```

### PR checklist
- [ ] Tests pass
- [ ] Coverage >80%
- [ ] No new ruff warnings
- [ ] Follows architecture rules
- [ ] Exit codes correct

---

## THINKING LEVELS (USE EXPLICITLY)

| Command | When to use |
|---------|-------------|
| `think` | Simple bug fix, add test |
| `think hard` | New analyzer rule, refactor module |
| `think harder` | Cross-module changes, edge cases |
| `ultrathink` | Architecture decisions, security design |

### Examples
```
"think: fix the regex pattern for AWS keys"
"think hard: implement SQL injection detection via AST"
"ultrathink: design the gate evaluation pipeline"
```

---

## CONTEXT MANAGEMENT

### When context is large
```
/compact
```

### When starting new feature
```
Read mvp.md section X, then implement Y
```

### When debugging
```
Read the failing test, then read the implementation
```

---

## FORBIDDEN PATTERNS

### DO NOT:
1. Add features not in MVP scope
2. Use AI for gate decisions
3. Store secrets unredacted
4. Create global state
5. Skip type hints
6. Commit without tests
7. Use `print()` instead of `click.echo()`
8. Hardcode paths (use `Path` objects)

### IF ASKED TO:
- Add SCA/CVE scanning → "Not in MVP scope, see mvp.md"
- Add AI remediation → "Not in MVP scope, v0.2 feature"
- Certify compliance → "QodaBit generates evidence, not certifications"

---

## QUICK REFERENCE

### Run tests
```bash
pytest -v
pytest --cov=qodabit --cov-report=term-missing
```

### Lint + format
```bash
ruff check . --fix
ruff format .
```

### Install dev
```bash
pip install -e ".[dev]"
```

### Test CLI
```bash
qodabit --version
qodabit init
qodabit audit --json
qodabit check
```

---

## DOCUMENTATION HIERARCHY

```
qoda.md     → Full enterprise spec (reference only)
mvp.md      → MVP scope (SOURCE OF TRUTH for v0.1)
claude.md   → Development rules (THIS FILE)
README.md   → User documentation (create at release)
```

### When in doubt
1. Check `mvp.md` for scope
2. Check `claude.md` for patterns
3. Ask before adding anything not documented

---

## PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| Single file (<1K LOC) | <2s |
| Project (<5K LOC) | <5s |
| Memory | <200MB |
| False positives | <10% |

---

## RELEASE CHECKLIST (v0.1)

- [ ] All 5 SAST rules implemented + tested
- [ ] Secrets scanner with all patterns
- [ ] Gates evaluate correctly
- [ ] CLI commands work
- [ ] Exit codes correct
- [ ] JSON output valid
- [ ] Terminal output readable
- [ ] `pip install qodabit` works
- [ ] README with quick start
- [ ] No security issues in own code

---

**Last updated:** 2025-01-XX
**MVP Target:** 6 weeks
**Status:** Week 1 - Foundation
