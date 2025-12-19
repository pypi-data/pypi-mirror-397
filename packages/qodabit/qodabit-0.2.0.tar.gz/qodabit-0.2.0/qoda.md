# QodaBit — Especificación de Producto v2.1 (Enterprise-Grade)

---

# FASE 1: ESPECIFICACIÓN DE PRODUCTO

---

## 1. Resumen General

**QodaBit** es un auditor de código enterprise-grade que opera localmente, diseñado para validar código, generar evidencia audit-ready y aplicar gates deterministas para cualquier desarrollador—desde AI Devs usando Claude Code/Cursor hasta ingenieros senior trabajando en entornos Fortune 100-500.

### Qué es

Un sistema integral de auditoría de código que opera como:
- **Herramienta CLI** para auditorías desde terminal
- **Extensión IDE** (VS Code/Cursor) para validación en tiempo real
- **Integración CI/CD** para gates automatizados
- **Servidor MCP** para integración con Claude Code
- **Generador de Evidence Pack** para auditorías enterprise

### Problema que resuelve

1. **AI Devs** construyen rápido con LLMs pero no pueden validar si el código es production-ready
2. **Desarrolladores junior** carecen de experiencia para detectar vulnerabilidades de seguridad
3. **Ingenieros senior** necesitan evidencia audit-ready para compliance
4. **Equipos** pierden tiempo en code reviews manuales detectando problemas prevenibles
5. **Vibe coding** produce prototipos funcionales que fallan auditorías enterprise
6. **Auditorías** requieren evidencia verificable, no solo reportes de "score"

### Para quién es

- **AI Developers** construyendo con Claude Code, Cursor, GPT
- **Desarrolladores Junior/Mid** aprendiendo patrones enterprise
- **Ingenieros Senior** requiriendo evidencia audit-ready
- **Equipos de ingeniería** desde startups hasta Fortune 500
- **Equipos DevSecOps** aplicando estándares de seguridad
- **Equipos GRC/Compliance** necesitando evidencia formal

### Principio Arquitectónico Central

```
┌─────────────────────────────────────────────────────────────┐
│                    DETERMINISTA = JUEZ                       │
│         (SAST, SCA, Secrets, Policy Engine, Gates)          │
│                    Decide PASS/FAIL                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI = CIRUJANO                           │
│              (Explicación, Remediación, PRs)                │
│                  Sugiere, NO decide                          │
└─────────────────────────────────────────────────────────────┘
```

- Los **gates deterministas** (SAST, SCA, Secrets, Policy Engine) deciden PASS/FAIL
- La **AI** solo sugiere remediaciones, explica problemas y genera PRs
- La AI **nunca** es fuente de verdad para certificación
- Solo los checks deterministas pueden bloquear merges/releases

### Impacto de negocio esperado

- **Reducir deuda técnica** 60-80% mediante detección temprana
- **Prevenir brechas de seguridad** detectando vulnerabilidades OWASP Top 10
- **Acelerar auditorías** con Evidence Packs audit-ready
- **Habilitar AI Devs** para producir código production-ready sin conocimiento técnico profundo
- **Eliminar bottlenecks** de code review manual
- **Facilitar compliance** con evidencia verificable (NO certificar, facilitar)

---

## 2. Goals (Objetivos)

### Lo que QodaBit SÍ logrará:

1. **Gates deterministas con bloqueo real**
   - PR Gates: secrets=0, SAST critical/high=0, SCA critical=0
   - Release Gates: SBOM presente, Evidence Pack generado y firmado
   - Bloqueo automático de merge/release si gates fallan
   - Sin excepciones no documentadas

2. **Evidence Pack por release**
   - SBOM formal (SPDX/CycloneDX)
   - Provenance del build (SLSA Level 2+)
   - Firma/attestation del artefacto y reporte
   - Trazabilidad PR → gates → release
   - Export "auditor friendly"

3. **Validación enterprise en tiempo real**
   - Detectar secretos hardcodeados, SQL injection, XSS
   - Alertas inline mientras el dev escribe código
   - Score de calidad actualizado continuamente
   - Modo Offline y Online para SCA

4. **AI como copiloto de remediación (NO como juez)**
   - Explicaciones contextuales de cada issue detectado
   - Sugerencias de fix con ejemplos
   - Generación de PRs de remediación
   - AI nunca ve secretos, nunca certifica

5. **Generación de evidencia audit-ready**
   - Reportes auditables mapeados a OWASP/CWE/ASVS
   - Evidencia inmutable con hash y firma
   - NO "certificamos SOC2/ISO" — generamos evidencia para facilitar auditorías

6. **Integración natural con flujo de desarrollo**
   - CLI para terminal
   - Extensión VS Code/Cursor
   - MCP server para Claude Code
   - Pre-commit hooks
   - CI/CD gates

7. **Análisis multi-capa**
   - **SAST** (Static Application Security Testing)
   - **SCA** (Software Composition Analysis) - dependencias y CVEs
   - **Secrets Scanning** - detección de secretos hardcodeados
   - **Policy Engine** - reglas enterprise customizables
   - **Dependency Impact** - detección de acoplamiento entre archivos
   - **LLM Validator** (opcional) - análisis semántico para remediación

8. **Performance enterprise**
   - Análisis < 30s por archivo
   - Soporte repos medianos (hasta 50K LOC inicialmente)
   - Cache incremental

---

## 3. Non-Goals (Fuera de Alcance v0.1-0.3)

### Lo que QodaBit NO hará:

1. **No certifica compliance**
   - NO "certificamos SOC2/ISO/NIST"
   - SOC 2 e ISO evalúan controles operando en el tiempo, no código
   - QodaBit genera evidencia audit-ready, el auditor certifica

2. **No es SaaS**
   - No sube código a servidores externos (excepto LLM opcional)
   - No requiere cuenta cloud
   - Todo corre local o infra propia

3. **No es auto-fix masivo**
   - No reescribe código automáticamente sin confirmación
   - AI sugiere fixes, el dev decide aplicarlos
   - Re-validación determinista después de cada fix

4. **AI no es fuente de verdad**
   - AI puede sugerir y explicar
   - Solo los checks deterministas pueden marcar PASS/FAIL
   - AI nunca ve secretos detectados

5. **No es deployment tool**
   - No despliega aplicaciones
   - No maneja infraestructura

6. **No reemplaza tests**
   - No genera tests automáticamente (fase futura)
   - Complementa testing, no lo sustituye

7. **No es multi-repo inicialmente**
   - v0.1-0.3 enfocado en repos individuales
   - Monorepos en roadmap futuro

8. **No soporta todos los lenguajes día 1**
   - Inicio: Python + TypeScript/JavaScript
   - Otros lenguajes: roadmap por demanda

---

## 4. Target Users (Usuarios Objetivo)

### Perfil 1: AI Developer

**Características:**
- Construye con Claude Code, Cursor, ChatGPT
- Conocimiento técnico limitado/medio
- Necesita validación constante
- Busca aprender mientras construye

**Necesidades de QodaBit:**
- Gates que digan SI/NO claro
- Prevención en tiempo real
- Explicaciones educativas (vía AI)
- Conversión vibe → enterprise con evidencia

### Perfil 2: Junior/Mid Developer

**Características:**
- 1-3 años experiencia
- Conoce sintaxis, no patrones enterprise
- Comete errores de seguridad por desconocimiento

**Necesidades de QodaBit:**
- Gates de bloqueo antes de merge
- Aprendizaje de buenas prácticas
- Feedback inmediato
- Referencias a estándares

### Perfil 3: Senior Engineer / AppSec

**Características:**
- 5+ años experiencia
- Necesita evidencia audit-ready
- Busca eficiencia, no educación
- Quiere gates + evidencia, no opiniones

**Necesidades de QodaBit:**
- Gates deterministas configurables
- Evidence Pack por release
- Integración CI/CD
- Customización de políticas
- Reportes auditables

### Perfil 4: Engineering Team / CTO

**Características:**
- Equipos 3-50 personas
- Necesitan estándares consistentes
- Velocidad sin incendios
- Deben cumplir auditorías

**Necesidades de QodaBit:**
- Policy enforcement uniforme
- Gates que bloquean automáticamente
- Evidence Pack para releases
- Métricas de equipo
- Reliability + operabilidad

