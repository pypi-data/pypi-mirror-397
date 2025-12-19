import unittest
import json
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import httpx

from jarvis_runtime.orchestrator import FlowOrchestrator
from jarvis_runtime.roles import HeuristicChat, HeuristicPlanner, HeuristicToolArgsGenerator, ToolExecutor
from jarvis_runtime.server import RuntimeCore, RuntimeRunStore, create_app

from .fake_tool_registry import FakeToolRegistryClient

try:  # optional, used for schema validation tests
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover
    jsonschema = None


def _arp_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _standard_schemas_root() -> Path:
    return _arp_root() / "ARP_Standard" / "spec" / "v1" / "schemas"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_against_schema(*, schema_rel: str, instance: Any) -> list[str]:
    if jsonschema is None:  # pragma: no cover
        raise RuntimeError("jsonschema is not installed")

    schema_path = _standard_schemas_root() / schema_rel
    schema = _load_json(schema_path)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        resolver = jsonschema.RefResolver(base_uri=schema_path.as_uri(), referrer=schema)
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)

    errors = sorted(validator.iter_errors(instance), key=lambda exc: list(exc.path))
    rendered: list[str] = []
    for err in errors:
        location = "/".join(str(p) for p in err.path) or "<root>"
        rendered.append(f"{location}: {err.message}")
    return rendered


class TestRuntimeServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._tmp = TemporaryDirectory()
        trace_dir = Path(self._tmp.name)

        tool_registry = FakeToolRegistryClient()
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

    async def test_health(self) -> None:
        resp = await self._client.get("/v1/health")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload.get("status"), "ok")
        self.assertIsInstance(payload.get("time"), str)
        if jsonschema is not None:
            self.assertEqual(_validate_against_schema(schema_rel="common/health.schema.json", instance=payload), [])

    async def test_run_lifecycle(self) -> None:
        created = await self._client.post("/v1/runs", json={"input": {"goal": "What time is it in UTC?"}})
        self.assertEqual(created.status_code, 200)
        status = created.json()
        self.assertIsInstance(status.get("run_id"), str)
        run_id = status["run_id"]
        if jsonschema is not None:
            self.assertEqual(_validate_against_schema(schema_rel="runtime/runs/run_status.schema.json", instance=status), [])

        fetched = await self._client.get(f"/v1/runs/{run_id}")
        self.assertEqual(fetched.status_code, 200)
        fetched_payload = fetched.json()
        self.assertEqual(fetched_payload.get("run_id"), run_id)
        if jsonschema is not None:
            self.assertEqual(
                _validate_against_schema(schema_rel="runtime/runs/run_status.schema.json", instance=fetched_payload),
                [],
            )

        result = await self._client.get(f"/v1/runs/{run_id}/result")
        self.assertEqual(result.status_code, 200)
        result_payload = result.json()
        self.assertEqual(result_payload.get("run_id"), run_id)
        self.assertTrue(result_payload.get("ok"))
        self.assertIn("output", result_payload)
        if jsonschema is not None:
            self.assertEqual(_validate_against_schema(schema_rel="runtime/runs/run_result.schema.json", instance=result_payload), [])

    async def test_validation_errors_use_error_envelope(self) -> None:
        resp = await self._client.post("/v1/runs", json=[])
        self.assertEqual(resp.status_code, 400)
        payload = resp.json()
        self.assertIsInstance(payload.get("error"), dict)
        self.assertIsInstance(payload["error"].get("code"), str)
        if jsonschema is not None:
            self.assertEqual(_validate_against_schema(schema_rel="common/error.schema.json", instance=payload), [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
