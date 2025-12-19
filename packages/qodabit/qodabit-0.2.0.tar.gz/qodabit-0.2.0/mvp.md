# QodaBit MVP v2 — Chat de Seguridad para AI Devs

---

## 1. Visión

**QodaBit = El copiloto de seguridad que falta entre Cursor/Claude Code y producción.**

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   Cursor / Claude Code          QodaBit           Producción │
│   ─────────────────────    ──────────────────    ────────── │
│   "Genera código"          "¿Está listo?"        "Deploy"   │
│                                                              │
│   [Vibe Coding] ──────────► [Validación] ──────► [Ship it]  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### El Problema
- AI Devs generan código rápido con Cursor/Claude Code
- No saben si ese código es seguro/production-ready
- Las herramientas existentes (Bandit, ESLint) son aburridas y no explican
- Nadie ofrece un **chat de seguridad** que hable su idioma

### La Solución
```bash
$ qodabit
> ¿Este código está listo para producción?

QodaBit: Analicé tu proyecto. Score: 67% Production-Ready

🔴 2 Critical:
   - SQL Injection en db.py:45
   - Secret hardcodeado en config.py:12

🟡 3 High:
   - Complejidad alta en utils.py (función process_data)

> Explícame el SQL injection

QodaBit: El problema está en la línea 45...
[explicación clara + código corregido]

> Aplica el fix

QodaBit: ✅ Aplicado. Re-analizando... Score: 78%
```

---

## 2. Diferenciador

| Herramienta | Qué hace | Problema |
|-------------|----------|----------|
| Bandit | Detecta vulnerabilidades | Sin AI, output críptico |
| Semgrep | SAST multi-lenguaje | Sin chat, curva de aprendizaje |
| SonarQube | Quality gates | Pesado, enterprise-only |
| **QodaBit** | **Chat + Detección + Fix + Score** | **Ninguno** |

**QodaBit = Semgrep + Gitleaks + AI Chat + Production Score**

---

## 3. Experiencia de Usuario

### Modo Chat (Principal)
```bash
$ qodabit

╭─────────────────────────────────────────────╮
│  QodaBit - Security Copilot                 │
│  "¿Tu código está listo para producción?"   │
╰─────────────────────────────────────────────╯

> analiza

Escaneando proyecto...
├── Semgrep: 47 archivos
├── Gitleaks: secrets scan
└── Radon: complexity analysis

Resultado: 72% Production-Ready

┌─────────────────────────────────────────────┐
│ 🔴 CRITICAL (2)                             │
│    SEC-001: SQL Injection      db.py:45     │
│    SEC-002: Hardcoded Secret   config.py:12 │
│                                             │
│ 🟠 HIGH (1)                                 │
│    CMP-001: High Complexity    utils.py:89  │
│                                             │
│ 🟡 MEDIUM (3)                               │
│    ...                                      │
└─────────────────────────────────────────────┘

> explica SEC-001

📋 SQL Injection en db.py:45

El código actual:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

❌ Problema: El user_id se concatena directamente en el query.
   Un atacante podría enviar: "1; DROP TABLE users; --"

✅ Solución:
```python
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

¿Quieres que aplique este fix? (s/n)

> s

✅ Fix aplicado en db.py:45
Re-analizando... Score: 84% (+12%)

> siguiente

📋 SEC-002: Hardcoded Secret en config.py:12
...
```

### Modo Comando (CI/CD)
```bash
# Para pipelines - no interactivo
$ qodabit check
Exit code: 1 (FAIL - 2 critical issues)

$ qodabit check --json > report.json