### Perfil 5: GRC / Compliance Team

**Características:**
- Responsables de auditorías
- Necesitan evidencia formal
- Gestionan excepciones

**Necesidades de QodaBit:**
- Evidence Pack audit-ready
- Export "auditor friendly"
- Excepciones con aprobador y expiración
- Trazabilidad completa
- Mapeo a estándares (ASVS/SSDF)

---

## 5. Success Metrics (Métricas de Éxito)

### Year 1 Targets (Realistas)

```yaml
year_1_targets:
  free_users: 2,000
  paid_users: 100
  arr: $50,000
  false_positive_rate: "<10%"
  nps: ">30"

year_2_targets:
  free_users: 10,000
  paid_users: 500
  arr: $200,000
  false_positive_rate: "<5%"
  nps: ">50"
```

### Adoption Metrics
- **Active users**: 500 devs en primeros 3 meses
- **Daily audits**: 2,000+ análisis/día
- **Retention**: 50%+ usuarios activos mes a mes

### Quality Metrics
- **Issues detectados**: 80%+ de vulnerabilidades críticas encontradas
- **False positives**: <10% (Year 1), <5% (Year 2)
- **Performance**: <30s análisis promedio por archivo
- **Crash rate**: <0.1%
- **Gate accuracy**: 99%+ (sin falsos PASS en criticals)

### Business Impact
- **Time saved**: 40%+ reducción en tiempo de code review
- **Security improvement**: 70%+ reducción de vulnerabilidades en producción
- **Audit readiness**: 90%+ de Evidence Packs aceptados en primera revisión
- **Gate adoption**: 80%+ de releases pasan por gates

---

## 6. User Stories

### US-1: AI Dev validando código con gates

**Como** AI Dev usando Cursor
**Quiero** que QodaBit bloquee mi commit si tiene issues críticos
**Para** no pushear código inseguro sin saberlo

**Acceptance Criteria:**
- Gate FAIL si secrets > 0
- Gate FAIL si SAST critical/high > 0
- Mensaje claro de qué arreglar
- AI sugiere fix (pero no decide PASS/FAIL)

### US-2: Junior dev aprendiendo con remediación AI

**Como** desarrollador junior
**Quiero** que la AI me explique por qué mi código falla los gates
**Para** mejorar mis habilidades y evitar repetir errores

**Acceptance Criteria:**
- Explicaciones educativas con ejemplos
- AI genera PR de fix sugerido
- Referencias a documentación oficial (OWASP, etc.)
- Re-validación automática después de fix

### US-3: Senior eng generando Evidence Pack

**Como** ingeniero senior
**Quiero** generar un Evidence Pack audit-ready por release
**Para** facilitar auditorías sin trabajo manual

**Acceptance Criteria:**
- Evidence Pack incluye SBOM (SPDX/CycloneDX)
- Incluye provenance SLSA
- Firma digital del pack
- Mapeo a controles ASVS/OWASP
- Hash inmutable

### US-4: Team lead aplicando gates

**Como** tech lead
**Quiero** aplicar gates que bloqueen merges con issues críticos
**Para** mantener calidad uniforme sin review manual

**Acceptance Criteria:**
- Gates configurables en `qodabit.yaml`
- PR bloqueado automáticamente si gate FAIL
- Dashboard de métricas del equipo
- Excepciones documentadas con aprobador

### US-5: DevOps integrando gates en CI/CD

**Como** ingeniero DevOps
**Quiero** bloquear releases sin Evidence Pack completo
**Para** asegurar trazabilidad de cada release

**Acceptance Criteria:**
- Release gate: SBOM presente
- Release gate: Evidence Pack firmado
- Exit code non-zero bloquea pipeline
- Artefactos en CI artifacts

### US-6: GRC exportando evidencia para auditor

**Como** responsable de compliance
**Quiero** exportar Evidence Packs en formato auditor-friendly
**Para** presentar a auditores externos sin reformatear

**Acceptance Criteria:**
- Export PDF/JSON estructurado
- Mapeo a controles SOC2/NIST visible
- Excepciones documentadas con justificación
- Trazabilidad PR → gate → release

### US-7: Dev revisando impacto de cambios

**Como** desarrollador
**Quiero** saber qué archivos se ven afectados por mis cambios
**Para** incluirlos en mi review y evitar bugs en producción

**Acceptance Criteria:**
- Ver archivos con alto acoplamiento a mis cambios
- Warning en PR si hay impacto no revisado
- Razones claras del acoplamiento (import, co-change, shared state)
- Recomendación de archivos adicionales a revisar

---

## 7. Promesa Comercial

### Lo que QodaBit SÍ promete:

> "QodaBit deja tu repo audit-ready con evidencia verificable y gates reproducibles."

- Gates deterministas que bloquean código inseguro
- Evidence Pack por release con SBOM + provenance + firma
- AI como copiloto de remediación (no como juez)
- Trazabilidad completa para auditorías

### Lo que QodaBit NO promete:

> ~~"Garantiza pasar auditoría SOC 2/ISO"~~

- Auditoría incluye procesos y operación sostenida
- QodaBit genera evidencia, el auditor certifica
- No reemplazamos auditoría, la facilitamos

---

## 8. Policy Packs (Segmentación por Buyer)

### Filosofía

**El motor es el mismo. Cambia el perfil, el lenguaje, y el paquete de evidencia.**

### Pack 1: AppSec (CISO / Security Team)

**Objetivo:** Reducción de riesgo inmediata, gates duros

**Template:** `qodabit init --template appsec-strict`

```yaml
version: "2.0"
template: "appsec-strict"

gates:
  pr:
    secrets: 0
    sast_critical: 0
    sast_high: 0
    sca_critical_runtime: 0
    sca_high_runtime: 0

  release:
    pr_gates_passed: true
    sbom_present: true
    evidence_pack_signed: true
    provenance_generated: true

policies:
  security:
    deny_hardcoded_secrets: true
    require_input_validation: true
    block_eval_usage: true
    block_dangerous_imports: true

  dependencies:
    fail_on_critical_cve_runtime: true
    fail_on_high_cve_runtime: true
    fail_on_critical_cve_dev: true
    max_cve_age_days: 30

  compliance:
    enforce_owasp_top10: true
    generate_asvs_mapping: true
```

**Target:** CISOs, AppSec Engineers, Fintech/Healthcare

### Pack 2: CTO (Startup / Fast-move)

**Objetivo:** Velocidad sin incendios, balance pragmático

**Template:** `qodabit init --template cto-balanced`

```yaml
version: "2.0"
template: "cto-balanced"

gates:
  pr:
    secrets: 0
    sast_critical: 0
    sast_high: 3
    sca_critical_runtime: 0

  release:
    pr_gates_passed: true
    sbom_present: true
    evidence_pack_signed: false

policies:
  security:
    deny_hardcoded_secrets: true
    require_input_validation: true

  quality:
    max_function_complexity: 15
    max_function_lines: 200

  dependencies:
    fail_on_critical_cve_runtime: true
    fail_on_high_cve_runtime: false
    warn_on_unmaintained: true

  coverage:
    minimum_new_code: 70
```

**Target:** CTOs Startup, Engineering Managers, Tech Leads

### Pack 3: GRC (Compliance / Audit-Ready)

**Objetivo:** Evidencia formal, trazabilidad completa

**Template:** `qodabit init --template grc-audit-ready`

```yaml
version: "2.0"
template: "grc-audit-ready"

gates:
  pr:
    secrets: 0
    sast_critical: 0
    sast_high: 0
    sca_critical_runtime: 0

  release:
    pr_gates_passed: true
    sbom_present: true
    evidence_pack_generated: true
    evidence_pack_signed: true
    provenance_generated: true
    all_exceptions_documented: true

policies:
  compliance:
    enforce_owasp_top10: true
    generate_asvs_mapping: true
    generate_ssdf_mapping: true
    require_exception_approval: true
    exception_max_duration_days: 90

  audit:
    immutable_logs: true
    log_retention_days: 365

  evidence:
    sbom_format: ["spdx", "cyclonedx"]
    provenance_level: "slsa-level-2"
    sign_with: "sigstore"

dependency_impact:
  enabled: true
  include_in_evidence: true
```

