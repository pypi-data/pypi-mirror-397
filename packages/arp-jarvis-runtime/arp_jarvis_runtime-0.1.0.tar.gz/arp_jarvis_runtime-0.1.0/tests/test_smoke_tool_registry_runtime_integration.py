import json
import sys
import unittest
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Optional, Protocol

import httpx

from arp_sdk.tool_registry.client import Client as ArpToolRegistryApiClient

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolExecutor
from jarvis_runtime.server import RuntimeCore, RuntimeRunStore, create_app
from jarvis_runtime.tool_registry_client import HttpToolRegistryClient

_TOOL_REGISTRY_REPO = Path(__file__).resolve().parents[2] / "JARVIS_Tool_Registry"
if not _TOOL_REGISTRY_REPO.exists():
    raise unittest.SkipTest("Optional smoke test requires sibling repo: JARVIS_Tool_Registry")
if str(_TOOL_REGISTRY_REPO) not in sys.path:
    sys.path.insert(0, str(_TOOL_REGISTRY_REPO))

class _ToolRegistryApp(Protocol):
    def handle(
        self,
        *,
        method: str,
        path: str,
        body: Optional[dict[str, Any]],
    ) -> tuple[int, Any, Any]: ...


class _ToolRegistryTransport:
    def __init__(self, *, app: _ToolRegistryApp):
        self._app = app
        self.requests: list[tuple[str, str]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        method = request.method
        path = request.url.path
        self.requests.append((method, path))

        request_body: Optional[dict[str, Any]] = None
        if request.content:
            request_body = json.loads(request.content.decode("utf-8"))

        status, payload, _ = self._app.handle(method=method, path=path, body=request_body)
        return httpx.Response(status_code=int(status), json=payload)


class TestRuntimeToolRegistrySmoke(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmp = TemporaryDirectory()
        trace_dir = Path(self._tmp.name)

        catalog_mod = import_module("tool_registry.catalog")
        server_mod = import_module("tool_registry.server")
        ToolCatalog = getattr(catalog_mod, "ToolCatalog")
        load_domain_tools = getattr(catalog_mod, "load_domain_tools")
        ToolRegistryApp = getattr(server_mod, "ToolRegistryApp")

        catalog = ToolCatalog(load_domain_tools(["core"]))
        tool_registry_app = ToolRegistryApp(catalog)

        status, _, _ = tool_registry_app.handle(method="GET", path="/v1/version", body=None)
        if int(status) != 200:
            raise unittest.SkipTest("Tool Registry dependency does not support ARP /v1 yet")

        self._tool_registry_transport = _ToolRegistryTransport(app=tool_registry_app)

        httpx_client = httpx.Client(
            base_url="http://tool-registry.test",
            transport=httpx.MockTransport(self._tool_registry_transport.handler),
        )
        sdk_client = ArpToolRegistryApiClient(base_url="http://tool-registry.test").set_httpx_client(httpx_client)
        tool_registry = HttpToolRegistryClient("http://tool-registry.test", client=sdk_client)

        tool_executor = ToolExecutor(tool_registry=tool_registry, args_generator=HeuristicToolArgsGenerator())
        orchestrator = FlowOrchestrator(
            planner=HeuristicPlanner(),
            tool_registry=tool_registry,
            tool_executor=tool_executor,
            chat=HeuristicChat(),
            trace_dir=trace_dir,
        )
        core = RuntimeCore(orchestrator=orchestrator, store=RuntimeRunStore(root_dir=trace_dir))
        app = create_app(core=core)

        self._client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://runtime.test")

    async def asyncTearDown(self) -> None:
        await self._client.aclose()
        self._tmp.cleanup()

    async def test_submit_run_invokes_tool_registry(self) -> None:
        created = await self._client.post("/v1/runs", json={"input": {"goal": "What time is it in UTC?"}})
        self.assertEqual(created.status_code, 200)
        run_id = created.json()["run_id"]

        result = await self._client.get(f"/v1/runs/{run_id}/result")
        self.assertEqual(result.status_code, 200)
        payload = result.json()
        self.assertTrue(payload.get("ok"))
        self.assertIn("UTC", payload.get("output", {}).get("final_text", ""))

        paths = [p for _, p in self._tool_registry_transport.requests]
        self.assertIn("/v1/tools", paths)
        self.assertIn("/v1/tool-invocations", paths)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
