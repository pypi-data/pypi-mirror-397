# QodaBit MVP v2 - Cuentas Necesarias

## 4 cuentas para MVP

| Cuenta | Cuándo | Para qué |
|--------|--------|----------|
| GitHub | Ya tienes | Repo, CI/CD |
| Anthropic | Semana 1 | Claude API (chat/explain/fix) |
| OpenAI | Semana 1 | GPT API (chat/explain/fix) |
| PyPI | Semana 5 | `pip install qodabit` |

---

## 1. GitHub (ya tienes)

Necesitas:
- Repo creado
- GitHub Actions habilitado

---

## 2. Anthropic (semana 1)

**Crear antes de empezar desarrollo:**

1. https://console.anthropic.com/
2. Sign up con email
3. Settings → API Keys → Create Key

**Guardar en `.env`:**
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx
```

**Costo:** ~$10-30/mes según uso (Claude 3.5 Sonnet)

---

## 3. OpenAI (semana 1)

**Crear antes de empezar desarrollo:**

1. https://platform.openai.com/
2. Sign up con email
3. API Keys → Create new secret key

**Guardar en `.env`:**
```
OPENAI_API_KEY=sk-xxxxxxxxxx
```

**Costo:** ~$10-30/mes según uso (GPT-4o)

---

## 4. PyPI (semana 5)

**Crear cuando estés listo para release:**

1. https://pypi.org/account/register/
2. Verificar email
3. Habilitar 2FA
4. Account settings → API tokens → Add API token

**Guardar en `.env`:**
```
PYPI_TOKEN=pypi-xxxxxxxxxx
PYPI_USERNAME=__token__
```

---

## Costo MVP

```
GitHub:    $0
Anthropic: ~$10-30/mes
OpenAI:    ~$10-30/mes
PyPI:      $0
---------------
Total:     ~$20-60/mes
```

---

**Eso es todo para MVP v2.**