**Target:** Compliance Officers, GRC Teams, Regulated Industries

### Pack Inheritance (Herencia)

```yaml
# Pack custom que hereda de otro
version: "2.0"
extends: "appsec-strict"

overrides:
  gates:
    pr:
      sast_high: 0  # Más estricto
  policies:
    compliance:
      pci_dss_mapping: required
```

### Comparación de Packs

| Feature | AppSec | CTO | GRC |
|---------|:------:|:---:|:---:|
| SAST Critical Block | ✅ | ✅ | ✅ |
| SAST High Block | ✅ | ⚠️ 3 max | ✅ |
| SCA High Block | ✅ | ❌ warn | ✅ |
| Dev Deps CVE Block | ✅ | ❌ | ✅ |
| Evidence Pack Signed | ✅ | Optional | ✅ |
| SLSA Provenance | ✅ | Optional | ✅ |
| Exception Workflow | Standard | Light | Strict |
| ASVS Mapping | ✅ | ❌ | ✅ |
| SSDF Mapping | ❌ | ❌ | ✅ |
| Dependency Impact | Warn | Warn | In Evidence |

---

## 9. Pricing Strategy

```yaml
pricing:
  free:
    price: $0
    features:
      - 1 proyecto
      - Gates básicos (SAST, secrets)
      - Sin AI suggestions
      - Sin Evidence Pack
      - Community support

  pro:
    price: $19/dev/month
    features:
      - Unlimited proyectos
      - Full gates + SCA
      - AI suggestions
      - Evidence Pack básico (SBOM)
      - Email support

  team:
    price: $49/dev/month
    features:
      - Todo de Pro
      - Evidence Pack completo (SBOM + SLSA + Sigstore)
      - Policy Packs customizables
      - Team dashboard
      - CI/CD integrations
      - Priority support

  enterprise:
    price: Custom (desde $500/month)
    features:
      - Todo de Team
      - On-premise / air-gapped
      - Custom rules engine
      - SSO/SAML
      - Audit trail inmutable
      - SLA 99.9%
      - Dedicated support
```

---

# FASE 2: REQUISITOS FUNCIONALES Y NO FUNCIONALES

---

## 1. Requisitos Funcionales (FR)

### FR-1: Análisis Estático de Código (SAST)

**FR-1.1** El sistema DEBE analizar archivos Python (.py) y TypeScript/JavaScript (.ts, .js, .tsx, .jsx)

**FR-1.2** El sistema DEBE detectar:
- Variables hardcodeadas (API keys, passwords, tokens)
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) patterns
- Uso de `eval()` y funciones peligrosas
- Importaciones inseguras
- Manejo inadecuado de errores (try-catch vacíos)
- Code smells (funciones >300 líneas, complejidad ciclomática >15)

**FR-1.3** El sistema DEBE generar un AST (Abstract Syntax Tree) completo del código analizado

**FR-1.4** El análisis DEBE completarse en <30 segundos por archivo de hasta 1000 líneas (excluyendo Dependency Impact, que corre en paralelo)

**FR-1.5** El sistema DEBE asignar severidad a cada issue:
- `CRITICAL`: Vulnerabilidades explotables, secrets expuestos
- `HIGH`: Riesgos de seguridad, violaciones compliance
- `MEDIUM`: Code smells, malas prácticas
- `LOW`: Sugerencias de mejora, optimizaciones

---

### FR-2: Análisis de Dependencias (SCA) - DUAL MODE

**FR-2.1** El sistema DEBE soportar dos modos de operación:

**Modo Offline:**
- Usa base de datos local de CVEs (descargable/actualizable)
- No requiere conexión a internet
- Reporta "freshness" del feed CVE en el reporte
- Comando: `qodabit db update` para actualizar DB local

**Modo Online:**
- Consulta APIs en vivo (NVD, GitHub Advisory)
- Caching local con TTL configurable
- Rate limiting automático
- Fallback a modo offline si APIs fallan

**FR-2.2** El sistema DEBE leer y analizar:
- `requirements.txt`, `pyproject.toml`, `Pipfile` (Python)
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` (Node/JS)

**FR-2.3** El sistema DEBE detectar y clasificar:
- **CVEs críticos en runtime deps** → FAIL (bloquea)
- **CVEs críticos en dev deps** → WARNING
- **Paquetes sin mantenimiento** → WARNING (no fail por defecto)
- **Licencias incompatibles** → FAIL (si policy lo requiere)

**FR-2.4** El sistema NO DEBE fallar por "dependencia >12 meses" como regla única. En su lugar:
- Evaluar por CVEs explotables
- Evaluar por licencia
- Evaluar por mantenimiento real
- Evaluar por exposición en runtime vs dev

**FR-2.5** El sistema DEBE generar SBOM (Software Bill of Materials) en formato:
- SPDX (JSON/Tag-Value)
- CycloneDX (JSON/XML)

**FR-2.6** El sistema DEBE reportar "CVE DB freshness" en cada análisis:
```json
{
  "cve_database": {
    "mode": "offline",
    "last_updated": "2025-01-15T10:00:00Z",
    "freshness_days": 2,
    "warning": "CVE database is 2 days old. Run 'qodabit db update' for latest."
  }
}
```

---

### FR-3: Secrets Scanning

**FR-3.1** El sistema DEBE detectar secretos hardcodeados:
- API keys (OpenAI, AWS, GCP, Azure, Stripe, etc.)
- Passwords y credentials
- Private keys (SSH, PGP, certificates)
- Tokens (JWT, OAuth, Bearer)
- Connection strings

**FR-3.2** El sistema DEBE tener tasa de detección >95% para patrones conocidos

**FR-3.3** Los secretos detectados NUNCA deben:
- Aparecer en logs
- Enviarse a LLM
- Guardarse en cache sin redacción
- Mostrarse completos en reportes (solo primeros/últimos 4 chars)

**FR-3.4** El sistema DEBE soportar `.qodabit-ignore` para falsos positivos documentados

---

### FR-4: Policy Engine (Motor de Políticas)

**FR-4.1** El sistema DEBE soportar configuración vía archivo `qodabit.yaml`

**FR-4.2** El archivo `qodabit.yaml` DEBE permitir definir:

```yaml
version: "2.0"

project:
  name: "project-name"

mode:
  sca: "offline" | "online" | "hybrid"

gates:
  pr:
    secrets: 0
    sast_critical: 0
    sast_high: 0
    sca_critical: 0
    tests_passing: true

  release:
    pr_gates_passed: true
    sbom_present: true
    evidence_pack_signed: true
    provenance_generated: true

paths:
  include: ["src/", "backend/"]
  exclude: ["node_modules/", ".venv/", "tests/"]

policies:
  security:
    deny_hardcoded_secrets: true
    max_function_complexity: 15
    require_input_validation: true

  dependencies:
    fail_on_critical_cve_runtime: true
    fail_on_critical_cve_dev: false
    fail_on_license_incompatible: true
    warn_on_unmaintained: true

  compliance:
    enforce_owasp_top10: true
    generate_asvs_mapping: true

exceptions:
  - id: "EXC-001"
    rule: "sast_high"
    file: "legacy/old_code.py"
    reason: "Legacy code, scheduled for removal Q2"
    approved_by: "security@company.com"
    expires: "2025-06-01"
```

**FR-4.3** El sistema DEBE validar sintaxis del archivo de configuración antes de ejecutar análisis

**FR-4.4** El sistema DEBE soportar templates de políticas:
- `template: "appsec-strict"`
- `template: "cto-balanced"`
- `template: "grc-audit-ready"`

**FR-4.5** Las excepciones DEBEN incluir obligatoriamente:
- Justificación
- Aprobador
- Fecha de expiración

**FR-4.6** El sistema DEBE soportar herencia de templates:
```yaml
extends: "appsec-strict"
overrides:
  gates:
    pr:
      sast_high: 0
