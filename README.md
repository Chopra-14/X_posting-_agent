# Guardrailed X (Twitter) Posting Agent Harness

This repository implements a deterministic agent harness that reads scheduled tweet data from a CSV, formats the content using an LLM (with strict JSON output), validates the result through a series of guardrails, and posts the tweet via Playwright against a **mock social media server**.

## Repository Layout
```
project/
│   README.md                # This file
│   docker-compose.yml       # Orchestrates mock server & agent
│   Dockerfile               # Build image for the agent service
│   .env.example             # Example environment variables
│
├─ src/
│   │   main.py            # Orchestrator / entry point
│   │   state_manager.py   # CSV parsing & state handling
│   │   llm_formatter.py   # LLM wrapper returning Pydantic model
│   │   guardrails.py      # Deterministic validation checks
│   │   browser_actor.py   # Playwright automation
│   │   mock_server.py     # FastAPI mock social server
│   │
│   └─ templates/          # Jinja2 HTML templates (inline strings used)
│
├─ data/
│   │   schedule.csv       # Sample schedule file
│   │   posted_ids.json    # Persistent list of already‑posted row IDs
│   │   browser_state.json # Playwright storage state (generated)
│   │   traces.jsonl       # Execution trace log (JSON Lines)
│
├─ tests/                     # Optional unit / integration tests
│
└─ evaluate.py                # Computes aggregate metrics from traces
```

## Quick Start (Docker)
```bash
# 1. Copy the example env file and fill in your secrets (or leave placeholders for the mock setup)
cp .env.example .env

# 2. Build and start the services
docker-compose up --build -d

# 3. Verify the mock server is reachable
curl http://localhost:8080/login
```

The agent runs automatically on container start, processes any tweet due today, and writes a trace entry to `data/traces.jsonl`.

## Key Concepts
| Component | Responsibility |
|-----------|-----------------|
| **ScheduleManager** (src/state_manager.py) | Reads `schedule.csv`, filters rows for the current date, and guarantees a row is processed only once (via `posted_ids.json`). |
| **LLMService** (src/llm_formatter.py) | Calls the configured LLM endpoint (`LLM_BASE_URL`) with temperature 0 and requests JSON‑mode output that matches the `FormattedPost` Pydantic schema. |
| **GuardrailChain** (src/guardrails.py) | Enforces length ≤ 280, bans specific words, and checks groundedness (no new URLs or @‑mentions). If any check fails, the raw CSV text is used instead. |
| **SocialMediaActor** (src/browser_actor.py) | Uses Playwright to load the mock social site, preserves session state in `browser_state.json`, and performs the actual post. |
| **Trace Logging** | Every run appends a JSON line to `data/traces.jsonl` containing timestamps, raw/LLM text, guardrail outcomes, and action status. |
| **Metrics** (evaluate.py) | Parses the trace file and produces `metrics.json` with Task Completion Rate, Groundedness Score, and Guardrail Trigger Rate. |

## Environment Variables (`.env.example`)
| Variable | Description |
|----------|-------------|
| `LLM_BASE_URL` | Base URL of the LLM service (e.g., `https://api.openai.com/v1`). |
| `OPENAI_API_KEY` | API key for OpenAI (or equivalent for other providers). |
| `MOCK_SOCIAL_URL` | Root URL of the mock social server (default `http://mock_social:8080`). |
| `MOCK_USERNAME` | Username used for the mock login page. |
| `MOCK_PASSWORD` | Password used for the mock login page. |

All secret values are **never** checked into version control.

---

For full details on each module, see the corresponding source files in `src/`.
