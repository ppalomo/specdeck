---
title: The OpenSpec CLI contract
description: What `openspec … --json` actually returns, what it costs, and what its exit codes mean.
updated: 2026-09-13
---

# The OpenSpec CLI contract

What Specdeck can rely on from `openspec … --json`, measured rather than assumed.
[ADR 0003](adr/0003-talk-to-openspec-through-the-cli.md) decides *that* the CLI is the
source of canonical state; this document records *what the CLI says* and what it costs.

Measured against **OpenSpec 1.11.0** on 2026-09-13, over three real roots — `dotclaude`,
`wyndwalks-hq`, `wyndwalks-admin` — and a deliberately broken one. All three use the
`spec-driven` schema.

## The commands and their shapes

Every command is run with the root as working directory. Key sets were identical across
all roots.

| Command | Top level | The part that matters |
|---|---|---|
| `list --json` | `changes`, `root` | `changes[] {name, completedTasks, totalTasks, lastModified, status}` — active changes only, never the archive |
| `list --specs --json` | `specs`, `root` | `specs[] {id, requirementCount}` |
| `status --all --json` | `changes`, `message`, `root` | `changes[] {changeName, schemaName, planningHome, changeRoot, artifactPaths, artifacts, isComplete, isPlanningComplete, nextSteps, applyRequires, actionContext}` |
| `validate --all --json` | `items`, `summary`, `version`, `root` | `items[] {id, type, valid, issues[], durationMs}`; `issues[] {level, path, message}` |
| `schemas --json` | array | `{name, description, artifacts[], source}` — the artifact list of a schema |

`root` carries `{path, source}`, where `source: "nearest"` means the CLI walked upwards
from the working directory to find `openspec/config.yaml`.

## A non-zero exit code does not mean failure

`validate` exits `1` when any item is invalid **and still writes the complete JSON report
to stdout**. A path that is not an OpenSpec root also exits `1`, with a structured
explanation on stdout:

```json
{"changes": [], "root": null,
 "status": [{"severity": "error", "code": "no_openspec_root", "message": "…"}]}
```

So stdout is parsed first, and the exit code is a hint, never the verdict. Reading it the
other way round turns every root with one failing spec into a dead panel.

A root with no changes is not an error either: `{"changes": [], "message": "No active
changes."}`, exit `0`.

## The pipeline vocabulary

The `spec-driven` schema has four artifacts — proposal → specs → design → tasks — and each
reports `done`, `ready` or `blocked`, with `requires` naming what it waits for.

Status comes from whether the file exists, **not** from the order of the pipeline: a change
can report `tasks: done` while `design: ready`. Any view of the pipeline has to render a
hole in the middle.

## What it costs

Roughly **half a second per invocation, regardless of the root**. `openspec --version`
alone costs 124 ms, so ~125 ms is Node starting and ~400 ms is fixed per-command work.
A root with zero changes and zero specs costs the same as one with 15 archived changes and
115 requirements.

| | |
|---|---|
| Any of the four commands above | 516–740 ms |
| Four commands × three roots, in sequence | 6.5 s |
| The same three `status` calls, concurrent | 540 ms |
| Parsing an entire root in process (markdown-it-py) | 140 ms |

Two facts follow: the cost is per invocation, so roots are read concurrently; and half a
second never belongs in a render path.

## In-process parsing agrees with the CLI

Cross-checking a markdown-it-py parse against the CLI's own counts over 19 specs,
142 requirements, 343 scenarios and the tasks of a change in flight produced **zero
disagreements** — including tasks whose checkbox text wraps over several indented lines.

Structural headers are English (`## Requirements`, `### Requirement:`, `#### Scenario:`,
`## ADDED Requirements`) even when the prose is Spanish, so nothing in the parse depends on
the language of the artifacts.

## Spanish artifacts are permanently warned about

A root that validates green still carries issues. `wyndwalks-admin` passes 15 of 15 items
while reporting 165:

| Count | Level | Message |
|---|---|---|
| 125 | WARNING | `… should contain SHALL or MUST (RFC 2119 best practice for English specs)` |
| 40 | INFO | `Requirement text is very long (>500 characters)` |

Those warnings are the standing price of writing specs in Spanish with DEBE/NO DEBE, and
they will not go away. Only `ERROR` makes an item `valid: false` — a real one reads
`ADDED "…" must include at least one scenario`. An issue count that mixes the three levels
describes nothing.

## Not established

- Schemas other than `spec-driven`. `schemas --json` reports the artifact list of each, so
  the pipeline is discoverable rather than hard-coded, but no other schema has been read.
- Archived changes. No command lists them: `list --json` is active-only, so the archive is
  known from disk alone.
- Stores and worksets, which are out of scope for V1.