```

---

### FR-5: Quality Gates

**FR-5.1** El sistema DEBE implementar gates como bloqueos binarios (PASS/FAIL)

**FR-5.2** PR Gates (bloquean merge):

| Gate | Condición FAIL | Default |
|------|----------------|---------|
| secrets | > 0 | Enabled |
| sast_critical | > 0 | Enabled |
| sast_high | > 0 | Enabled |
| sca_critical_runtime | > 0 | Enabled |
| tests_passing | false | Optional |

**FR-5.3** Release Gates (bloquean release):

| Gate | Condición FAIL | Default |
|------|----------------|---------|
| pr_gates_passed | false | Enabled |
| sbom_present | false | Enabled |
| evidence_pack_generated | false | Enabled |
| evidence_pack_signed | false | Optional |
| provenance_generated | false | Optional |

**FR-5.4** El sistema DEBE reportar estado de gates:
```json
{
  "gates": {
    "type": "pr",
    "status": "FAIL",
    "passed": ["sca_critical_runtime", "tests_passing"],
    "failed": ["secrets", "sast_critical"],
    "details": {
      "secrets": {"found": 2, "threshold": 0},
      "sast_critical": {"found": 1, "threshold": 0}
    }
  }
}
```

**FR-5.5** Gates DEBEN ser deterministas y reproducibles:
- Mismo código + misma config = mismo resultado
- Sin dependencia de AI para PASS/FAIL
- Auditable y explicable

---

### FR-6: Evidence Pack Generator

**FR-6.1** El sistema DEBE generar Evidence Pack por release:
```bash
qodabit evidence generate --release v1.0.0 --sign
```

**FR-6.2** El Evidence Pack DEBE contener:

**A) SBOM (Software Bill of Materials)**
- Formato: SPDX y/o CycloneDX
- Todas las dependencias con versiones
- Hashes de cada dependencia
- Licencias

**B) Provenance (SLSA)**
- Builder identity
- Source repository
- Build timestamp
- Build parameters
- Entry point

**C) Scan Reports**
- SAST findings (JSON)
- SCA findings (JSON)
- Secrets scan results (redacted)
- Policy violations

**D) Gate Results**
- PR gates history
- Release gates status
- Exceptions applied (con aprobador)

**E) Attestation**
- Hash SHA-256 de todo el pack
- Firma digital (Sigstore/cosign opcional)
- Timestamp firmado

**FR-6.3** Estructura del Evidence Pack:
```
evidence-pack-v1.0.0/
├── manifest.json          # Incluye schema_version para compatibilidad futura
├── sbom/
│   ├── sbom.spdx.json
│   └── sbom.cyclonedx.json
├── provenance/
│   └── slsa-provenance.json
├── scans/
│   ├── sast-report.json
│   ├── sca-report.json
│   └── secrets-report.json
├── gates/
│   ├── pr-gates-history.json
│   └── release-gates.json
├── exceptions/
│   └── active-exceptions.json
├── attestation/
│   ├── sha256sums.txt
│   ├── signature.sig
│   └── timestamp.tsr
└── README.md
```

**FR-6.4** El sistema DEBE soportar export "auditor-friendly":
```bash
qodabit evidence export --format auditor-pdf --release v1.0.0
```

**FR-6.5** SLSA Provenance Levels:
- v0.2: SLSA Level 2 (build service generates provenance)
- v0.3: SLSA Level 3 objetivo (hardened build platform)

---

### FR-7: LLM Validator (Remediación AI - NO Autoritativo)

**FR-7.1** El sistema DEBE permitir habilitar/deshabilitar LLM vía config

**FR-7.2** El sistema DEBE soportar múltiples providers:
- Anthropic Claude (vía API)
- OpenAI GPT-4 (vía API)
- Modelos locales (Ollama: Llama, Mistral)

**FR-7.3** **PRINCIPIO FUNDAMENTAL:** La AI NO es fuente de verdad
- AI puede sugerir y explicar
- AI puede generar PRs de fix
- Solo los checks deterministas pueden marcar PASS/FAIL
- AI NUNCA decide si un gate pasa o falla

**FR-7.4** Cuando habilitado, el LLM DEBE:
- Explicar issues en lenguaje humano
- Sugerir fixes específicos
- Generar PRs de remediación
- Proporcionar contexto educativo

**FR-7.5** El sistema DEBE garantizar seguridad de AI:
- AI NUNCA ve secretos detectados (redaction automática)
- AI NUNCA sube código por default
- Límite de tokens/costo configurable
- Timeout 30s por archivo
- Fallback a análisis estático si LLM falla
- Rate limiting configurable:

```yaml
llm:
  provider: "anthropic"
  rate_limit:
    requests_per_minute: 20
    tokens_per_minute: 40000
    max_retries: 3
    retry_backoff_ms: 1000
```

**FR-7.6** Flujo de remediación con AI:
```
1. Gate FAIL detectado (determinista)
2. Usuario solicita "explain" o "fix"
3. AI recibe código CON SECRETOS REDACTADOS
4. AI sugiere fix
5. Usuario aplica fix
6. Re-validación DETERMINISTA
7. Gate re-evaluado (sin AI)
```

---

### FR-8: Sistema de Reportes

**FR-8.1** El sistema DEBE generar reportes en formatos:
- Markdown (`.md`)
- JSON (`.json`)
- HTML (`.html`)
- PDF (v0.2+)

**FR-8.2** El reporte DEBE incluir:
- Estado de gates (PASS/FAIL)
- Total de issues por severidad
- Lista detallada de issues con:
  - Archivo y línea afectada
  - Descripción del problema
  - Severidad
  - Regla violada
  - Sugerencia de fix
  - Referencia a estándar (OWASP, CWE, ASVS)
- SBOM summary
- CVE database freshness
- Timestamp y versión de QodaBit
- Hash SHA-256 del reporte

**FR-8.3** El reporte JSON DEBE seguir estructura:
```json
{
  "version": "2.1.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "project": "my-project",
  "gates": {
    "type": "pr",
    "status": "FAIL",
    "passed": ["sca_critical"],
    "failed": ["secrets"]
  },
  "summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 8
  },
  "cve_database": {
    "mode": "offline",
    "freshness_days": 2
  },
  "issues": [],
  "sbom_summary": {
    "total_dependencies": 127,
    "direct": 45,
    "transitive": 82
  },
  "hash": "sha256:a3f5b8c..."
}
```

---

### FR-9: CLI (Command Line Interface)

**FR-9.1** El sistema DEBE proveer ejecutable `qodabit` con comandos:

```bash
# Análisis y Gates
qodabit audit                    # Audita directorio actual
qodabit audit --gate pr          # Evalúa PR gates
qodabit audit --gate release     # Evalúa release gates
qodabit gate status              # Muestra estado de gates

# Evidence Pack
qodabit evidence generate --release <tag>
qodabit evidence sign --release <tag>
qodabit evidence export --format auditor-pdf

# SBOM
qodabit sbom generate --format spdx
qodabit sbom generate --format cyclonedx

# SCA Database
qodabit db update                # Actualiza CVE database local
qodabit db status                # Muestra freshness de DB

# Dependency Impact
qodabit impact analyze           # Analiza acoplamiento
qodabit impact show <file>       # Muestra impacto de archivo
qodabit impact pr                # Impacto de cambios staged

# Configuración
qodabit init                     # Crea qodabit.yaml template
qodabit init --template appsec-strict
qodabit config validate

# Reportes
qodabit report --format json
qodabit report --format markdown

# AI Remediation
qodabit fix <issue-id>
qodabit explain <issue-id>

# CI/CD
qodabit ci-check
qodabit ci-check --gate pr
qodabit ci-check --gate release

