# JARVIS Runtime

This repo contains the **Jarvis Agent Runtime**: a Python runtime for executing Agent Runtime Protocol-style agent flows using the 3-role loop:

Planner → Tool Executor (arg-gen + invoke) → Chat

It is designed to run against an **ARP Tool Registry** service and share contracts via the **ARP Standard** Python SDK (`arp-standard-py` / `arp_sdk`).

## Quickstart

See:

- [`docs/quickstart.md`](docs/quickstart.md)
- [`docs/trace.md`](docs/trace.md)

## Install

```bash
# CLI installs (recommended)
pipx install arp-jarvis-runtime

# or, in a virtualenv
python3 -m pip install arp-jarvis-runtime
```

## Run against a real Tool Registry service

Terminal A (Tool Registry):

```bash
arp-jarvis-tool-registry
```

Terminal B (Runtime):

```bash
arp-jarvis-runtime demo --tool-registry-url http://127.0.0.1:8000
```

Or configure via env var (preferred when launched by a daemon):

```bash
export ARP_TOOL_REGISTRY_URL=http://127.0.0.1:8000
arp-jarvis-runtime demo
```

Back-compat env var: `JARVIS_TOOL_REGISTRY_URL`.

## Run as a Runtime HTTP server (v1)

```bash
arp-jarvis-runtime serve --host 127.0.0.1 --port 8081 --tool-registry-url http://127.0.0.1:8000
```

If `--port` is omitted and `8081` is already in use, the runtime binds to a free port and prints it (or use `--port 0` to always pick a free port). Use `--auto-port` to fall back when an explicit `--port` is in use.

Runtime API endpoints (selected):
- `GET /v1/health`
- `GET /v1/version`
- `POST /v1/runs`
- `GET /v1/runs/{run_id}`
- `GET /v1/runs/{run_id}/result`

## OpenAI mode (optional)

This runtime uses the OpenAI Python SDK for Responses parsing + structured outputs. To enable it:

```bash
python3 -m pip install "arp-jarvis-runtime[openai]"
export OPENAI_API_KEY=...
arp-jarvis-runtime demo --mode openai --tool-registry-url http://127.0.0.1:8000
```

Optional model overrides:

- `JARVIS_MODEL_PLANNER`
- `JARVIS_MODEL_TOOL_ARGS`
- `JARVIS_MODEL_CHAT`
- `JARVIS_MODEL_DEFAULT`

## Validation

Unit tests:

```bash
python3 -m unittest discover -v
```

Or (if you have `pytest` installed):

```bash
pytest -q
```

Typecheck (pyright):

```bash
pyright -p pyrightconfig.json
```

## Design docs

- [`docs/intro.md`](docs/intro.md)
- [`docs/design/overview.md`](docs/design/overview.md)

## Repo boundaries

- This repo: flow execution, LLM role orchestration, runtime packaging.
- `Tool_Registry` (separate repo): tool discovery + schemas + invocation routing (+ MCP aggregation).
- `ARP_Standard` (separate repo): spec + schemas + SDKs (published as `arp-standard-py`).

## MVP capabilities + known gaps

Capabilities:

- Stub-mode 3-role loop (Planner → Tool → Chat) with trace JSONL.
- Tool Registry integration via HTTP (ARP Standard v1).
- Trace replay: rerun Chat from recorded tool results.

Known gaps:

- No production hardening (auth, multi-tenancy, concurrency controls, streaming, persistence).
- Prompt packs and planning heuristics are MVP-grade; no memory/scheduler/control plane yet.