$ qodabit audit --gate pr
FAIL: Gates not passed
- secrets: 1 found (threshold: 0)
- sast_critical: 2 found (threshold: 0)
```

---

## 4. Stack Técnico

### Herramientas Determinísticas (el motor)

| Función | Herramienta | Por qué |
|---------|-------------|---------|
| SAST | **Semgrep OSS** | 30+ lenguajes, OWASP rules, gratis |
| Secrets | **Gitleaks** | El mejor detector de secrets, gratis |
| Complexity | **Radon** (Python) | Cyclomatic complexity |
| Dependencies | **pip-audit / npm audit** | CVE detection |

### AI Layer (la magia)

| Función | Tecnología |
|---------|------------|
| Chat | Claude API (Anthropic) |
| Explain | Claude con contexto del issue |
| Fix | Claude genera código corregido |
| Apply | Edición automática del archivo |

### Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        QodaBit CLI                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    Chat     │    │   Scanner   │    │   Reporter  │     │
│  │   Engine    │◄──►│  Orchestrator│◄──►│   + Score   │     │
│  └──────┬──────┘    └──────┬──────┘    └─────────────┘     │
│         │                  │                                 │
│         ▼                  ▼                                 │
│  ┌─────────────┐    ┌─────────────────────────────────┐    │
│  │   Claude    │    │      Herramientas Externas       │    │
│  │    API      │    │  ┌─────────┐ ┌────────┐ ┌─────┐ │    │
│  └─────────────┘    │  │ Semgrep │ │Gitleaks│ │Radon│ │    │
│                      │  └─────────┘ └────────┘ └─────┘ │    │
│                      └─────────────────────────────────┘    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                       Gate Evaluator                         │
│              (PASS/FAIL determinístico para CI)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Requisitos Funcionales

### FR-1: Chat Interactivo

**FR-1.1** `qodabit` sin argumentos abre modo chat

**FR-1.2** Comandos en chat:
```
analiza / scan      → Escanea proyecto completo
explica <ID>        → Explica issue específico
fix <ID>            → Genera y aplica fix
siguiente / next    → Va al siguiente issue
score               → Muestra Production-Ready Score
salir / exit        → Cierra chat
```

**FR-1.3** El chat mantiene contexto de la conversación

**FR-1.4** Preguntas en lenguaje natural:
```
> ¿qué problemas tiene mi código?
> ¿cómo arreglo el SQL injection?
> ¿está seguro este archivo?
> analiza solo src/auth.py
```

---

### FR-2: Scanner Orchestrator

**FR-2.1** Ejecuta herramientas en paralelo:
```python
async def scan():
    results = await asyncio.gather(
        run_semgrep(),      # SAST
        run_gitleaks(),     # Secrets
        run_radon(),        # Complexity
        run_pip_audit(),    # Dependencies (si aplica)
    )
    return aggregate(results)
```

**FR-2.2** Agrega resultados en formato unificado:
```json
{
  "issues": [
    {
      "id": "SEC-001",
      "tool": "semgrep",
      "rule": "python.lang.security.audit.dangerous-system-call",
      "severity": "CRITICAL",
      "file": "src/utils.py",
      "line": 45,
      "message": "SQL Injection vulnerability",
      "snippet": "cursor.execute(f\"SELECT...\")"
    }
  ]
}
```

**FR-2.3** Configura herramientas vía `qodabit.yaml`:
```yaml
version: "2.0"

tools:
  semgrep:
    enabled: true
    config: "p/owasp-top-ten"
  gitleaks:
    enabled: true
  radon:
    enabled: true
    thresholds:
      cyclomatic_max: 10
  pip_audit:
    enabled: true

gates:
  pr:
    critical: 0
    high: 0
    secrets: 0
```

---

### FR-3: Production-Ready Score

**FR-3.1** Calcula score 0-100% basado en:

```python
def calculate_score(issues: list[Issue]) -> int:
    base = 100

    # Penalizaciones
    for issue in issues:
        if issue.severity == "CRITICAL":
            base -= 15
        elif issue.severity == "HIGH":
            base -= 8
        elif issue.severity == "MEDIUM":
            base -= 3
        elif issue.severity == "LOW":
            base -= 1

    return max(0, base)
```

**FR-3.2** Categorías de score:
```
90-100%  → 🟢 Production Ready
70-89%   → 🟡 Almost Ready (fix criticals)
50-69%   → 🟠 Needs Work
0-49%    → 🔴 Not Ready
```

**FR-3.3** Muestra delta después de fixes:
```
Score: 84% (+12% desde último scan)
```

---

### FR-4: AI Explain

**FR-4.1** Cuando usuario pide explicación:
```python
prompt = f"""
Explica este problema de seguridad de forma clara y concisa:

Archivo: {issue.file}:{issue.line}
Código:
```
{issue.snippet}
```

Problema detectado: {issue.message}
Regla: {issue.rule}

Explica:
1. Qué es el problema (1-2 oraciones)
2. Por qué es peligroso (ejemplo de ataque)
3. Cómo solucionarlo (código corregido)
"""
```

**FR-4.2** Respuesta formateada para terminal:
```
📋 SQL Injection en db.py:45

❌ Problema: [explicación]

💀 Riesgo: [ejemplo de ataque]

✅ Solución:
```python
[código corregido]
```