# Utilidades
qodabit version
qodabit doctor
```

**FR-9.2** El CLI DEBE retornar exit codes:
- `0`: Gates PASS
- `1`: Gates FAIL (issues críticos)
- `2`: Error de configuración
- `3`: Error de ejecución

**FR-9.3** El CLI DEBE soportar flags globales:
- `--config <path>`: Archivo config custom
- `--mode offline|online`: Modo SCA
- `--verbose`: Output detallado
- `--quiet`: Solo errores críticos
- `--no-color`: Sin colores ANSI
- `--json`: Output JSON para parsing

---

### FR-10: Extensión IDE (VS Code / Cursor)

**FR-10.1** La extensión DEBE mostrar estado de gates en statusbar

**FR-10.2** La extensión DEBE mostrar issues inline en el editor:
- Subrayado de código problemático
- Tooltip con descripción del issue
- Quick fix action cuando disponible (via AI)

**FR-10.3** La extensión DEBE proveer panel conversacional con:
- Estado de gates (PASS/FAIL)
- Lista de issues por severidad
- Botón "Fix with AI" por issue
- Botón "Generate Evidence Pack"

**FR-10.4** La extensión DEBE ejecutar análisis:
- On save (opcional, configurable)
- On demand (comando manual)

---

### FR-11: MCP Server (Claude Code Integration)

**FR-11.1** El sistema DEBE proveer servidor MCP con herramientas:

```json
{
  "tools": [
    {
      "name": "qodabit_gate_check",
      "description": "Check PR or release gates",
      "parameters": {"gate_type": "pr|release"}
    },
    {
      "name": "qodabit_audit",
      "description": "Run full audit",
      "parameters": {"path": "string"}
    },
    {
      "name": "qodabit_fix_issue",
      "description": "Get AI fix suggestion for issue",
      "parameters": {"issue_id": "string"}
    },
    {
      "name": "qodabit_generate_evidence",
      "description": "Generate Evidence Pack",
      "parameters": {"release_tag": "string"}
    },
    {
      "name": "qodabit_impact",
      "description": "Analyze dependency impact",
      "parameters": {"file": "string"}
    }
  ]
}
```

---

### FR-12: Pre-commit Hooks

**FR-12.1** El sistema DEBE proveer instalador de hooks:
```bash
qodabit hooks install
qodabit hooks uninstall
```

**FR-12.2** El pre-commit hook DEBE:
- Ejecutar PR gates en archivos staged
- Bloquear commit si gates FAIL
- Mostrar resumen claro de qué falló
- Permitir bypass con `--no-verify` (documentado en logs)

---

### FR-13: CI/CD Integration

**FR-13.1** El sistema DEBE proveer GitHub Action:

```yaml
- name: QodaBit Gate Check
  uses: qodabit/action@v2
  with:
    gate: pr
    mode: offline
    fail-on-gate-fail: true

- name: QodaBit Evidence Pack
  uses: qodabit/action@v2
  with:
    command: evidence
    release: ${{ github.ref_name }}
    sign: true
```

**FR-13.2** El sistema DEBE soportar GitLab CI:

```yaml
qodabit-gates:
  image: qodabit/cli:latest
  script:
    - qodabit ci-check --gate pr

qodabit-evidence:
  image: qodabit/cli:latest
  script:
    - qodabit evidence generate --release $CI_COMMIT_TAG
  artifacts:
    paths:
      - evidence-pack-*/
```

---

### FR-14: Dependency Impact Analysis

**FR-14.1** El sistema DEBE detectar acoplamiento entre archivos usando métodos deterministas:

| Método | Descripción | Determinista |
|--------|-------------|--------------|
| Import Graph | Análisis estático de imports/requires | ✅ Sí |
| Git Co-change | Archivos que históricamente cambian juntos | ✅ Sí |
| Shared State | Variables/estado compartido entre módulos | ✅ Sí |

**FR-14.2** El sistema DEBE calcular `coupling_score` basado en:
- **Import directo:** +0.3 si A importa B
- **Co-change frecuente:** +0.4 si cambian juntos >70% del tiempo
- **Estado compartido:** +0.3 si comparten variables globales/estado
- **Valor máximo:** 1.0 (capped). Si la suma excede 1.0, se reporta 1.0

**FR-14.3** Configuración en `qodabit.yaml`:

```yaml
dependency_impact:
  enabled: true

  detection:
    import_graph: true
    import_depth: 2           # Límite de profundidad (evita explosión)
    git_cochange: true
    git_lookback: 100         # Commits a analizar (si repo tiene menos, usa todos)
    shared_state: true

  thresholds:
    high_coupling: 0.7        # >= 0.7 = fuertemente acoplados
    moderate_coupling: 0.4    # 0.4-0.7 = moderadamente acoplados

  actions:
    warn_on_pr: true          # Warning en PR si hay impacto
    require_review: ["high_coupling"]
    block_pr: false           # No bloquea por default
```

**FR-14.4** El sistema DEBE generar output de impacto:

```json
{
  "dependency_impact": {
    "analyzed_files": 45,
    "high_coupling_pairs": 3,
    "moderate_coupling_pairs": 8,
    "impacts": [
      {
        "file_a": "src/auth.py",
        "file_b": "src/session.py",
        "coupling_score": 0.82,
        "classification": "high",
        "reasons": [
          "Import directo: auth.py imports session.py",
          "Co-change: 89% (67/75 commits)",
          "Shared state: user_context, session_token"
        ],
        "recommendation": "Cambios en auth.py requieren review de session.py"
      }
    ]
  }
}
```

**FR-14.5** En PR Gate Check, el sistema DEBE:
- Identificar archivos modificados en el PR
- Calcular archivos impactados por coupling
- Agregar warnings al reporte si `warn_on_pr: true`
- Sugerir reviewers adicionales para archivos acoplados

**FR-14.6** Output en PR Gate:

```json
{
  "gates": {
    "status": "PASS",
    "passed": ["secrets", "sast_critical"],
    "warnings": [
      {
        "type": "dependency_impact",
        "message": "Cambios en src/auth.py impactan 2 archivos con alto acoplamiento",
        "impacted_files": ["src/session.py", "src/middleware/auth_check.py"],
        "recommendation": "Incluir estos archivos en review"
      }
    ]
  }
}
```

**FR-14.7** CLI Commands:

```bash
qodabit impact analyze              # Ver mapa de acoplamiento
qodabit impact show src/auth.py     # Ver impacto de archivo específico
qodabit impact pr                   # Ver impacto de cambios staged
qodabit impact analyze --json       # Output JSON para CI
```

**FR-14.8** El análisis de Dependency Impact es 100% determinista:
- No usa AI para calcular scores
- No depende de estado externo mutable
- Mismo código + misma historia git = mismo resultado
- Los warnings NO bloquean gates (solo informan)

---

## 2. Requisitos No Funcionales (NFR)

### NFR-1: Performance

**NFR-1.1** Análisis estático DEBE completarse en:
- Archivo individual (<1K LOC): <2s
- Proyecto pequeño (<10K LOC): <15s
- Proyecto mediano (<50K LOC): <60s

**NFR-1.2** Consumo de memoria DEBE ser:
- <500MB para proyectos <50K LOC
- <2GB para proyectos grandes

**NFR-1.3** Evidence Pack generation: <30s para proyectos típicos

---

### NFR-2: Security

**NFR-2.1** El sistema NO DEBE:
- Enviar código a servidores externos (excepto LLM si habilitado)
- Guardar secrets detectados en logs (redaction obligatoria)
- Exponer información sensible en reportes

**NFR-2.2** Secrets handling:
- Redacción automática en logs
- Redacción antes de enviar a LLM
- Solo primeros/últimos 4 chars en reportes

**NFR-2.3** Comunicación con APIs externas DEBE usar HTTPS/TLS 1.3

**NFR-2.4** Evidence Pack DEBE incluir firma digital opcional (Sigstore/cosign)

---

### NFR-3: Supply Chain Security

**NFR-3.1** SBOM DEBE cumplir:
- SPDX 2.3+
- CycloneDX 1.4+

**NFR-3.2** Provenance DEBE cumplir:
- SLSA Level 2 (v0.2)
- SLSA Level 3 objetivo (v0.3)

**NFR-3.3** Firmas DEBEN soportar:
- Sigstore/cosign (recomendado)
- GPG (alternativa)

---

### NFR-4: Auditability

**NFR-4.1** Cada análisis DEBE generar log inmutable con:
- Timestamp
- Versión QodaBit
- Configuración usada (hash)
- Gates evaluados y resultados
- Archivos analizados
- Hash del análisis

**NFR-4.2** Trazabilidad completa:
- PR → Gates → Release → Evidence Pack
- Cada paso linkeable

**NFR-4.3** Excepciones DEBEN tener:
- Justificación obligatoria
- Aprobador identificado
- Fecha de expiración
- Auditoría de quién/cuándo aplicó

---

### NFR-5: Determinism

**NFR-5.1** Gates DEBEN ser 100% deterministas:
- Mismo input = mismo output
- Sin dependencia de AI para PASS/FAIL
- Sin dependencia de estado externo mutable

**NFR-5.2** Reproducibilidad:
- Análisis reproducible con mismo código + config
- Evidence Pack verificable independientemente

---

### NFR-6: Compatibility

**NFR-6.1** El sistema DEBE soportar:
- **OS**: Linux, macOS, Windows
- **Python**: 3.9+
- **Node**: 18+
- **VS Code**: 1.85+
- **Cursor**: 0.40+

**NFR-6.2** Binarios DEBEN distribuirse para:
- `x86_64` (Intel/AMD)
- `arm64` (Apple Silicon, ARM servers)

---

## 3. Constraints (Restricciones)

**C-1** El sistema DEBE operar completamente offline para análisis básico (SAST, Secrets, SBOM)

**C-2** SCA puede requerir conectividad para CVE lookup en modo online

**C-3** AI features requieren conectividad (o modelo local)

**C-4** El sistema NO DEBE requerir acceso root/admin para instalación básica

**C-5** Gates NO DEBEN depender de AI para decisiones PASS/FAIL

**C-6** Evidence Pack DEBE ser verificable sin QodaBit (formatos estándar)

---

# FASE 3: ARQUITECTURA Y DISEÑO TÉCNICO

---

## 1. Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────────┐
│                         QodaBit Core                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Scanner   │  │  Analyzers  │  │   Policy    │              │
│  │   Engine    │──│   (SAST,    │──│   Engine    │              │
│  │             │  │  SCA, Sec)  │  │   + Gates   │              │
│  └─────────────┘  └─────────────┘  └──────┬──────┘              │
│                                           │                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────▼──────┐              │
│  │  Evidence   │  │    SBOM     │  │   Gate      │              │
│  │  Pack Gen   │◄─│  Generator  │  │  Evaluator  │              │
│  └──────┬──────┘  └─────────────┘  └─────────────┘              │
│         │                                                        │
│  ┌──────▼──────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Provenance │  │   Signer    │  │  Dependency │              │
│  │  Generator  │  │ (Sigstore)  │  │   Impact    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                         AI Layer (Opcional)                       │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Redaction  │  │     LLM     │  │  Fix PR     │              │
│  │   Engine    │──│   Client    │──│  Generator  │              │
│  │ (Secrets)   │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                          Interfaces                               │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │   CLI   │  │   IDE   │  │   MCP   │  │  CI/CD  │            │
│  │         │  │  Ext.   │  │ Server  │  │ Actions │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Componentes Core

### 2.1 Scanner Engine

**Responsabilidad:** Descubrir y clasificar archivos a analizar

```go
type ScanResult struct {
    Files       []FileInfo
    TotalLines  int
    Languages   map[string]int
    GitInfo     *GitMetadata
}

