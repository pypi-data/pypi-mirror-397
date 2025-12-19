# QodaBit - Fase 1: Lo que aprendimos

## Resumen

En la Fase 1 construimos el **esqueleto funcional** de QodaBit: un CLI que abre un chat interactivo y ejecuta escaneos de seguridad usando Semgrep y Gitleaks en paralelo.

---

## Arquitectura Final

```
qodabit/
├── cli.py              # Entry point (Click)
├── chat/
│   └── engine.py       # Chat REPL interactivo (Rich)
├── scanner/
│   ├── orchestrator.py # Ejecuta scanners en paralelo
│   ├── semgrep.py      # SAST scanner
│   └── gitleaks.py     # Secrets scanner
├── score/
│   ├── calculator.py   # Production-Ready Score
│   └── gates.py        # PASS/FAIL para CI
└── config/
    └── loader.py       # Carga qodabit.yaml
```

---

## Conceptos Clave

### 1. CLI Framework: Click

**¿Qué es?** Una librería de Python para crear CLIs de forma declarativa.

**¿Por qué Click?**
- Decoradores simples (`@click.command()`)
- Manejo automático de argumentos y opciones
- Agrupa comandos fácilmente (`@click.group()`)

**Ejemplo real de QodaBit:**
```python
@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        # Sin comando = abre chat
        start_chat()

@main.command()
def check():
    """Scan + evaluate gates."""
    pass
```

**Resultado:** `qodabit` abre chat, `qodabit check` ejecuta el comando check.

---

### 2. Terminal UI: Rich

**¿Qué es?** Librería para crear interfaces de terminal bonitas.

**Componentes usados:**
- `Console` - Output con colores y estilos
- `Panel` - Cajas con bordes
- `Progress` - Spinners y barras de progreso

**Ejemplo real:**
```python
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn

console = Console()

# Panel con borde
console.print(Panel(
    "[bold cyan]QodaBit v0.2.0[/bold cyan]",
    border_style="cyan"
))

# Spinner mientras escanea
with Progress(SpinnerColumn(), ...) as progress:
    task = progress.add_task("Escaneando...")
    result = await scan_project()
```

---

### 3. Async/Await para Paralelismo

**¿Por qué async?** Para ejecutar múltiples scanners AL MISMO TIEMPO.

**Sin async:** Semgrep (5s) + Gitleaks (2s) = **7 segundos**
**Con async:** Ambos en paralelo = **5 segundos** (el más lento)

**Patrón usado:**
```python
import asyncio

async def scan_project(path):
    # Ejecuta AMBOS al mismo tiempo
    results = await asyncio.gather(
        run_semgrep(path),
        run_gitleaks(path),
        return_exceptions=True,  # No falla si uno falla
    )
    return aggregate(results)
```

**Para ejecutar async desde sync:**
```python
# En el chat REPL (que es sync)
if user_input == "analiza":
    asyncio.run(run_scan())  # Ejecuta la corutina
```

---

### 4. Subprocess Async

**¿Por qué?** Semgrep y Gitleaks son binarios externos (no Python).

**Patrón:**
```python
async def run_semgrep(path):
    proc = await asyncio.create_subprocess_exec(
        "pysemgrep",
        "--config", "p/owasp-top-ten",
        "--json",
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return json.loads(stdout)
```

**Puntos clave:**
- `create_subprocess_exec` - No bloquea mientras el proceso corre
- `PIPE` - Captura output en memoria
- `communicate()` - Espera a que termine y devuelve output

---

### 5. Formato Unificado de Issues

**Problema:** Semgrep y Gitleaks devuelven JSON diferente.

**Solución:** Convertir todo a un formato unificado:

```python
@dataclass
class Issue:
    id: str          # "SEC-001"
    tool: str        # "semgrep" | "gitleaks"
    rule: str        # "python.lang.security.audit.sql-injection"
    severity: str    # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    file: str        # "src/db.py"
    line: int        # 45
    message: str     # "SQL Injection vulnerability"
    snippet: str     # El código problemático
```

**Mapeo de severidades:**
```python
# Semgrep usa ERROR/WARNING/INFO
# Nosotros usamos CRITICAL/HIGH/MEDIUM/LOW
def map_severity(semgrep_severity):
    return {
        "ERROR": "CRITICAL",
        "WARNING": "HIGH",
        "INFO": "MEDIUM",
    }.get(semgrep_severity, "LOW")
```

