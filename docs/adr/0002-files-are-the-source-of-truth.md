---
title: "ADR 0002 — The files are the source of truth"
status: accepted
date: 2026-09-12
---

# ADR 0002 — The files are the source of truth

## Status

Accepted (2026-09-12).

## Context

Specdeck reads several repositories at once and renders changes, specs, tasks and
validation results. The obvious engineering reflex is to import all of that into a
database, index it and query it.

But the data already has an owner. `openspec/` is written by OpenSpec, by Claude Code, by
the user's editor and by `git pull`, all outside Specdeck and all without telling it. Any
copy Specdeck keeps is wrong the moment one of them writes, and a stale panel about the
state of your work is worse than no panel: it is a panel you stop trusting.

## Decision

Specdeck keeps **no database of its own**. The markdown and YAML files under each root's
`openspec/` are the only source of truth. Everything Specdeck holds is a cache in memory,
derived from disk and invalidated by a filesystem watcher.

The only thing Specdeck persists is its own registry of registered roots, in
`~/.config/specdeck/repos.json` — which repositories to look at, not what is in them.

## Consequences

- Editing a `.md` from anywhere is reflected in the UI in under a second. That is the
  product's core promise, and it falls out of this decision rather than being built.
- Cold start costs a full parse of every registered root. Acceptable at the expected scale
  (a handful of roots, tens of changes); if it stops being so, the answer is a cache keyed
  by mtime, not a database.
- There is no history beyond what the files carry. Trends over time, or "what changed last
  week" beyond the archive folder, would need a store and are out of scope.
- No migrations, no schema of our own to version, no divergence between two truths.
- Parsing must be tolerant. A file we do not fully understand is shown as text rather than
  dropped, because the file is right and the parser is what is incomplete.

## Alternatives considered

- **SQLite mirror of specs and changes.** Rejected: it breaks this decision outright and
  buys query power the UI does not need.
- **Persistent cache on disk keyed by mtime.** Not now. It is a performance measure with
  no measured problem, and it can be added later without changing the model.