type FileInfo struct {
    Path         string
    Language     string
    Lines        int
    Hash         string
    LastModified time.Time
}
```

### 2.2 Analyzers

**SAST Analyzer**
- Parser AST por lenguaje
- Pattern matching de vulnerabilidades
- Detección de code smells

**Secrets Analyzer**
- Regex patterns para secrets conocidos
- Entropy analysis para secrets desconocidos

**SCA Analyzer (Dual Mode)**

```go
type SCAConfig struct {
    Mode     string  // "offline" | "online" | "hybrid"
    DBPath   string
    CacheTTL int
}

type SCAResult struct {
    Dependencies []Dependency
    CVEs         []CVEFinding
    Licenses     []LicenseInfo
    DBFreshness  DBFreshnessInfo
}
```

### 2.3 Policy Engine + Gate Evaluator

```go
type GateResult struct {
    Type    GateType  // "pr" | "release"
    Status  GateStatus  // PASS | FAIL
    Passed  []string
    Failed  []string
    Details map[string]GateDetail
}

// Evaluación 100% determinista
func (e *GateEvaluator) Evaluate(findings Findings, config Config) GateResult {
    // Sin llamadas a AI
    // Sin estado externo mutable
}
```

### 2.4 Evidence Pack Generator

```go
type EvidencePack struct {
    Manifest    Manifest
    SBOM        SBOMData
    Provenance  ProvenanceData
    Scans       ScanReports
    Gates       GateHistory
    Exceptions  []Exception
    Attestation AttestationData
}
```

### 2.5 Dependency Impact Analyzer

```go
type DependencyImpact struct {
    AnalyzedFiles         int
    HighCouplingPairs     int
    ModerateCouplingPairs int
    Impacts               []ImpactPair
}

type ImpactPair struct {
    FileA          string
    FileB          string
    CouplingScore  float64
    Classification string  // high, moderate, low
    Reasons        []string
    Recommendation string
}

type ImpactAnalyzer interface {
    Analyze(projectPath string, config ImpactConfig) (*DependencyImpact, error)
    AnalyzeForPR(changedFiles []string, config ImpactConfig) (*PRImpactResult, error)
}
```

### 2.6 AI Layer (Opcional)

**Redaction Engine**
```go
type RedactionEngine interface {
    Redact(code string, secrets []SecretFinding) string
}
// api_key = "sk-abc123" → api_key = "[REDACTED:API_KEY]"
```

**LLM Client**
```go
type LLMClient interface {
    Explain(issue Finding, codeContext string) (*Explanation, error)
    SuggestFix(issue Finding, codeContext string) (*FixSuggestion, error)
}
// IMPORTANTE: Solo sugiere, no decide PASS/FAIL
```

---

## 3. Flujos de Datos

### 3.1 Flujo: PR Gate Check

```
1. Developer hace PR
         │
         ▼
2. CI trigger: qodabit ci-check --gate pr
         │
         ▼
3. Scanner descubre archivos
         │
         ▼
4. Analyzers ejecutan (SAST, SCA, Secrets)
         │          (Determinista)
         ▼
5. Dependency Impact analiza acoplamiento
         │
         ▼
6. Gate Evaluator evalúa thresholds
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 PASS       FAIL
    │         │
    ▼         ▼
 Merge     Block + Report
 allowed     │
             ▼
          (Opcional) AI explica/sugiere fix
```

### 3.2 Flujo: Release con Evidence Pack

```
1. Tag release: v1.0.0
         │
         ▼
2. CI trigger: qodabit evidence generate --release v1.0.0
         │
         ▼
3. Verificar PR gates pasaron (histórico)
         │
         ▼
4. Generar SBOM (SPDX + CycloneDX)
         │
         ▼
5. Generar Provenance (SLSA)
         │
         ▼
6. Compilar scan reports + dependency impact
         │
         ▼
7. Evaluar Release Gates
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 PASS       FAIL
    │         │
    ▼         ▼
8. Generar   Block
   Evidence   release
   Pack
    │
    ▼
9. (Opcional) Firmar con Sigstore
    │
    ▼
10. Archivar Evidence Pack
```

### 3.3 Flujo: AI Remediation (Post-FAIL)

```
1. Gate FAIL (determinista)
         │
         ▼
2. Usuario: qodabit explain <issue-id>
         │
         ▼
3. Redaction Engine elimina secrets del contexto
         │
         ▼
4. LLM recibe código REDACTADO
         │
         ▼
5. LLM genera explicación + sugerencia
         │
         ▼
6. Usuario aplica fix
         │
         ▼
7. qodabit audit --gate pr (re-validación DETERMINISTA)
         │
         ▼
