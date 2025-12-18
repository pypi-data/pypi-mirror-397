from __future__ import annotations

import importlib.metadata
import json
import logging
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

from .catalog import ToolCatalog, load_domain_tools

from arp_sdk.tool_registry.models import (
    ErrorEnvelope,
    ErrorEnvelopeError,
    ErrorEnvelopeErrorDetails,
    Health,
    HealthStatus,
    VersionInfo,
)
from arp_sdk.tool_registry.types import UNSET, Unset

logger = logging.getLogger("tool_registry.http")


def _package_version() -> str:
    try:
        return importlib.metadata.version("jarvis-tool-registry")
    except importlib.metadata.PackageNotFoundError:  # pragma: no cover
        return "0.0.0"


def _error_envelope(
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    retryable: bool | None = None,
) -> dict[str, Any]:
    details_value: ErrorEnvelopeErrorDetails | Unset
    if details is None:
        details_value = UNSET
    else:
        details_value = ErrorEnvelopeErrorDetails.from_dict(details)

    retryable_value: bool | Unset
    if retryable is None:
        retryable_value = UNSET
    else:
        retryable_value = retryable

    error = ErrorEnvelopeError(code=code, message=message, details=details_value, retryable=retryable_value)
    return ErrorEnvelope(error=error).to_dict()


class ToolRegistryApp:
    def __init__(self, catalog: ToolCatalog):
        self._catalog = catalog
        self._service_name = "jarvis-tool-registry"
        self._service_version = _package_version()

    def handle(self, *, method: str, path: str, body: Any) -> tuple[HTTPStatus, Any, Optional[str]]:
        parsed = urlparse(path)

        if method == "GET":
            return self._handle_get(parsed.path)
        if method == "POST":
            return self._handle_post(parsed.path, body)
        return (
            HTTPStatus.METHOD_NOT_ALLOWED,
            _error_envelope("request.method_not_allowed", "Not allowed"),
            None,
        )

    def _handle_get(self, path: str) -> tuple[HTTPStatus, Any, Optional[str]]:
        if path == "/v1alpha1/health":
            payload = Health(status=HealthStatus.OK, time=datetime.now(tz=timezone.utc)).to_dict()
            return HTTPStatus.OK, payload, None

        if path == "/v1alpha1/version":
            return (
                HTTPStatus.OK,
                VersionInfo(
                    service_name=self._service_name,
                    service_version=self._service_version,
                    supported_api_versions=["v1alpha1"],
                ).to_dict(),
                None,
            )

        if path == "/v1alpha1/tools":
            payload = [t.to_dict() for t in self._catalog.list_tools()]
            return HTTPStatus.OK, payload, None

        if path.startswith("/v1alpha1/tools/"):
            tool_id = path[len("/v1alpha1/tools/") :]
            if not tool_id:
                return HTTPStatus.NOT_FOUND, _error_envelope("route.not_found", "Not found"), None

            try:
                definition = self._catalog.get_definition(tool_id)
            except KeyError:
                return (
                    HTTPStatus.NOT_FOUND,
                    _error_envelope("tool.not_found", "Unknown tool", details={"tool_id": tool_id}, retryable=False),
                    tool_id,
                )

            return HTTPStatus.OK, definition.to_dict(), tool_id

        return HTTPStatus.NOT_FOUND, _error_envelope("route.not_found", "Not found"), None

    def _handle_post(self, path: str, body: Any) -> tuple[HTTPStatus, Any, Optional[str]]:
        if path != "/v1alpha1/tool-invocations":
            return HTTPStatus.NOT_FOUND, _error_envelope("route.not_found", "Not found"), None

        if body is None:
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_json", "Request body must be valid JSON", retryable=False),
                None,
            )

        if not isinstance(body, dict):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Request body must be an object", retryable=False),
                None,
            )

        invocation_id = body.get("invocation_id")
        if not isinstance(invocation_id, str) or not invocation_id.strip():
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Missing or invalid 'invocation_id'", retryable=False),
                None,
            )

        tool_id = body.get("tool_id")
        if tool_id is not None and (not isinstance(tool_id, str) or not tool_id.strip()):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Invalid 'tool_id'", retryable=False),
                None,
            )

        tool_name = body.get("tool_name")
        if tool_name is not None and (not isinstance(tool_name, str) or not tool_name.strip()):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Invalid 'tool_name'", retryable=False),
                None,
            )

        if not tool_id and not tool_name:
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "One of 'tool_id' or 'tool_name' is required", retryable=False),
                None,
            )

        args = body.get("args")
        if not isinstance(args, dict):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Missing or invalid 'args' (must be an object)", retryable=False),
                None,
            )

        context = body.get("context")
        if context is not None and not isinstance(context, dict):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Invalid 'context' (must be an object)", retryable=False),
                None,
            )

        caller = body.get("caller")
        if caller is not None and not isinstance(caller, dict):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Invalid 'caller' (must be an object)", retryable=False),
                None,
            )

        extensions = body.get("extensions")
        if extensions is not None and not isinstance(extensions, dict):
            return (
                HTTPStatus.BAD_REQUEST,
                _error_envelope("request.invalid_shape", "Invalid 'extensions' (must be an object)", retryable=False),
                None,
            )

        result = self._catalog.invoke(
            invocation_id=invocation_id.strip(),
            tool_id=tool_id.strip() if isinstance(tool_id, str) else None,
            tool_name=tool_name.strip() if isinstance(tool_name, str) else None,
            args=args,
            context=context,
        )
        tool_ref = (tool_id.strip() if isinstance(tool_id, str) else None) or (tool_name.strip() if isinstance(tool_name, str) else None)
        return HTTPStatus.OK, result.to_dict(), tool_ref


