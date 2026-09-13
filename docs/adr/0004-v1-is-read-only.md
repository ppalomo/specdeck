---
title: "ADR 0004 — V1 never writes to a repository"
status: accepted
date: 2026-09-13
---

# ADR 0004 — V1 never writes to a repository

## Status

Accepted (2026-09-13).

## Context

The tempting features are the writing ones: tick a task, create a change, archive a
finished one. They are also the dangerous ones. The files Specdeck would write are being
written at the same time by Claude Code and by the user's editor, and a lost edit in a
proposal is expensive and hard to notice.

Concurrent writing is solvable — atomic writes, locking, conflict detection, an embedded
terminal for commands that prompt — but all of it is machinery in service of features that
do not yet exist, on top of a product whose value is being able to *see* the state of
several repositories at once.

## Decision

**V1 is read-only.** Specdeck does not create, modify, move or delete any file in any
registered root. It does not tick tasks, does not create changes, does not archive.

Only read-only commands run, from a closed allowlist (`status`, `list`, `show`, `validate`,
`doctor`, `instructions`). Anything that would write is offered as **Copy command**: the
exact command, ready to paste into a terminal or into Claude Code, executed by the user
elsewhere.

The only path Specdeck writes to is its own configuration directory,
`~/.config/specdeck/`.

## Consequences

- Specdeck cannot corrupt anyone's work. That property holds by construction, not by
  careful coding, which is the point.
- No atomic writes, no locking, no concurrent-write protection, no embedded pty terminal in
  V1. They arrive together in V2, when they are actually needed.
- Writing stays where it already works: the editor and the agent. Specdeck's job is to show
  the state and get you there — hence opening the editor at the exact line.
- Some flows are two-step: read here, act in the terminal. The Copy command button keeps
  the friction to one paste.
- The boundary must be defended in review. Every proposal that quietly adds a write is out
  of V1 scope regardless of how small it looks.

## Alternatives considered

- **Ticking tasks only.** Rejected: it looks harmless and is the exact case with the worst
  collision odds, since `tasks.md` is what the agent writes most often.
- **Write with a lock file.** Deferred to V2: the lock protects against Specdeck's own
  concurrency, not against an agent that does not honour it.