8. Gate re-evaluado SIN AI
```

---

## 4. Stack Técnico

### Core Engine
- **Lenguaje**: Go 1.21+ (performance, single binary)
- **Parser AST**: tree-sitter (Python, TypeScript)
- **CVE Database**: SQLite (portable, offline)
- **SBOM**: Libraries SPDX/CycloneDX Go

### CLI
- **Framework**: Cobra
- **Output**: termcolor, structured JSON

### IDE Extension
- **Lenguaje**: TypeScript
- **UI**: React + Webview API
- **Comunicación**: child process al CLI

### MCP Server
- **Protocol**: MCP specification
- **Transport**: stdio

### Signing
- **Primary**: Sigstore/cosign
- **Fallback**: GPG

### AI Integration
- **Providers**: Anthropic, OpenAI, Ollama
- **Redaction**: Custom engine pre-LLM

---

## 5. IDE Extension UX

```
┌─────────────────────────────────────┐
│  QodaBit                        [⚙] │
├─────────────────────────────────────┤
│                                     │
│  Gate Status: PR                    │
│  ┌─────────────────────────────┐   │
│  │  ❌ FAIL                     │   │
│  │  2 gates failing             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Failed Gates:                      │
│  ❌ secrets (2 found, 0 allowed)    │
│  ❌ sast_critical (1 found)         │
│                                     │
│  Passed Gates:                      │
│  ✅ sca_critical                    │
│  ✅ sast_high                       │
│                                     │
│  ─────────────────────────────      │
│                                     │
│  Critical Issues:                   │
│                                     │
│  🔴 Hardcoded API Key               │
│  📁 backend/auth.py:42              │
│  [View] [Fix with AI] [Ignore]      │
│                                     │
│  🔴 SQL Injection                   │
│  📁 backend/db.py:128               │
│  [View] [Fix with AI] [Ignore]      │
│                                     │
│  ─────────────────────────────      │
│                                     │
│  ⚠️ Dependency Impact               │
│  auth.py → session.py (0.82)        │
│  [View Impact Map]                  │
│                                     │
│  [Re-run Gates] [Generate Evidence] │
│                                     │
└─────────────────────────────────────┘
```

---

# FASE 4: PLAN DE IMPLEMENTACIÓN

---

## 1. Filosofía del Roadmap

**Principio:** Evidence Pack + Gates primero, UI bonita después.

Si el buyer es enterprise, necesitan ver:
1. Gates que bloquean (credibilidad)
2. Evidence Pack (audit-ready)
3. SBOM + Provenance (supply chain)
4. UI/UX (nice to have)

---

## 2. Timeline Overview

```
v0.1 (Week 1-8)   : CLI + Gates + Evidence Pack básico
v0.2 (Week 9-18)  : IDE Extension + SBOM/SLSA + Signing
v0.3 (Week 19-28) : MCP + Multi-lang + Enterprise features
```

---

## 3. v0.1 - Foundation + Gates + Evidence (Week 1-8)

### Milestone 1: Project Setup (Week 1)
- [ ] Repo structure (Go monorepo)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Linting, formatting, testing setup
- [ ] `qodabit.yaml` schema definition
- [ ] Basic CLI scaffold (Cobra)

### Milestone 2: Scanner Engine (Week 1-2)
- [ ] File discovery
- [ ] Language detection (Python, TS/JS)
- [ ] Gitignore parsing
- [ ] Path include/exclude
- [ ] File hashing

### Milestone 3: SAST Analyzer (Week 2-4)
- [ ] Python AST parser (tree-sitter)
- [ ] TypeScript AST parser (tree-sitter)
- [ ] 5 security rules per language
- [ ] Severity classification
- [ ] JSON output format

### Milestone 4: Secrets Scanner (Week 3-4)
- [ ] Regex patterns for known secrets
- [ ] Entropy analysis
- [ ] Redaction engine
- [ ] `.qodabit-ignore` support

### Milestone 5: SCA Analyzer - Offline Mode (Week 4-5)
- [ ] Lock file parsers
- [ ] Local CVE database (SQLite)
- [ ] `qodabit db update` command
- [ ] DB freshness tracking
- [ ] License detection

### Milestone 6: Policy Engine + Gates (Week 5-6)
- [ ] `qodabit.yaml` parser
- [ ] Policy validation
- [ ] PR Gates implementation
- [ ] Gate evaluation (deterministic)
- [ ] Exit codes for CI
- [ ] Exceptions with approver/expiry

### Milestone 7: Evidence Pack Generator (Week 6-7)
- [ ] SBOM generator (SPDX format)
- [ ] Scan reports compiler
- [ ] Gate history tracker
- [ ] Evidence Pack structure
- [ ] SHA256 checksums
- [ ] `qodabit evidence generate` command

### Milestone 8: Dependency Impact (Week 7)
- [ ] Import graph analyzer
- [ ] Git co-change detector
- [ ] Coupling score calculator
- [ ] `qodabit impact` commands

### Milestone 9: Reporter + CLI Polish (Week 7-8)
- [ ] JSON report format
- [ ] Markdown report format
- [ ] CLI help and docs
- [ ] `qodabit doctor` command

### v0.1 Deliverables:
- ✅ CLI funcional
- ✅ SAST (Python + TS)
- ✅ Secrets scanning
- ✅ SCA offline mode
- ✅ PR Gates (deterministic)
- ✅ Evidence Pack (básico)
- ✅ SBOM (SPDX)
- ✅ Dependency Impact
- ✅ JSON/Markdown reports

---

## 4. v0.2 - IDE + Supply Chain + Signing (Week 9-18)

### Milestone 10: SCA Online Mode (Week 9-10)
- [ ] NVD API integration
- [ ] GitHub Advisory integration
- [ ] Caching layer
- [ ] Hybrid mode

### Milestone 11: SBOM Enhancement (Week 10-11)
- [ ] CycloneDX format
- [ ] Dependency graph
- [ ] Transitive dependencies

### Milestone 12: Provenance Generator (Week 11-12)
- [ ] SLSA v0.2 format
- [ ] Build metadata capture
- [ ] Source provenance

### Milestone 13: Signing (Week 12-13)
- [ ] Sigstore/cosign integration
- [ ] GPG fallback
- [ ] Evidence Pack signing

### Milestone 14: Release Gates (Week 13-14)
- [ ] PR gates history tracking
- [ ] Release gate evaluation
- [ ] SBOM/Evidence presence check

### Milestone 15: AI Remediation Layer (Week 14-15)
- [ ] LLM client (Anthropic, OpenAI)
- [ ] Redaction engine
- [ ] `qodabit explain/fix` commands

### Milestone 16: IDE Extension (Week 15-18)
- [ ] Extension scaffold
- [ ] CLI integration
- [ ] Webview panel
- [ ] Gate status display
- [ ] "Fix with AI" button

### Milestone 17: Pre-commit Hooks (Week 17-18)
- [ ] Hook installer
- [ ] Fast gate check
- [ ] Bypass logging

### v0.2 Deliverables:
- ✅ SCA online mode
- ✅ SBOM (SPDX + CycloneDX)
- ✅ SLSA Provenance
- ✅ Signing (Sigstore)
- ✅ Release Gates
- ✅ AI Remediation
- ✅ IDE Extension
- ✅ Pre-commit hooks

---

## 5. v0.3 - Enterprise + MCP + Multi-lang (Week 19-28)

### Milestone 18: MCP Server (Week 19-20)
- [ ] MCP protocol implementation
- [ ] Tools: gate_check, audit, fix, evidence, impact
- [ ] Claude Code integration testing

### Milestone 19: Additional Languages (Week 20-23)
- [ ] Go analyzer
- [ ] Java analyzer (básico)
- [ ] Rust analyzer (básico)

### Milestone 20: CI/CD Actions (Week 23-25)
- [ ] GitHub Action
- [ ] GitLab CI template
- [ ] Artifact publishing

### Milestone 21: Enterprise Features (Week 25-28)
- [ ] Policy templates (appsec, cto, grc)
- [ ] Template inheritance
- [ ] Auditor export (PDF)
- [ ] ASVS/SSDF mapping
- [ ] Exception workflow refinement

### v0.3 Deliverables:
- ✅ MCP Server
- ✅ Go/Java/Rust support
- ✅ GitHub Action
- ✅ GitLab CI
- ✅ Enterprise policy templates
- ✅ Auditor PDF export
- ✅ ASVS mapping

---

## 6. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SLSA complexity | Start with Level 2, defer Level 3 |
| Sigstore learning curve | GPG fallback always available |
| CVE DB size | Start with critical/high only |
| AI costs | Clear limits in config, optional feature |
| Multi-lang complexity | One language fully working before next |
| Import graph explosion | Limit depth with `import_depth` config |

---

# FASE 5: TESTING & QA STRATEGY

---

## 1. Testing por Componente

### Gate Evaluator Tests (CRÍTICO)

```go
func TestGateEvaluator_Deterministic(t *testing.T) {
    findings := loadFixture("findings-with-secrets.json")
    config := loadConfig("strict-policy.yaml")

    result1 := evaluator.Evaluate(findings, config)
    result2 := evaluator.Evaluate(findings, config)

    assert.Equal(t, result1, result2)
    assert.Equal(t, GateStatusFail, result1.Status)
}