¿Aplicar fix? (s/n)
```

---

### FR-5: AI Fix

**FR-5.1** Genera código corregido con AI

**FR-5.2** Muestra diff antes de aplicar:
```diff
- query = f"SELECT * FROM users WHERE id = {user_id}"
+ query = "SELECT * FROM users WHERE id = %s"
- cursor.execute(query)
+ cursor.execute(query, (user_id,))
```

**FR-5.3** Aplica fix automáticamente si usuario confirma

**FR-5.4** Re-escanea después del fix para validar

**FR-5.5** **IMPORTANTE:** El fix DEBE pasar validación determinística
- AI sugiere el fix
- Semgrep/Gitleaks validan que el fix funciona
- Si sigue detectando issue → avisar al usuario

---

### FR-6: Modo Comando (CI/CD)

**FR-6.1** Comandos no-interactivos:
```bash
qodabit check              # Escanea + evalúa gates
qodabit audit              # Solo escanea, muestra resultados
qodabit audit --json       # Output JSON
qodabit audit --gate pr    # Evalúa PR gates
qodabit score              # Solo muestra score
qodabit init               # Crea qodabit.yaml
qodabit version            # Muestra versión
```

**FR-6.2** Exit codes:
```
0 = PASS (gates passed)
1 = FAIL (gates failed)
2 = ERROR (config/runtime error)
```

**FR-6.3** Output JSON para CI:
```json
{
  "score": 72,
  "gates": {
    "status": "FAIL",
    "failed": ["critical", "secrets"]
  },
  "summary": {
    "critical": 2,
    "high": 1,
    "medium": 3,
    "low": 5
  },
  "issues": [...]
}
```

---

### FR-7: Gates Determinísticos

**FR-7.1** Gates en `qodabit.yaml`:
```yaml
gates:
  pr:
    critical: 0      # FAIL si > 0
    high: 0          # FAIL si > 0
    secrets: 0       # FAIL si > 0
    score_min: 80    # FAIL si score < 80
```

**FR-7.2** Evaluación 100% determinística:
- Basada solo en output de herramientas
- Sin AI en la decisión PASS/FAIL
- Reproducible: mismo código = mismo resultado

---

## 6. Lenguajes Soportados

### MVP (día 1)
- **Python** (Semgrep + Radon + pip-audit)
- **JavaScript/TypeScript** (Semgrep + npm audit)

### Roadmap
- Go, Java, Rust (Semgrep ya los soporta)

---

## 7. Dependencias

### Herramientas CLI (usuario debe instalar)
```bash
# Requeridas
pip install semgrep
pip install gitleaks  # o brew install gitleaks

# Opcionales
pip install radon        # Python complexity
pip install pip-audit    # Python deps
```

### Python packages
```
click>=8.1.0       # CLI framework
rich>=13.0.0       # Terminal UI
anthropic>=0.18.0  # Claude API
pyyaml>=6.0        # Config
```

### API Keys
```
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Requerida para chat/explain/fix
```

---

## 8. Costos

| Componente | Costo |
|------------|-------|
| Semgrep OSS | $0 |
| Gitleaks | $0 |
| Radon | $0 |
| Claude API | ~$10-30/mes (uso moderado) |

**Total MVP: ~$10-30/mes**

---

## 9. Fases de Desarrollo

| Fase | Nombre | Entregable Principal |
|------|--------|----------------------|
| 1 | Foundation | Chat + Scanner funcionando |
| 2 | Score + Gates | Modo CI/CD listo |
| 3 | AI Integration | Explain + Fix con AI |
| 4 | Polish | Tests + Config |
| 5 | Release | PyPI + Launch |

---

### FASE 1: Foundation
**Resultado:** `qodabit` abre chat y escanea con Semgrep/Gitleaks

- [ ] CLI scaffold (Click + Rich)
- [ ] Chat REPL básico
- [ ] Scanner orchestrator (Semgrep + Gitleaks en paralelo)
- [ ] Output unificado

```bash
$ qodabit
> analiza
✓ Semgrep: X issues
✓ Gitleaks: X secrets
```

---

### FASE 2: Score + Gates
**Resultado:** `qodabit check` devuelve PASS/FAIL para CI

- [ ] Aggregator de resultados
- [ ] Production-Ready Score (0-100%)
- [ ] Gate evaluator
- [ ] Modo comando (check, audit, score)

```bash
$ qodabit check
Score: 72% | Gates: FAIL
$ echo $?
1
```

---

### FASE 3: AI Integration
**Resultado:** AI explica y arregla issues

- [ ] Claude/OpenAI API client
- [ ] Comando `explica <ID>`
- [ ] Comando `fix <ID>`
- [ ] Apply fix + re-validate

```bash
> explica SEC-001
📋 SQL Injection en db.py:45
[explicación AI]

> fix SEC-001
✓ Fix aplicado. Score: 84% (+12%)
```

---

### FASE 4: Polish
**Resultado:** CLI production-ready

- [ ] Config file (qodabit.yaml)
- [ ] `qodabit init`
- [ ] Error handling robusto
- [ ] Test suite (pytest)
- [ ] Natural language en chat

```bash
$ qodabit init
✓ Created qodabit.yaml

