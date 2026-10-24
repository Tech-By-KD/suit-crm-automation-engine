# SuiteCRM Automation Engine

Playwright + Pytest automation framework targeting the SuiteCRM 8 demo environment. Covers UI end-to-end flows and framework-level unit tests.

---

## Stack

| Thing | Version |
|---|---|
| Python | 3.10+ |
| Playwright | 1.48+ |
| Pytest | 8.0+ |
| Pydantic | 2.6+ |
| Ruff | 0.5+ |

---

## Project layout

```
suit-crm-automation-engine/
├── config/
│   ├── config.yaml               # browser, timeouts, artifact defaults
│   └── environments/
│       └── test.yaml             # base_url per environment
├── src/
│   ├── application/crm/
│   │   ├── pages/                # page objects (login, home)
│   │   └── workflows/            # business-level flows (auth, etc.)
│   └── framework/
│       ├── config/               # settings loader + Pydantic models
│       └── reporting/            # artifact manager (screenshots, traces)
├── tests/
│   ├── conftest.py               # fixtures (browser, context, page, workflows)
│   ├── ui/                       # browser-driven tests
│   └── unit/                     # framework unit tests, no browser needed
├── artifacts/                    # failure screenshots + traces (git-ignored)
├── .env.example
└── pyproject.toml
```

---

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
cd suit-crm-automation-engine
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
```

**2. Install dependencies**

```bash
pip install -e ".[dev]"
playwright install chromium
```

**3. Configure credentials**

Copy `.env.example` to `.env` and fill in your credentials. This file is git-ignored — never commit real secrets.

```bash
copy .env.example .env
```

```ini
CRM_USERNAME=your_username
CRM_PASSWORD=your_password

# Optional overrides
# CRM_BASE_URL=https://suite8demo.suiteondemand.com
# CRM_BROWSER=chromium
# CRM_HEADLESS=false
```

---

## Running tests

```bash
# All tests
pytest

# Smoke tests only
pytest -m smoke

# UI tests only
pytest -m ui

# Unit tests only (no browser, no CRM connection)
pytest -m unit

# Run headed (visible browser window)
pytest --headed

# Target a different environment
pytest --environment staging
```

---

## Markers

| Marker | What it covers |
|---|---|
| `smoke` | Fast, critical-path checks |
| `regression` | Broader functional coverage |
| `ui` | Browser-driven tests |
| `unit` | Framework unit tests |

---

## Artifacts

On test failure, the framework automatically saves to `artifacts/<run-id>/<test-node-id>/`:

- `screenshot-0.png` — page state at the point of failure
- `trace.zip` — Playwright trace, open with `playwright show-trace trace.zip`
- `failure.txt` — node ID and page URLs

Artifacts are git-ignored via `.gitignore`. The `artifacts/.gitkeep` keeps the folder tracked.

---

## Configuration

Settings are layered in this order (later wins):

1. `config/config.yaml` — base defaults
2. `config/environments/<name>.yaml` — environment-specific values
3. Environment variables (`CRM_USERNAME`, `CRM_PASSWORD`, `CRM_BASE_URL`, etc.)
4. CLI flags (`--browser`, `--headed`, `--base-url`)

Credentials are never stored in YAML. They come from environment variables or `.env`.

---

## Linting

```bash
ruff check .
ruff format .
```
