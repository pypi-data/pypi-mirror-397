# Tool Registry

This repo contains the **Tool Registry** service: a standalone tool provider for ARP runtimes.

Current phase: MVP implementation (stdlib HTTP server).

## Design docs

- [`docs/intro.md`](docs/intro.md)
- [`docs/design/overview.md`](docs/design/overview.md)

## Install

```bash
pipx install arp-jarvis-tool-registry
python3 -m pip install arp-jarvis-tool-registry
```

## Run locally

Create a virtualenv, then install and run the service:

```bash
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install -e .

arp-jarvis-tool-registry
```

If port `8000` is already in use, it binds to a free port and logs it (or use `--port 0` to always pick a free port). Use `--auto-port` to fall back when an explicit `--port` (or `TOOL_REGISTRY_PORT`) is in use.

Env vars:

- `TOOL_REGISTRY_HOST` (default `127.0.0.1`)
- `TOOL_REGISTRY_PORT` (default `8000`)
- `TOOL_REGISTRY_DOMAINS` (default `core`)

Endpoints:

- `GET /v1/health`
- `GET /v1/version`
- `GET /v1/tools`
- `GET /v1/tools/{tool_id}`
- `POST /v1/tool-invocations` (body: `{"invocation_id":"...","tool_id":"...","args":{...}}` or `{"invocation_id":"...","tool_name":"...","args":{...}}`)

More docs:

- [`docs/intro.md`](docs/intro.md)
- [`docs/adding_tools.md`](docs/adding_tools.md)

## Run tests

From the repo root:

```bash
python3 -m unittest discover -v
```

Or (if you have `pytest` installed):

```bash
pytest -q
```

Optional (schema contract tests):

```bash
python3 -m pip install jsonschema
```

## MVP capabilities + known gaps

Capabilities:

- Tool discovery (`GET /v1/tools`) and detail (`GET /v1/tools/{tool_id}`).
- Validated invocation (`POST /v1/tool-invocations`) with normalized `ToolInvocationResult`/`ErrorEnvelope`.
- Simple in-repo “domain modules” pattern for adding tools.

Known gaps:

- No auth, rate limiting, or multi-tenant policy layer yet.
- Stdlib HTTP server only (FastAPI/ASGI swap is a future improvement).
- No MCP aggregation implementation in this MVP.
