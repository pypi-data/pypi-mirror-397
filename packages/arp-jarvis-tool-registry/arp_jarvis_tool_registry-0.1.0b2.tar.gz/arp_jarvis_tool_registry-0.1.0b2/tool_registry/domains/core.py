from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from ..catalog import Tool
from ..safe_eval import UnsafeExpressionError, safe_eval_arithmetic

from arp_sdk.tool_registry.models import ToolDefinition, ToolDefinitionInputSchema, ToolDefinitionSource


def load_tools() -> list[Tool]:
    return [
        Tool(definition=_echo_definition(), handler=_echo),
        Tool(definition=_calc_definition(), handler=_calc),
        Tool(definition=_time_now_definition(), handler=_time_now),
    ]


def _echo_definition() -> ToolDefinition:
    return ToolDefinition(
        tool_id="tool_echo",
        name="echo",
        description="Echoes the provided text.",
        input_schema=ToolDefinitionInputSchema.from_dict(
            {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            }
        ),
        source=ToolDefinitionSource.REGISTRY_LOCAL,
    )


def _calc_definition() -> ToolDefinition:
    return ToolDefinition(
        tool_id="tool_calc",
        name="calc",
        description="Evaluate a simple arithmetic expression.",
        input_schema=ToolDefinitionInputSchema.from_dict(
            {
                "type": "object",
                "properties": {"expression": {"type": "string", "minLength": 1}},
                "required": ["expression"],
                "additionalProperties": False,
            }
        ),
        source=ToolDefinitionSource.REGISTRY_LOCAL,
    )


def _time_now_definition() -> ToolDefinition:
    return ToolDefinition(
        tool_id="tool_time_now",
        name="time_now",
        description="Return the current time as an ISO 8601 timestamp in the provided IANA timezone (default UTC).",
        input_schema=ToolDefinitionInputSchema.from_dict(
            {
                "type": "object",
                "properties": {"tz": {"type": ["string", "null"], "default": "UTC"}},
                "required": ["tz"],
                "additionalProperties": False,
            }
        ),
        source=ToolDefinitionSource.REGISTRY_LOCAL,
    )


def _echo(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    return {"text": str(args.get("text") or "")}


def _calc(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    expression = str(args.get("expression") or "")
    try:
        value = safe_eval_arithmetic(expression)
    except UnsafeExpressionError as exc:
        # Raise a regular exception; catalog will normalize it.
        raise ValueError(str(exc)) from exc
    return {"expression": expression, "value": value}


def _time_now(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    tz_name = str(args.get("tz") or "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError(f"Unknown timezone: {tz_name}") from exc
    now = datetime.now(tz=tz)
    return {"tz": tz_name, "iso": now.isoformat()}
