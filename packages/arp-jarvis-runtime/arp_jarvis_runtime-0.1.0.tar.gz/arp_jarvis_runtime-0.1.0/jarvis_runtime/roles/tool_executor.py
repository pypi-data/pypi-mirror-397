from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from uuid import uuid4

from arp_sdk.tool_registry.models import ToolInvocationResult

from ..json_schema import ToolArgsValidationError, validate_tool_args
from ..tool_registry_client import ToolRegistryClient
from ..trace import TraceWriter
from .tool_args import ToolArgsGenerator


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    tool_name: str
    args: dict[str, Any]
    tool_result: ToolInvocationResult
    attempts: int


class ToolExecutor:
    def __init__(
        self,
        *,
        tool_registry: ToolRegistryClient,
        args_generator: ToolArgsGenerator,
        trace: Optional[TraceWriter] = None,
        max_arg_retries: int = 1,
    ):
        self._tool_registry = tool_registry
        self._args_generator = args_generator
        self._trace = trace
        self._max_arg_retries = max_arg_retries

    def execute(
        self,
        *,
        tool_name: str,
        intent: str,
        targets: list[str],
        context: dict[str, Any],
        trace_ctx: dict[str, Any],
        trace: Optional[TraceWriter] = None,
    ) -> ToolExecutionResult:
        trace_writer = trace or self._trace
        definition = self._tool_registry.get_tool(tool_name)
        tool_schema = definition.input_schema.to_dict()
        tool_description = definition.description if isinstance(definition.description, str) else None

        attempt = 0
        last_validation_error: Optional[dict[str, Any]] = None
        while True:
            attempt += 1
            args = self._args_generator.generate(
                tool_name=tool_name,
                tool_schema=tool_schema,
                context=context,
                intent=intent,
                targets=targets,
                tool_description=tool_description,
                validation_error=last_validation_error,
                trace=trace_writer,
            )
            if trace_writer:
                trace_writer.write(
                    "tool_args_generated",
                    {"tool_name": tool_name, "attempt": attempt, "args": args, "trace": trace_ctx},
                )

            try:
                validate_tool_args(tool_schema, args)
            except ToolArgsValidationError as exc:
                last_validation_error = exc.error.to_dict()
                if trace_writer:
                    trace_writer.write(
                        "tool_args_invalid",
                        {"tool_name": tool_name, "attempt": attempt, "error": exc.error.to_dict(), "trace": trace_ctx},
                    )
                if attempt <= self._max_arg_retries:
                    continue
                return ToolExecutionResult(
                    tool_name=tool_name,
                    args=args,
                    tool_result=ToolInvocationResult(invocation_id=f"local:{uuid4()}", ok=False, error=exc.error),
                    attempts=attempt,
                )

            if trace_writer:
                trace_writer.write("tool_invocation", {"tool_name": tool_name, "args": args, "trace": trace_ctx})

            invoke_context = dict(context)
            meta = context.get("meta")
            invoke_meta = dict(meta) if isinstance(meta, dict) else {}
            invoke_meta.update(trace_ctx)
            invoke_context["meta"] = invoke_meta

            result = self._tool_registry.invoke(tool_name, args=args, context=invoke_context)
            if trace_writer:
                trace_writer.write("tool_result", {"tool_name": tool_name, "result": result.to_dict(), "trace": trace_ctx})
            return ToolExecutionResult(tool_name=tool_name, args=args, tool_result=result, attempts=attempt)
