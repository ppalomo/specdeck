---
title: "ADR 0005 — uv, not Poetry"
status: accepted
date: 2026-09-13
---

# ADR 0005 — uv, not Poetry

## Status

Accepted (2026-09-13).

## Context

The author's other Python projects use Poetry, so consistency argues for Poetry here. Three
things specific to this project argue the other way.

The repository pins its own Python version. The machine runs 3.14 and Specdeck targets
3.13; Poetry needs an interpreter to already exist and would pull in pyenv, which is not
installed. `uv` installs and pins the interpreter itself.

Distribution is `uvx specdeck`: one command that installs and runs the tool in an ephemeral
environment, with the compiled frontend inside the wheel. That is the shipping mechanism in
the plan, and it is uv's.

And uv is already a dependency of this setup — the author's Claude Code marketplace uses it
to run `markitdown-mcp`.

## Decision

Dependencies, virtualenv, interpreter and packaging are managed with **uv**. The pinned
version lives in `.python-version` (3.13), the dependency graph in `pyproject.toml`, the
resolution in `uv.lock`, all committed. Builds are `uv build`.

## Consequences

- Consistency with the author's other repositories is broken on purpose. Anyone moving
  between them pays a small tax: `uv run` instead of `poetry run`. The `Makefile` absorbs
  most of it.
- The Python version is a property of the repository, not of the machine. Cloning and
  running `uv sync` reproduces the interpreter as well as the packages.
- Install and resolve times drop enough to matter in CI.
- uv is young and moves fast. The lockfile is committed and the version used is recorded in
  CI, so a breaking release is caught there rather than on a developer machine.

## Alternatives considered

- **Poetry**, for consistency with the author's other projects. Rejected for the three
  reasons above; consistency lost to interpreter management and to the distribution story.
- **pip with a plain venv.** Rejected: no lockfile, and the interpreter problem stands.
