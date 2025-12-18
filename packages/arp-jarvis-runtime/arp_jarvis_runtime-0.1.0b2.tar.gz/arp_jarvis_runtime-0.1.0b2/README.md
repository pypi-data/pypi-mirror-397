# JARVIS Runtime

This repo contains the **Jarvis Agent Runtime**: a Python runtime for executing Agent Runtime Protocol-style agent flows using the 3-role loop:

Planner → Tool Executor (arg-gen + invoke) → Chat

It is designed to run against an **ARP Tool Registry** service and share contracts via the **ARP Standard** Python SDK (`arp-standard-py` / `arp_sdk`).

## Quickstart

See:

- `docs/quickstart.md`
- `docs/trace.md`

## Install

From PyPI (once published):

```bash
pipx install arp-jarvis-runtime
```

Pre-release (e.g. `0.1.0a1`):

```bash
pipx install --pip-args="--pre" arp-jarvis-runtime
```

Or in a virtualenv:

```bash
pip install arp-jarvis-runtime
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

## OpenAI mode (optional)

This runtime uses the OpenAI Python SDK for Responses parsing + structured outputs. To enable it:

```bash
pip install -e ".[openai]"
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
python -m unittest discover -v
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

- `docs/intro.md`
- `docs/design/overview.md`

## Repo boundaries

- This repo: flow execution, LLM role orchestration, runtime packaging.
- `Tool_Registry` (separate repo): tool discovery + schemas + invocation routing (+ MCP aggregation).
- `ARP_Standard` (separate repo): spec + schemas + SDKs (published as `arp-standard-py`).

## MVP capabilities + known gaps

Capabilities:

- Stub-mode 3-role loop (Planner → Tool → Chat) with trace JSONL.
- Tool Registry integration via HTTP (ARP Standard v1alpha1).
- Trace replay: rerun Chat from recorded tool results.

Known gaps:

- No production hardening (auth, multi-tenancy, concurrency controls, streaming, persistence).
- Prompt packs and planning heuristics are MVP-grade; no memory/scheduler/control plane yet.
