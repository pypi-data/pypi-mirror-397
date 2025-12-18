from __future__ import annotations

import importlib
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from . import json_schema

from arp_sdk.tool_registry.models import (
    ToolDefinition,
    ToolInvocationResult,
    ToolInvocationResultError,
    ToolInvocationResultErrorDetails,
    ToolInvocationResultResult,
)


ToolHandler = Callable[[dict[str, Any], Optional[dict[str, Any]], Optional[dict[str, Any]]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class Tool:
    definition: ToolDefinition
    handler: ToolHandler


def load_domain_tools(domain_names: Iterable[str]) -> list[Tool]:
    tools: list[Tool] = []
    for domain_name in domain_names:
        module = importlib.import_module(f"tool_registry.domains.{domain_name}")
        load_fn = getattr(module, "load_tools", None)
        if not callable(load_fn):
            raise RuntimeError(f"Domain module tool_registry.domains.{domain_name} is missing load_tools()")
        loaded = load_fn()
        if not isinstance(loaded, list) or not all(isinstance(t, Tool) for t in loaded):
            raise RuntimeError(f"Domain module {domain_name} returned invalid tool list")
        tools.extend(loaded)
    return tools


class ToolCatalog:
    def __init__(self, tools: Iterable[Tool]):
        self._tools_by_id: dict[str, Tool] = {}
        self._tools_by_name: dict[str, Tool] = {}
        for tool in tools:
            tool_id = tool.definition.tool_id
            name = tool.definition.name
            if tool_id in self._tools_by_id:
                raise ValueError(f"Duplicate tool_id: {tool_id}")
            if name in self._tools_by_name:
                raise ValueError(f"Duplicate tool name: {name}")
            self._tools_by_id[tool_id] = tool
            self._tools_by_name[name] = tool

    def list_tools(self) -> list[ToolDefinition]:
        return [t.definition for t in self._tools_by_id.values()]

    def get_definition(self, tool_id: str) -> ToolDefinition:
        tool = self._tools_by_id.get(tool_id)
        if tool is None:
            raise KeyError(tool_id)
        return tool.definition

    def invoke(
        self,
        *,
        invocation_id: str,
        tool_id: str | None,
        tool_name: str | None,
        args: dict[str, Any],
        context: Optional[dict[str, Any]],
    ) -> ToolInvocationResult:
        start = time.perf_counter()

        tool = None
        if tool_id:
            tool = self._tools_by_id.get(tool_id)
        if tool is None and tool_name:
            tool = self._tools_by_name.get(tool_name)
        if tool is None:
            latency_ms = int((time.perf_counter() - start) * 1000)
            details: dict[str, Any] = {}
            if tool_id:
                details["tool_id"] = tool_id
            if tool_name:
                details["tool_name"] = tool_name
            error_details = ToolInvocationResultErrorDetails.from_dict(details)
            error = ToolInvocationResultError(
                code="tool.not_found",
                message="Unknown tool",
                details=error_details,
                retryable=False,
            )
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=error, duration_ms=latency_ms)

        issues = json_schema.validate(args, tool.definition.input_schema.to_dict())
        if issues:
            latency_ms = int((time.perf_counter() - start) * 1000)
            error_details = ToolInvocationResultErrorDetails.from_dict({"issues": issues})
            error = ToolInvocationResultError(
                code="tool.invalid_args",
                message="Tool arguments did not match input_schema",
                details=error_details,
                retryable=False,
            )
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=error, duration_ms=latency_ms)

        try:
            result = tool.handler(args, context, None)
            if not isinstance(result, dict):
                raise ValueError("Tool handler must return an object")
        except ValueError as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            details: dict[str, Any] = {"tool_id": tool.definition.tool_id, "tool_name": tool.definition.name}
            error_details = ToolInvocationResultErrorDetails.from_dict(details)
            error = ToolInvocationResultError(
                code="tool.execution_error",
                message=str(exc) or "Tool execution failed",
                details=error_details,
                retryable=False,
            )
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=error, duration_ms=latency_ms)
        except Exception as exc:  # pragma: no cover - defensive
            latency_ms = int((time.perf_counter() - start) * 1000)
            details: dict[str, Any] = {
                "tool_id": tool.definition.tool_id,
                "tool_name": tool.definition.name,
                "exception": repr(exc),
            }
            error_details = ToolInvocationResultErrorDetails.from_dict(details)
            error = ToolInvocationResultError(
                code="tool.handler_error",
                message="Tool handler raised an exception",
                details=error_details,
            )
            return ToolInvocationResult(invocation_id=invocation_id, ok=False, error=error, duration_ms=latency_ms)

        latency_ms = int((time.perf_counter() - start) * 1000)
        result_model = ToolInvocationResultResult.from_dict(result)
        return ToolInvocationResult(invocation_id=invocation_id, ok=True, result=result_model, duration_ms=latency_ms)
