import json
import unittest
from tempfile import TemporaryDirectory
from typing import Any, Optional

import httpx

from arp_sdk.tool_registry.client import Client as ArpToolRegistryApiClient

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolArgsGenerator, ToolExecutor
from jarvis_runtime.tool_registry_client import HttpToolRegistryClient
from jarvis_runtime.trace import TraceWriter

from .fake_tool_registry import FakeToolRegistryClient


class _RecordingTransport:
    def __init__(self, *, registry: FakeToolRegistryClient):
        self._registry = registry
        self.requests: list[tuple[str, str]] = []
        self.calls: list[dict[str, Any]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        method = request.method
        path = request.url.path
        self.requests.append((method, path))

        request_body: Optional[dict[str, Any]] = None
        if request.content:
            request_body = json.loads(request.content.decode("utf-8"))

        status = 404
        payload: Any = {"error": {"code": "http.not_found", "message": "Not found"}}

        if method == "GET" and path == "/v1/tools":
            status = 200
            payload = [t.to_dict() for t in self._registry.list_tools()]

        if method == "POST" and path == "/v1/tool-invocations":
            if not isinstance(request_body, dict):
                status = 400
                payload = {"error": {"code": "request.invalid", "message": "Expected JSON object"}}
            else:
                invocation_id = request_body.get("invocation_id")
                tool_name = request_body.get("tool_name")
                args = request_body.get("args")
                if not isinstance(invocation_id, str) or not isinstance(tool_name, str) or not isinstance(args, dict):
                    status = 400
                    payload = {"error": {"code": "request.invalid", "message": "Missing invocation_id/tool_name/args"}}
                else:
                    handler = self._registry.handlers.get(tool_name)
                    if handler is None:
                        status = 200
                        payload = {
                            "invocation_id": invocation_id,
                            "ok": False,
                            "error": {"code": "tool.not_found", "message": "Unknown tool"},
                        }
                    else:
                        result = handler(args)
                        status = 200
                        payload = {"invocation_id": invocation_id, "ok": True, "result": result}

        self.calls.append(
            {
                "method": method,
                "path": path,
                "request_body": request_body,
                "status": status,
                "response_payload": payload,
            }
        )
        return httpx.Response(status_code=status, json=payload)


class AlwaysInvalidArgsGenerator(ToolArgsGenerator):
    def generate(
        self,
        *,
        tool_name: str,
        tool_schema: dict[str, Any],
        context: dict[str, Any],
        intent: str,
        targets: list[str],
        tool_description: Optional[str] = None,
        validation_error: Optional[dict[str, Any]] = None,
        trace: Optional[TraceWriter] = None,
    ) -> dict[str, Any]:
        return {}


def _read_events(path) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class TestHttpIntegration(unittest.TestCase):
    def _make_http_tool_registry(self, transport: _RecordingTransport) -> HttpToolRegistryClient:
        httpx_client = httpx.Client(base_url="http://tool-registry.test", transport=httpx.MockTransport(transport.handler))
        sdk_client = ArpToolRegistryApiClient(base_url="http://tool-registry.test").set_httpx_client(httpx_client)
        return HttpToolRegistryClient("http://tool-registry.test", client=sdk_client)

    def test_time_now_end_to_end_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            registry = FakeToolRegistryClient()
            transport = _RecordingTransport(registry=registry)
            tool_registry = self._make_http_tool_registry(transport)
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )

            result = orchestrator.run(user_request="What time is it in UTC?")
            self.assertEqual(result.status, "completed")
            self.assertIn("UTC", result.final_text)

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertIn("/v1/tool-invocations", paths)

            invoke_call = next(c for c in transport.calls if c["method"] == "POST" and c["path"] == "/v1/tool-invocations")
            self.assertIsInstance(invoke_call.get("request_body"), dict)
            body = invoke_call["request_body"]
            self.assertIsInstance(body.get("invocation_id"), str)
            self.assertEqual(body.get("tool_name"), "time_now")
            self.assertIsInstance(body.get("args"), dict)

    def test_no_tool_path_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            registry = FakeToolRegistryClient()
            transport = _RecordingTransport(registry=registry)
            tool_registry = self._make_http_tool_registry(transport)
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )

            result = orchestrator.run(user_request="Rephrase this sentence: hello world")
            self.assertEqual(result.status, "completed")

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertFalse(any(p == "/v1/tool-invocations" for p in paths))

    def test_invalid_args_do_not_invoke_over_http(self) -> None:
        with TemporaryDirectory() as tmp:
            registry = FakeToolRegistryClient()
            transport = _RecordingTransport(registry=registry)
            tool_registry = self._make_http_tool_registry(transport)
            tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=AlwaysInvalidArgsGenerator())
            orchestrator = FlowOrchestrator(
                planner=HeuristicPlanner(),
                tool_registry=tool_registry,
                tool_executor=tool_executor,
                chat=HeuristicChat(),
                trace_dir=tmp,
            )

            result = orchestrator.run(user_request="What is (19*23)?")
            self.assertEqual(result.status, "failed")
            self.assertIn("tool.invalid_args", result.final_text)

            paths = [p for _, p in transport.requests]
            self.assertIn("/v1/tools", paths)
            self.assertFalse(any(p == "/v1/tool-invocations" for p in paths))

            events = _read_events(result.trace.trace_jsonl)
            invalids = [e for e in events if e.get("type") == "tool_args_invalid" and e.get("tool_name") == "calc"]
            self.assertEqual(len(invalids), 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
