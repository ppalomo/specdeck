---
title: "ADR 0001 — A Python server, not Node"
status: accepted
date: 2026-09-12
---

# ADR 0001 — A Python server, not Node

## Status

Accepted (2026-09-12).

## Context

Specdeck serves a local web UI, watches the filesystem and runs the `openspec` CLI. An
earlier sketch of the project put the server in Node with Hono, on the grounds that
OpenSpec itself is a Node package: one toolchain, one language, and Zod schemas shared
between server and client.

Two things undercut that. OpenSpec does not publicly expose its artifact graph or its
parsers, so there is nothing to import — the integration is spawning a binary and reading
its JSON, which any language does equally well (see [ADR 0003](0003-talk-to-openspec-through-the-cli.md)).
And the shared-types argument is answered by generating TypeScript from the server's
OpenAPI document, which costs one build step.

What remains is which stack produces a better server for this shape of problem, and which
one the author is fastest in.

## Decision

The server is **Python 3.13 with FastAPI and uvicorn**, one asyncio process. Pydantic v2
models are the single definition of every payload; FastAPI publishes `/openapi.json` and
the frontend generates its types from it with `openapi-typescript`.

Node stays installed regardless, because the `openspec` CLI needs it. It is a runtime
dependency of the product, not the language of the product.

## Consequences

- Types are generated, not shared. `pnpm gen:types` runs in `dev` and `build`, and CI fails
  if the checked-in types are stale. That check is load-bearing; without it the two sides
  drift silently.
- Two toolchains in one repository: `uv` for the server, `pnpm` for `web/`. The `Makefile`
  hides the split behind `install`, `dev`, `check` and `build`.
- WebSockets, background tasks and subprocess handling come from the standard library and
  FastAPI, with no extra dependency.
- `watchfiles` gives a Rust-backed, FSEvents-based watcher on macOS — better than the Node
  equivalents for this job.
- Distribution becomes `uvx specdeck`, with the compiled frontend packaged inside the
  Python wheel. See [ADR 0005](0005-uv-over-poetry.md).

## Alternatives considered

- **Node + Hono.** Rejected: its main advantage disappears once types are generated from
  OpenAPI and OpenSpec turns out to be a CLI integration.
- **Next.js.** Rejected: SSR is pointless for a localhost tool, and it fits WebSockets and
  long-running processes poorly.
- **Django or Flask.** Rejected: WebSockets and OpenAPI would come from third-party
  packages instead of the framework.
