from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arp_sdk.tool_registry.models import ToolInvocationResultError, ToolInvocationResultErrorDetails


@dataclass(frozen=True, slots=True)
class ToolArgsValidationError(Exception):
    error: ToolInvocationResultError

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.error.code}: {self.error.message}"


def validate_tool_args(schema: dict[str, Any], args: dict[str, Any]) -> None:
    issues = validate(args, schema)
    if issues:
        details = ToolInvocationResultErrorDetails.from_dict({"issues": issues})
        raise ToolArgsValidationError(
            error=ToolInvocationResultError(
                code="tool.invalid_args",
                message="Tool args did not match the tool input schema.",
                details=details,
                retryable=True,
            )
        )


def validate(instance: Any, schema: dict[str, Any]) -> list[str]:
    """Validate a JSON-like instance against a small subset of JSON Schema.

    Intentionally supports only the MVP subset:
    - object schemas with properties/required/additionalProperties
    - string schemas with minLength/enum
    - nullability via type=["string","null"]
    """
    issues: list[str] = []
    _validate(instance, schema, issues, path="$")
    return issues


def _validate(instance: Any, schema: dict[str, Any], issues: list[str], *, path: str) -> None:
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        if _matches_any_type(instance, schema_type):
            return
        issues.append(f"{path}: expected {schema_type}, got {type(instance).__name__}")
        return

    if schema_type == "object":
        _validate_object(instance, schema, issues, path=path)
        return

    if schema_type == "string":
        _validate_string(instance, schema, issues, path=path)
        return

    if schema_type is None:
        return

    if not _matches_any_type(instance, [schema_type]):
        issues.append(f"{path}: expected {schema_type}, got {type(instance).__name__}")


def _matches_any_type(instance: Any, types: list[str]) -> bool:
    for t in types:
        if t == "null" and instance is None:
            return True
        if t == "object" and isinstance(instance, dict):
            return True
        if t == "string" and isinstance(instance, str):
            return True
        if t == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool):
            return True
        if t == "integer" and isinstance(instance, int) and not isinstance(instance, bool):
            return True
        if t == "boolean" and isinstance(instance, bool):
            return True
        if t == "array" and isinstance(instance, list):
            return True
    return False


def _validate_object(instance: Any, schema: dict[str, Any], issues: list[str], *, path: str) -> None:
    if not isinstance(instance, dict):
        issues.append(f"{path}: expected object, got {type(instance).__name__}")
        return

    properties = schema.get("properties") or {}
    required = schema.get("required") or []
    additional = schema.get("additionalProperties", True)

    for key in required:
        if key not in instance:
            issues.append(f"{path}: missing required property '{key}'")

    for key, value in instance.items():
        if key in properties:
            subschema = properties[key]
            if isinstance(subschema, dict):
                _validate(value, subschema, issues, path=f"{path}.{key}")
            continue

        if additional is False:
            issues.append(f"{path}: unexpected property '{key}'")


def _validate_string(instance: Any, schema: dict[str, Any], issues: list[str], *, path: str) -> None:
    if not isinstance(instance, str):
        issues.append(f"{path}: expected string, got {type(instance).__name__}")
        return

    min_length = schema.get("minLength")
    if isinstance(min_length, int) and len(instance) < min_length:
        issues.append(f"{path}: string shorter than minLength={min_length}")

    enum = schema.get("enum")
    if isinstance(enum, list) and enum and instance not in enum:
        issues.append(f"{path}: value not in enum")