class ToolRegistryServer:
    def __init__(self, *, host: str, port: int, domains: list[str]):
        tools = load_domain_tools(domains)
        self._catalog = ToolCatalog(tools)
        self._app = ToolRegistryApp(self._catalog)
        self._host = host
        self._port = port
        self._httpd = ThreadingHTTPServer((host, port), self._make_handler())

    @property
    def server_address(self) -> tuple[str, int]:
        host, port = self._httpd.server_address[:2]
        return str(host), int(port)

    def serve_forever(self) -> None:
        host, port = self.server_address
        logger.info("tool_registry.start host=%s port=%s", host, port)
        self._httpd.serve_forever()

    def shutdown(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()

    def _make_handler(self):
        app = self._app

        class Handler(BaseHTTPRequestHandler):
            server_version = "ToolRegistry/0.1"

            def do_GET(self):  # noqa: N802
                started = time.perf_counter()
                request_id = self._get_request_id()
                try:
                    status, payload, tool_name = app.handle(method="GET", path=self.path, body=None)
                except Exception as exc:  # pragma: no cover - defensive
                    status, payload, tool_name = (
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        _error_envelope("server.error", str(exc)),
                        None,
                    )
                ok = int(status) < 400
                self._send_json(status=status, payload=payload, request_id=request_id)
                self._log(request_id, tool_name=tool_name, started=started, ok=ok)

            def do_POST(self):  # noqa: N802
                started = time.perf_counter()
                request_id = self._get_request_id()
                body = self._read_json_body()
                try:
                    status, payload, tool_name = app.handle(method="POST", path=self.path, body=body)
                except Exception as exc:  # pragma: no cover - defensive
                    status, payload, tool_name = (
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        _error_envelope("server.error", str(exc)),
                        None,
                    )
                ok = int(status) < 400
                self._send_json(status=status, payload=payload, request_id=request_id)
                self._log(request_id, tool_name=tool_name, started=started, ok=ok)

            def _read_json_body(self) -> Any:
                length = self.headers.get("Content-Length")
                if not length:
                    return None
                try:
                    raw = self.rfile.read(int(length))
                except Exception:
                    return None
                try:
                    return json.loads(raw.decode("utf-8"))
                except Exception:
                    return None

            def _get_request_id(self) -> str:
                incoming = self.headers.get("X-Request-Id")
                if incoming and str(incoming).strip():
                    return str(incoming).strip()
                return str(uuid4())

            def _send_json(self, *, status: HTTPStatus, payload: Any, request_id: str) -> None:
                encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                self.send_response(int(status))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("X-Request-Id", request_id)
                self.end_headers()
                self.wfile.write(encoded)

            def _log(self, request_id: str, *, tool_name: Optional[str], started: float, ok: bool) -> None:
                latency_ms = int((time.perf_counter() - started) * 1000)
                logger.info(
                    "request request_id=%s tool_name=%s ok=%s latency_ms=%s method=%s path=%s",
                    request_id,
                    tool_name or "-",
                    ok,
                    latency_ms,
                    self.command,
                    self.path,
                )

            def log_message(self, format: str, *args):  # noqa: A002
                # Use structured logging via _log instead of default stderr logs.
                return

        return Handler
