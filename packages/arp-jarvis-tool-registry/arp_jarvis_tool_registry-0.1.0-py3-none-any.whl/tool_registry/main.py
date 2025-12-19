from __future__ import annotations

import argparse
import errno
import logging
import os
from typing import Sequence

from .server import ToolRegistryServer


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=None, help="Default: $TOOL_REGISTRY_HOST or 127.0.0.1")
    parser.add_argument("--port", type=int, default=None, help="Default: $TOOL_REGISTRY_PORT or 8000 (use 0 for auto)")
    parser.add_argument("--domains", default=None, help="Comma-separated. Default: $TOOL_REGISTRY_DOMAINS or core")
    parser.add_argument(
        "--auto-port",
        action="store_true",
        help="If the selected port is unavailable, bind to a free port instead.",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    host = args.host if args.host is not None else os.getenv("TOOL_REGISTRY_HOST", "127.0.0.1")

    env_port = os.getenv("TOOL_REGISTRY_PORT")
    if args.port is not None:
        port = args.port
        port_source = "cli"
    elif env_port is not None:
        port = int(env_port)
        port_source = "env"
    else:
        port = 8000
        port_source = "default"

    domains_raw = args.domains if args.domains is not None else os.getenv("TOOL_REGISTRY_DOMAINS", "core")
    domains = _split_csv(domains_raw)

    try:
        server = ToolRegistryServer(host=host, port=port, domains=domains)
    except OSError as exc:
        should_fallback = bool(args.auto_port) or port_source == "default"
        if exc.errno == errno.EADDRINUSE and should_fallback:
            logging.getLogger("tool_registry").warning("Port %s is already in use; binding to a free port instead.", port)
            server = ToolRegistryServer(host=host, port=0, domains=domains)
        else:
            raise
    server.serve_forever()
    return 0