$ pytest
====== 20 passed ======
```

---

### FASE 5: Release
**Resultado:** `pip install qodabit` funciona

- [ ] PyPI publish
- [ ] README.md
- [ ] GitHub Actions CI/CD
- [ ] Demo video

```bash
$ pip install qodabit
$ qodabit --version
QodaBit v0.2.0
```

---

## 10. Criterios de Éxito

### Funcionales
- [ ] Chat interactivo funciona
- [ ] Detecta issues con Semgrep/Gitleaks
- [ ] AI explica y genera fixes
- [ ] Score calcula correctamente
- [ ] Gates funcionan en CI

### Experiencia
- [ ] < 5 segundos para scan típico
- [ ] Explicaciones claras (no jerga)
- [ ] Fixes que realmente funcionan

### Adopción (mes 1)
- [ ] 200 instalaciones
- [ ] 20 usuarios activos
- [ ] 50 issues explicados con AI
- [ ] 10 testimonios

---

## 11. Lo que NO es MVP

| Feature | Por qué no | Versión |
|---------|------------|---------|
| IDE Extension | Complejidad UI | v0.3 |
| Evidence Pack | Enterprise | v0.4 |
| SBOM/SLSA | Enterprise | v0.4 |
| Multi-repo | Complejidad | v0.5 |
| Dashboard web | Diferente producto | v1.0 |

---

## 12. Ejemplo Completo

```bash
$ cd mi-proyecto-python
$ qodabit

╭─────────────────────────────────────────────╮
│  QodaBit v0.2.0 - Security Copilot          │
│  Escribe 'ayuda' para ver comandos          │
╰─────────────────────────────────────────────╯

> analiza

Escaneando...
✓ Semgrep (2.3s) - 47 archivos
✓ Gitleaks (0.8s) - secrets check
✓ Radon (0.5s) - complexity

═══════════════════════════════════════════════
  Production-Ready Score: 68% 🟠
═══════════════════════════════════════════════

🔴 CRITICAL (2)
   SEC-001  SQL Injection           src/db.py:45
   SEC-002  Hardcoded API Key       src/config.py:12

🟠 HIGH (1)
   CMP-001  Cyclomatic complexity   src/utils.py:89
            (15, max allowed: 10)

🟡 MEDIUM (2)
   SEC-003  Weak crypto (MD5)       src/auth.py:23
   DEP-001  Vulnerable package      requests==2.25.0

> explica SEC-001

📋 SQL Injection en src/db.py:45

Tu código actual:
┌────────────────────────────────────────────┐
│  44 │  def get_user(user_id):              │
│  45 │      query = f"SELECT * FROM users   │
│     │               WHERE id = {user_id}"  │
│  46 │      cursor.execute(query)           │
└────────────────────────────────────────────┘

❌ PROBLEMA:
El parámetro user_id se inserta directamente en el query SQL.
Esto permite SQL Injection.

💀 EJEMPLO DE ATAQUE:
Si user_id = "1; DROP TABLE users; --"
El query se convierte en:
SELECT * FROM users WHERE id = 1; DROP TABLE users; --

✅ SOLUCIÓN:
Usar queries parametrizados:
┌────────────────────────────────────────────┐
│  44 │  def get_user(user_id):              │
│  45 │      query = "SELECT * FROM users    │
│     │               WHERE id = %s"         │
│  46 │      cursor.execute(query, (user_id,))│
└────────────────────────────────────────────┘

¿Aplicar este fix? (s/n): s

Aplicando fix...
✓ Archivo modificado: src/db.py
✓ Re-escaneando...
✓ SEC-001 resuelto

Score: 76% (+8%) 🟡

> siguiente

📋 SEC-002: Hardcoded API Key en src/config.py:12
...

> check

Evaluando gates...

Gates: FAIL
├── critical: 1 (threshold: 0) ❌
├── high: 1 (threshold: 0) ❌
├── secrets: 1 (threshold: 0) ❌
└── score: 76% (min: 80%) ❌

Arregla los issues críticos antes de merge.

> salir

Hasta luego! 👋
```

---

## Resumen

```
┌─────────────────────────────────────────────────────────────┐
│                     QodaBit MVP v2                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Qué: Chat de seguridad para AI Devs                        │
│                                                              │
│  Cómo:                                                       │
│  └── Semgrep + Gitleaks (detección)                         │
│  └── Claude API (explicación + fix)                         │
│  └── Production-Ready Score                                  │
│  └── Gates para CI                                          │
│                                                              │
│  Para quién: Devs que usan Cursor/Claude Code               │
│                                                              │
│  Diferenciador: Nadie más ofrece chat + fix + score         │
│                                                              │
│  Timeline: 5 semanas                                        │
│                                                              │
│  Costo: ~$10-30/mes (Claude API)                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**QodaBit MVP v2 — Listo para validación con maestro**