---

### 6. Production-Ready Score

**Fórmula simple:**
```python
def calculate_score(issues):
    score = 100

    for issue in issues:
        if issue.severity == "CRITICAL":
            score -= 15
        elif issue.severity == "HIGH":
            score -= 8
        elif issue.severity == "MEDIUM":
            score -= 3
        elif issue.severity == "LOW":
            score -= 1

    return max(0, score)  # Nunca menor a 0
```

**Categorías:**
- `90-100%` → PRODUCTION_READY
- `70-89%` → ALMOST_READY
- `50-69%` → NEEDS_WORK
- `0-49%` → NOT_READY

---

### 7. Testing con Pytest

**Estructura:**
```
tests/
├── test_score.py   # Tests del calculator
└── test_gates.py   # Tests del gate evaluator
```

**Ejemplo de test:**
```python
def test_critical_issue_penalty():
    """Critical issues subtract 15 points."""
    issues = [{"severity": "CRITICAL"}]
    result = calculate_score(issues)
    assert result.score == 85
    assert result.category == "ALMOST_READY"
```

**Ejecutar:** `pytest tests/ -v`

---

## Herramientas Instaladas

| Herramienta | Comando | Propósito |
|-------------|---------|-----------|
| Semgrep | `pip install semgrep` | SAST (detecta vulnerabilidades) |
| Gitleaks | `brew install gitleaks` | Detecta secrets hardcodeados |
| Click | dependencia | Framework CLI |
| Rich | dependencia | UI de terminal |
| Pytest | dev dependency | Testing |

---

## Comandos Disponibles (Fase 1)

```bash
# Abre chat interactivo
qodabit

# En el chat:
> analiza    # Escanea proyecto
> score      # Muestra Production-Ready Score
> issues     # Lista todos los issues
> ayuda      # Muestra comandos
> salir      # Cierra chat
```

---

## Flujo de Datos

```
Usuario escribe "analiza"
        ↓
Chat Engine detecta comando
        ↓
asyncio.run(run_scan())
        ↓
Scanner Orchestrator
        ↓
asyncio.gather(
    run_semgrep(),   ──→ subprocess ──→ JSON
    run_gitleaks(),  ──→ subprocess ──→ JSON
)
        ↓
Convertir a formato unificado (List[Issue])
        ↓
Calcular Production-Ready Score
        ↓
Mostrar resultados con Rich
```

---

## Decisiones de Diseño

### ¿Por qué no Radon en Fase 1?
Semgrep + Gitleaks cubren seguridad y secrets. Radon (complejidad) es nice-to-have, lo agregamos en Fase 4.

### ¿Por qué pysemgrep?
El comando `semgrep` regular tuvo problemas. `pysemgrep` es el core de Python que funciona mejor.

### ¿Por qué `--no-git` en Gitleaks?
Para escanear archivos actuales, no historial de git. Más rápido y relevante para el dev actual.

### ¿Por qué Python 3.9?
El sistema del usuario tiene 3.9.6. Ajustamos para compatibilidad aunque 3.10+ es preferible.

---

## Lo que NO hicimos en Fase 1

- AI (Claude/OpenAI) → Fase 3
- Gates para CI → Fase 2
- Config file (qodabit.yaml) → Fase 4
- Natural language queries → Fase 4
- PyPI publish → Fase 5

---

## Próximos pasos (Fase 2)

1. Implementar `qodabit check` que devuelve exit code 0/1
2. Implementar `qodabit audit --json` para CI
3. Gate evaluator funcional
4. Agregar comando `score` standalone

---

## Tips para contenido

### Para un thread de Twitter/X:
1. "Building a Security CLI from scratch"
2. Muestra el `pyproject.toml` y explica cada dependencia
3. Muestra el patrón async/await con diagrama
4. Screenshot del chat funcionando
5. El Production-Ready Score formula

### Para un video corto:
1. Demo: `qodabit` → `analiza` → resultados
2. Explica qué hace cada scanner
3. Muestra el score cambiando con issues

### Snippets de código interesantes:
- El `asyncio.gather()` para paralelismo
- El mapping de severidades
- El chat REPL loop
