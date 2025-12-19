from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from arp_sdk.runtime.models import RunRequest, RunResult, RunStatus
from arp_sdk.runtime.types import Unset as RuntimeUnset

from .orchestrator import FlowOrchestrator
from .roles import (
    HeuristicChat,
    HeuristicPlanner,
    HeuristicToolArgsGenerator,
    LlmChat,
    LlmPlanner,
    LlmToolArgsGenerator,
    ToolExecutor,
)
from .tool_registry_client import HttpToolRegistryClient, ToolRegistryClient
from .util import utc_now_iso


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _service_version() -> str:
    try:
        return package_version("arp-jarvis-runtime")
    except PackageNotFoundError:
        return "0.0.0"


def _error_envelope(*, code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class RuntimeRunStore:
    root_dir: Path

    def run_dir(self, run_id: str) -> Path:
        return self.root_dir / run_id

    def write_request(self, run_id: str, request: RunRequest) -> None:
        _atomic_write_json(self.run_dir(run_id) / "request.json", request.to_dict())

    def write_status(self, run_id: str, status: RunStatus) -> None:
        _atomic_write_json(self.run_dir(run_id) / "status.json", status.to_dict())

    def write_result(self, run_id: str, result: RunResult) -> None:
        _atomic_write_json(self.run_dir(run_id) / "result.json", result.to_dict())

    def read_status(self, run_id: str) -> RunStatus | None:
        path = self.run_dir(run_id) / "status.json"
        if not path.exists():
            return None
        return RunStatus.from_dict(_read_json(path))

    def read_result(self, run_id: str) -> RunResult | None:
        path = self.run_dir(run_id) / "result.json"
        if not path.exists():
            return None
        return RunResult.from_dict(_read_json(path))


@dataclass(slots=True)
class RuntimeCore:
    orchestrator: FlowOrchestrator
    store: RuntimeRunStore

    def submit_run(self, request: RunRequest) -> RunStatus:
        run_id = _ensure_run_id(request)
        self.store.write_request(run_id, request)

        started_at = _utc_now_z()
        try:
            goal = str(request.input_.goal)
            exec_result = self.orchestrator.run_with_ids(user_request=goal, flow_id=run_id)
        except Exception as exc:  # noqa: BLE001 - surface into RunResult
            ended_at = _utc_now_z()
            status = RunStatus.from_dict({"run_id": run_id, "state": "failed", "started_at": started_at, "ended_at": ended_at})
            self.store.write_status(run_id, status)
            result = RunResult.from_dict(
                {
                    "run_id": run_id,
                    "ok": False,
                    "error": {"code": "runtime.exception", "message": str(exc)},
                }
            )
            self.store.write_result(run_id, result)
            return status

        ended_at = _utc_now_z()
        succeeded = exec_result.status == "completed"
        state = "succeeded" if succeeded else "failed"

        status = RunStatus.from_dict({"run_id": run_id, "state": state, "started_at": started_at, "ended_at": ended_at})
        self.store.write_status(run_id, status)

        output: dict[str, Any] = {"final_text": exec_result.final_text}
        trace_uri = exec_result.trace.trace_jsonl.absolute().as_uri()
        output["trace_uri"] = trace_uri

        result_payload: dict[str, Any] = {"run_id": run_id, "ok": succeeded, "output": output}
        if not succeeded:
            result_payload["error"] = {"code": "flow.failed", "message": exec_result.final_text}

        result = RunResult.from_dict(result_payload)
        self.store.write_result(run_id, result)
        return status

    def get_run_status(self, run_id: str) -> RunStatus:
        status = self.store.read_status(run_id)
        if status is None:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")
        return status

    def get_run_result(self, run_id: str) -> RunResult:
        result = self.store.read_result(run_id)
        if result is None:
            raise FileNotFoundError(f"Unknown run_id: {run_id}")
        return result


def _ensure_run_id(request: RunRequest) -> str:
    if isinstance(request.run_id, RuntimeUnset):
        request.run_id = f"run_{uuid.uuid4().hex[:12]}"
    return str(request.run_id)


def _resolve_tool_registry_url(explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    import os

    return (os.getenv("ARP_TOOL_REGISTRY_URL") or os.getenv("JARVIS_TOOL_REGISTRY_URL") or "http://127.0.0.1:8000").rstrip("/")


def _make_orchestrator(
    *,
    mode: str,
    tool_registry: ToolRegistryClient,
    trace_dir: Path,
    redact_prompts: bool,
    max_steps: int,
) -> FlowOrchestrator:
    if mode == "openai":
        from .llm import OpenAIResponsesClient

        import os

        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("JARVIS_OPENAI_API_KEY") or ""
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY (or JARVIS_OPENAI_API_KEY)")
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("JARVIS_OPENAI_BASE_URL") or "https://api.openai.com/v1"
        model = os.getenv("JARVIS_MODEL_DEFAULT") or "gpt-5-nano"
        client = OpenAIResponsesClient(api_key=api_key, base_url=base_url, default_model=model)

        planner = LlmPlanner(client, model=os.getenv("JARVIS_MODEL_PLANNER"), redact_prompts=redact_prompts)
        args_gen = LlmToolArgsGenerator(client, model=os.getenv("JARVIS_MODEL_TOOL_ARGS"), redact_prompts=redact_prompts)
        chat = LlmChat(client, model=os.getenv("JARVIS_MODEL_CHAT"), redact_prompts=redact_prompts)
    else:
        planner = HeuristicPlanner()
        args_gen = HeuristicToolArgsGenerator()
        chat = HeuristicChat()

    tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=args_gen)

    return FlowOrchestrator(
        planner=planner,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        chat=chat,
        trace_dir=trace_dir,
        redact_prompts=redact_prompts,
        max_steps=max_steps,
    )


def create_app(
    *,
    core: RuntimeCore | None = None,
    trace_dir: str | Path = "./runs",
    tool_registry_url: str | None = None,
    mode: str = "stub",
    redact_prompts: bool = False,
    max_steps: int = 20,
) -> FastAPI:
    trace_dir_path = Path(trace_dir)

    if core is None:
        tool_registry_client = HttpToolRegistryClient(_resolve_tool_registry_url(tool_registry_url))
        orchestrator = _make_orchestrator(
            mode=mode,
            tool_registry=tool_registry_client,
            trace_dir=trace_dir_path,
            redact_prompts=redact_prompts,
            max_steps=max_steps,
        )
        core = RuntimeCore(orchestrator=orchestrator, store=RuntimeRunStore(root_dir=trace_dir_path))

    app = FastAPI(title="ARP Jarvis Runtime", version=_service_version())

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_error_envelope(code="bad_request", message="Invalid request", details={"errors": exc.errors()}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(
            status_code=int(getattr(exc, "status_code", 500)),
            content=_error_envelope(code="http_error", message=message),
        )

    @app.get("/v1/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "time": utc_now_iso(), "checks": []}

    @app.get("/v1/version")
    def version() -> dict[str, Any]:
        return {
            "service_name": "arp-jarvis-runtime",
            "service_version": _service_version(),
            "supported_api_versions": ["v1"],
        }

    @app.post("/v1/runs")
    def create_run(body: dict[str, Any] = Body(...)) -> JSONResponse:
        try:
            request = RunRequest.from_dict(body)
        except Exception as exc:  # noqa: BLE001 - parse errors to API envelope
            return JSONResponse(
                status_code=400,
                content=_error_envelope(code="bad_request", message="Invalid RunRequest", details={"error": str(exc)}),
            )

        try:
            status = core.submit_run(request)
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))

        return JSONResponse(status_code=200, content=status.to_dict())

    @app.get("/v1/runs/{run_id}")
    def get_run_status(run_id: str) -> JSONResponse:
        try:
            status = core.get_run_status(run_id)
        except FileNotFoundError as exc:
            return JSONResponse(status_code=404, content=_error_envelope(code="not_found", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))
        return JSONResponse(status_code=200, content=status.to_dict())

    @app.get("/v1/runs/{run_id}/result")
    def get_run_result(run_id: str) -> JSONResponse:
        try:
            result = core.get_run_result(run_id)
        except FileNotFoundError as exc:
            return JSONResponse(status_code=404, content=_error_envelope(code="not_found", message=str(exc)))
        except Exception as exc:  # noqa: BLE001 - surface core errors
            return JSONResponse(status_code=500, content=_error_envelope(code="internal_error", message=str(exc)))
        return JSONResponse(status_code=200, content=result.to_dict())

    @app.post("/v1/runs/{run_id}:cancel")
    def cancel_run(run_id: str) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=_error_envelope(code="not_cancelable", message="This runtime executes runs synchronously; cancel is not supported."),
        )

    @app.get("/v1/runs/{run_id}/events")
    def run_events(run_id: str) -> JSONResponse:
        return JSONResponse(
            status_code=501,
            content=_error_envelope(code="not_implemented", message="Run events stream is not implemented."),
        )

    return app
