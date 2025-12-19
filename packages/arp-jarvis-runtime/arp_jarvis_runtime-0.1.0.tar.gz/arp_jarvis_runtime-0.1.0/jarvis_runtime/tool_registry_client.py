from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol
from uuid import uuid4

import httpx

from arp_sdk.errors import ArpApiError
from arp_sdk.tool_registry import InvokeToolRequest as ArpInvokeToolRequest
from arp_sdk.tool_registry import ToolRegistryClient as ArpToolRegistryFacadeClient
from arp_sdk.tool_registry.client import Client as ArpToolRegistryApiClient
from arp_sdk.tool_registry.models import ToolDefinition, ToolInvocationResult, ToolInvocationResultError, ToolInvocationResultErrorDetails


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
    _sdk: ArpToolRegistryFacadeClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = ArpToolRegistryApiClient(base_url=self.base_url.rstrip("/"), timeout=httpx.Timeout(self.timeout_s))
        self._sdk = ArpToolRegistryFacadeClient(client=self.client)

    def list_tools(self) -> list[ToolDefinition]:
        try:
            return self._sdk.list_tools()
        except ArpApiError as exc:
            raise RuntimeError(f"Tool Registry list_tools failed: {exc.code}: {exc.message}") from exc

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
        invocation_id = str(uuid4())
        req = ArpInvokeToolRequest(invocation_id=invocation_id, tool_name=name, args=args, context=context)
        try:
            return self._sdk.invoke_tool(req)
        except httpx.TimeoutException as exc:
            details = ToolInvocationResultErrorDetails.from_dict({"exception": repr(exc)})
            err = ToolInvocationResultError(code="tool_registry.timeout", message="Tool Registry request timed out", details=details, retryable=True)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
        except httpx.HTTPError as exc:
            details = ToolInvocationResultErrorDetails.from_dict({"exception": repr(exc)})
            err = ToolInvocationResultError(code="tool_registry.http_error", message="Tool Registry request failed", details=details, retryable=True)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
        except ArpApiError as exc:
            payload: dict[str, Any] = {"code": exc.code, "message": exc.message}
            if isinstance(exc.details, dict):
                payload["details"] = exc.details
            err = ToolInvocationResultError.from_dict(payload)
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=err)
