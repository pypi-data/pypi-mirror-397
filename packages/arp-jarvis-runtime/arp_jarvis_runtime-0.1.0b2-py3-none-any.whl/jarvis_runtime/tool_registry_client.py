from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol
from uuid import uuid4

import httpx

from arp_sdk.tool_registry import Client as ArpToolRegistryApiClient
from arp_sdk.tool_registry.api.default import get_v1alpha1_tools, post_v1alpha1_tool_invocations
from arp_sdk.tool_registry.models import (
    ErrorEnvelope,
    ToolDefinition,
    ToolInvocationResult,
    ToolInvocationResultError,
    ToolInvocationResultErrorDetails,
)


class ToolRegistryClient(Protocol):
    def list_tools(self) -> list[ToolDefinition]: ...

    def get_tool(self, name: str) -> ToolDefinition: ...

    def invoke(
        self,
        name: str,
        *,
        args: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> ToolInvocationResult: ...


@dataclass(slots=True)
class HttpToolRegistryClient:
    base_url: str
    timeout_s: float = 10.0
    client: Optional[ArpToolRegistryApiClient] = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = ArpToolRegistryApiClient(base_url=self.base_url.rstrip("/"), timeout=httpx.Timeout(self.timeout_s))

    def list_tools(self) -> list[ToolDefinition]:
        assert self.client is not None
        resp = get_v1alpha1_tools.sync(client=self.client)
        if resp is None:
            raise RuntimeError("Tool Registry list_tools returned no response")
        if isinstance(resp, ErrorEnvelope):
            raise RuntimeError(f"Tool Registry list_tools failed: {resp.error.code}: {resp.error.message}")
        return resp

    def get_tool(self, name: str) -> ToolDefinition:
        for tool in self.list_tools():
            if tool.name == name or tool.tool_id == name:
                return tool
        raise RuntimeError(f"Tool not found: {name}")

    def invoke(
        self,
        name: str,
        *,
        args: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> ToolInvocationResult:
        assert self.client is not None
        invocation_id = str(uuid4())
        body: dict[str, Any] = {"invocation_id": invocation_id, "tool_name": name, "args": args}
        if context is not None:
            body["context"] = context
        try:
            resp = post_v1alpha1_tool_invocations.sync(client=self.client, body=body)
        except httpx.TimeoutException as exc:
            details = ToolInvocationResultErrorDetails.from_dict({"exception": repr(exc)})
            err = ToolInvocationResultError(code="tool_registry.timeout", message="Tool Registry request timed out", details=details, retryable=True)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
        except httpx.HTTPError as exc:
            details = ToolInvocationResultErrorDetails.from_dict({"exception": repr(exc)})
            err = ToolInvocationResultError(code="tool_registry.http_error", message="Tool Registry request failed", details=details, retryable=True)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)

        if resp is None:
            err = ToolInvocationResultError(code="tool_registry.no_response", message="Tool Registry returned no response", retryable=True)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
        if isinstance(resp, ErrorEnvelope):
            err = ToolInvocationResultError.from_dict(resp.error.to_dict())
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
        return resp