func TestGateEvaluator_NoAIDependency(t *testing.T) {
    evaluator := NewGateEvaluator(panicOnCallAIClient)
    result := evaluator.Evaluate(findings, config)
    assert.NotNil(t, result)
}
```

### Evidence Pack Tests

```go
func TestEvidencePack_ContainsAllComponents(t *testing.T) {
    pack := generator.Generate(release)

    assert.FileExists(t, pack.Path("manifest.json"))
    assert.FileExists(t, pack.Path("sbom/sbom.spdx.json"))
    assert.FileExists(t, pack.Path("provenance/slsa-provenance.json"))
    assert.FileExists(t, pack.Path("attestation/sha256sums.txt"))
}

func TestEvidencePack_HashesAreValid(t *testing.T) {
    pack := generator.Generate(release)
    for file, expectedHash := range pack.Attestation.SHA256Sums {
        actualHash := sha256File(pack.Path(file))
        assert.Equal(t, expectedHash, actualHash)
    }
}
```

### Secrets Redaction Tests

```go
func TestRedaction_SecretsNeverReachLLM(t *testing.T) {
    code := `api_key = "sk-abc123xyz789"`
    secrets := []SecretFinding{{Line: 1, Type: "api_key"}}

    redacted := redactor.Redact(code, secrets)

    assert.NotContains(t, redacted, "sk-abc123xyz789")
    assert.Contains(t, redacted, "[REDACTED:API_KEY]")
}
```

### Dependency Impact Tests

```go
func TestDependencyImpact_Deterministic(t *testing.T) {
    result1 := analyzer.Analyze(projectPath, config)
    result2 := analyzer.Analyze(projectPath, config)

    assert.Equal(t, result1, result2)
}

func TestDependencyImpact_CouplingScore(t *testing.T) {
    result := analyzer.Analyze(projectPath, config)

    for _, impact := range result.Impacts {
        assert.GreaterOrEqual(t, impact.CouplingScore, 0.0)
        assert.LessOrEqual(t, impact.CouplingScore, 1.0)
    }
}
```

---

## 2. Integration Tests

### Full Gate Flow

```go
func TestIntegration_PRGateFlow(t *testing.T) {
    project := setupTestProject("vulnerable-project")
    result := runCLI("qodabit", "audit", "--gate", "pr", project.Path)

    assert.Equal(t, 1, result.ExitCode)
    assert.Contains(t, result.Output, "FAIL")
}

func TestIntegration_AIRemediationDoesNotAffectGates(t *testing.T) {
    project := setupTestProject("vulnerable-project")

    result1 := runCLI("qodabit", "audit", "--gate", "pr")
    assert.Equal(t, GateStatusFail, result1.GateStatus)

    runCLI("qodabit", "explain", "issue-1")

    result2 := runCLI("qodabit", "audit", "--gate", "pr")
    assert.Equal(t, GateStatusFail, result2.GateStatus)

    applyFix(project, "fix-for-issue-1")
    result3 := runCLI("qodabit", "audit", "--gate", "pr")
    assert.Equal(t, GateStatusPass, result3.GateStatus)
}
```

---

## 3. E2E Scenarios

### Scenario 1: Enterprise Developer Flow
1. Developer clones repo
2. Runs `qodabit init --template appsec-strict`
3. Makes changes with vulnerability
4. Runs `qodabit audit --gate pr` → FAIL
5. Runs `qodabit explain <issue>` → AI explains
6. Fixes issue
7. Runs `qodabit audit --gate pr` → PASS
8. Checks `qodabit impact pr` → Reviews impacted files
9. Creates PR
10. CI runs gates → PASS
11. Merge allowed

### Scenario 2: Release with Evidence Pack
1. All PRs merged with passing gates
2. Tag release: `v1.0.0`
3. CI runs `qodabit evidence generate --release v1.0.0`
4. Evidence Pack created with SBOM, provenance, dependency impact
5. CI runs `qodabit evidence sign`
6. Release gate passes
7. Release published with Evidence Pack artifact

### Scenario 3: Auditor Review
1. Auditor receives Evidence Pack
2. Verifies signature
3. Reviews SBOM
4. Reviews provenance
5. Reviews gate history
6. Reviews exceptions (with approvers)
7. Reviews dependency impact map
8. Accepts evidence

---

## 4. Quality Gates for QodaBit Itself

**PR Requirements:**
- [ ] All tests passing
- [ ] Coverage >80%
- [ ] No new security warnings
- [ ] Gate tests specifically passing
- [ ] Determinism tests passing

**Release Requirements:**
- [ ] All PR requirements
- [ ] E2E scenarios passing
- [ ] SBOM generated for QodaBit itself
- [ ] Evidence Pack for QodaBit release
- [ ] Signed release

---

# FASE 6: DEPLOYMENT & RELEASE PLAN

---

## 1. Release Strategy

### v0.1 Release (Week 8)

**Target:** Early enterprise adopters, security-conscious teams

**Key Message:**
> "Gates that block + Evidence that proves"

**Launch Assets:**
- CLI binary (all platforms)
- Documentation site
- Quick start guide
- Example configs
- Demo video

**Channels:**
- GitHub Release
- Homebrew tap
- NPM wrapper
- Docker image

**Success Metrics (4 weeks post-release):**
- 500 downloads
- 10 enterprise inquiries
- 5 Evidence Packs generated
- <5 critical bugs

### v0.2 Release (Week 18)

**Target:** Teams needing full supply chain security

**Key Message:**
> "SBOM + SLSA + Signed Evidence = Audit Ready"

**Success Metrics:**
- 2000 downloads
- 1000 extension installs
- 50 signed Evidence Packs
- 3 enterprise pilots

### v0.3 Release (Week 28)

**Target:** Enterprise adoption, compliance teams

**Key Message:**
> "Enterprise-grade code compliance, audit-ready from day 1"

**Success Metrics:**
- 5000 downloads
- 10 enterprise customers
- Featured in security publications

---

## 2. Distribution

```bash
# Install script
curl -fsSL https://qodabit.dev/install.sh | sh

# Homebrew
brew tap qodabit/tap
brew install qodabit

# NPM
npm install -g @qodabit/cli

# Docker
docker run -v $(pwd):/code qodabit/cli audit /code

# VS Code
ext install qodabit.qodabit-vscode
```

---

## 3. Support Plan

**Community:**
- GitHub Issues
- GitHub Discussions
- Discord (v0.2+)

**Enterprise:**
- Priority email support
- Slack channel
- Custom policy help
- SLA: 4h response

---

# RESUMEN DE VERSIONES

## v1.0 → v2.0 (Cambios)

1. **Terminología:** "Certificar" → "Audit-ready evidence"
2. **Nuevo FR:** Evidence Pack Generator (SBOM + Provenance + Firma)
3. **Nuevo FR:** Quality Gates (PR + Release) con PASS/FAIL binario
4. **Nuevo FR:** SCA Dual Mode (Offline/Online)
5. **Nuevo NFR:** Supply Chain Security (SLSA, Sigstore)
6. **Modificado FR:** LLM Validator → AI es copiloto, NO juez
7. **Reordenado Roadmap:** Evidence Pack antes que UI
8. **Nuevo concepto:** "Determinista = Juez, AI = Cirujano"
9. **Policy Packs:** Segmentación por buyer (AppSec, CTO, GRC)
10. **Excepciones:** Requieren aprobador + expiración

## v2.0 → v2.1 (Cambios)

1. **Nuevo FR-14:** Dependency Impact Analysis
   - Import graph + Git co-change + Shared state
   - Coupling score determinista
   - Warnings en PR (no bloquea)
   - CLI commands: `qodabit impact`

2. **Policy Packs Expandidos:**
   - Configs YAML completos por pack
   - Template inheritance (`extends`)
   - Comparación detallada de features

3. **Sugerencias Integradas:**
   - `import_depth` para limitar explosión de grafos
   - Herencia de packs para customización enterprise

4. **Métricas Realistas:**
   - Year 1: 2K users, 100 paid, $50K ARR
   - Year 2: 10K users, 500 paid, $200K ARR

5. **Nueva User Story:** US-7 (Dev revisando impacto de cambios)

---

**Documento oficial QodaBit v2.1 Enterprise-Grade** ✅
