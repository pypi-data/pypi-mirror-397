from __future__ import annotations

import argparse
import errno
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any

from .llm import OpenAIResponsesClient
from .roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, LlmChat, LlmPlanner, LlmToolArgsGenerator, ToolExecutor
from .tool_registry_client import HttpToolRegistryClient
from .orchestrator import FlowOrchestrator


def _bind_server_socket(host: str, port: int) -> tuple[int, int]:
    sock = socket.create_server((host, port))
    actual_port = int(sock.getsockname()[1])
    fd = sock.detach()
    return actual_port, fd


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--trace-dir", default=os.getenv("JARVIS_TRACE_DIR", "./runs"))
    common.add_argument("--redact-prompts", action="store_true", default=bool(os.getenv("JARVIS_REDACT_PROMPTS", "")))
    common.add_argument(
        "--tool-registry-url",
        default=os.getenv("ARP_TOOL_REGISTRY_URL") or os.getenv("JARVIS_TOOL_REGISTRY_URL") or "http://127.0.0.1:8000",
    )
    common.add_argument("--mode", choices=["stub", "openai"], default=os.getenv("JARVIS_RUNTIME_MODE", "stub"))

    serve_cmd = sub.add_parser("serve", parents=[common], help="Run the ARP Runtime HTTP server")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=None, help="Default: 8081 (use 0 for auto)")
    serve_cmd.add_argument(
        "--auto-port",
        action="store_true",
        help="If the selected port is unavailable, bind to a free port instead.",
    )
    serve_cmd.add_argument("--log-level", default="info")

    run_cmd = sub.add_parser("run", parents=[common], help="Run a single request")
    run_cmd.add_argument("--request", required=True)

    demo_cmd = sub.add_parser("demo", parents=[common], help="Run the 3-step MVP demo")

    replay_cmd = sub.add_parser("replay", parents=[common], help="Replay chat from a recorded trace")
    replay_cmd.add_argument("--trace", required=True, help="Path to a trace.jsonl file")
    replay_cmd.add_argument(
        "--original",
        action="store_true",
        help="Print the recorded final_text instead of rerunning Chat",
    )

    args = parser.parse_args(argv)

    if args.cmd == "serve":
        from .server import create_app

        try:
            import uvicorn  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise SystemExit(f"Missing server dependencies. Install with: python -m pip install fastapi uvicorn\n{exc}") from exc

        app = create_app(
            trace_dir=args.trace_dir,
            tool_registry_url=args.tool_registry_url,
            mode=args.mode,
            redact_prompts=bool(args.redact_prompts),
        )

        requested_port = int(args.port) if args.port is not None else 8081
        try:
            actual_port, fd = _bind_server_socket(args.host, requested_port)
        except OSError as exc:
            should_fallback = bool(args.auto_port) or args.port is None
            if exc.errno != errno.EADDRINUSE or not should_fallback:
                raise
            actual_port, fd = _bind_server_socket(args.host, 0)
            print(f"Port {requested_port} is already in use; serving on port {actual_port} instead.", file=sys.stderr)

        uvicorn.run(app, host=args.host, port=actual_port, fd=fd, log_level=args.log_level)
        return 0

    if args.cmd == "replay":
        return _cmd_replay(trace_path=Path(args.trace), mode=args.mode, redact_prompts=bool(args.redact_prompts), original_only=bool(args.original))

    tool_registry_client = HttpToolRegistryClient(args.tool_registry_url)

    if args.mode == "openai":
        client = _make_openai_client()
        planner = LlmPlanner(client, model=os.getenv("JARVIS_MODEL_PLANNER"), redact_prompts=args.redact_prompts)
        args_gen = LlmToolArgsGenerator(client, model=os.getenv("JARVIS_MODEL_TOOL_ARGS"), redact_prompts=args.redact_prompts)
        chat = LlmChat(client, model=os.getenv("JARVIS_MODEL_CHAT"), redact_prompts=args.redact_prompts)
    else:
        planner = HeuristicPlanner()
        args_gen = HeuristicToolArgsGenerator()
        chat = HeuristicChat()

    tool_executor = ToolExecutor(tool_registry=tool_registry_client, args_generator=args_gen)

    orchestrator = FlowOrchestrator(
        planner=planner,
        tool_registry=tool_registry_client,
        tool_executor=tool_executor,
        chat=chat,
        trace_dir=Path(args.trace_dir),
        redact_prompts=args.redact_prompts,
    )

    if args.cmd == "run":
        result = orchestrator.run(user_request=args.request)
        print(result.final_text)
        print(f"trace: {result.trace.trace_jsonl}")
        return 0 if result.status == "completed" else 1

    if args.cmd == "demo":
        requests = [
            "What time is it in UTC?",
            "What is (19*23)?",
            "Rephrase this sentence: The quick brown fox jumps over the lazy dog.",
        ]
        for req in requests:
            print(f"\n--- request: {req}")
            result = orchestrator.run(user_request=req)
            print(result.final_text)
            print(f"trace: {result.trace.trace_jsonl}")
        return 0

    raise RuntimeError("Unknown command")


def _make_openai_client() -> OpenAIResponsesClient:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("JARVIS_OPENAI_API_KEY") or ""
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY (or JARVIS_OPENAI_API_KEY)")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("JARVIS_OPENAI_BASE_URL") or "https://api.openai.com/v1"
    model = os.getenv("JARVIS_MODEL_DEFAULT") or "gpt-5-nano"
    return OpenAIResponsesClient(api_key=api_key, base_url=base_url, default_model=model)


def _cmd_replay(*, trace_path: Path, mode: str, redact_prompts: bool, original_only: bool) -> int:
    if not trace_path.exists():
        raise SystemExit(f"Trace not found: {trace_path}")

    events = _read_trace_events(trace_path)
    original_status, original_final_text = _extract_original_result(events)

    if original_only:
        print(original_final_text)
        return 0 if original_status == "completed" else 1

    user_request, context = _extract_replay_context(events)

    if mode == "openai":
        client = _make_openai_client()
        chat = LlmChat(client, model=os.getenv("JARVIS_MODEL_CHAT"), redact_prompts=redact_prompts)
    else:
        chat = HeuristicChat()

    result = chat.run(user_request=user_request, context=context, trace=None)
    print(result.text)
    return 0 if original_status == "completed" else 1


def _read_trace_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def _extract_original_result(events: list[dict[str, Any]]) -> tuple[str, str]:
    for event in reversed(events):
        if event.get("type") == "flow_completed":
            status = event.get("status")
            final_text = event.get("final_text")
            return (status if isinstance(status, str) else "completed"), (final_text if isinstance(final_text, str) else "")
    return "completed", ""


def _extract_replay_context(events: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    # Prefer the already-constructed chat user_payload from the trace when available.
    for event in reversed(events):
        if event.get("type") != "llm_call" or event.get("role") != "chat":
            continue
        user_prompt = event.get("user_prompt")
        if not isinstance(user_prompt, str):
            continue
        try:
            payload = json.loads(user_prompt)
        except Exception:
            continue
        user_request = payload.get("user_request")
        context = payload.get("context")
        if isinstance(user_request, str) and isinstance(context, dict):
            return user_request, context

    user_request = ""
    trace_id = None
    error = None
    tool_results: list[dict[str, Any]] = []

    for event in events:
        if event.get("type") == "flow_started":
            inp = event.get("input")
            if isinstance(inp, dict) and isinstance(inp.get("user_request"), str):
                user_request = inp["user_request"]
            if isinstance(event.get("trace_id"), str):
                trace_id = event["trace_id"]
        if event.get("type") == "flow_failed":
            err = event.get("error")
            if isinstance(err, dict):
                error = err

        if event.get("type") != "tool_result":
            continue
        tool_name = event.get("tool_name")
        tool_result = event.get("result")
        trace = event.get("trace")
        step_id = trace.get("step_id") if isinstance(trace, dict) else None
        if not isinstance(tool_name, str) or not isinstance(tool_result, dict):
            continue
        if tool_result.get("ok") is True:
            tool_results.append({"tool_name": tool_name, "result": tool_result.get("result"), "step_id": step_id})

    context: dict[str, Any] = {"user_request": user_request, "step_results": [], "tool_results": tool_results, "meta": {}}
    if trace_id is not None:
        context["meta"]["trace_id"] = trace_id
    if error is not None:
        context["error"] = error
    return user_request, context
