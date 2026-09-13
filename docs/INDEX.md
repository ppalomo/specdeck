---
title: Documentation index
description: One line per document, and where each kind of knowledge belongs.
updated: 2026-09-13
---

# Documentation index

## Reference

| Document | What it answers |
|---|---|
| [glossary.md](glossary.md) | The canonical name of every concept — and the pairs that get confused: change vs commit, current spec vs delta, archive vs sync. |

## Decisions

| ADR | Decision |
|---|---|
| [0001](adr/0001-python-server-over-node.md) | The server is Python and FastAPI, not Node — and why sharing types was not the reason it looked otherwise. |
| [0002](adr/0002-files-are-the-source-of-truth.md) | No database of our own: `openspec/` on disk is the truth, everything else is cache. |
| [0003](adr/0003-talk-to-openspec-through-the-cli.md) | OpenSpec is reached through its CLI and its JSON; in-process parsing renders but never decides. |
| [0004](adr/0004-v1-is-read-only.md) | V1 writes to no repository. Anything that would write is offered as a command to copy. |
| [0005](adr/0005-uv-over-poetry.md) | uv manages the interpreter, the dependencies and the packaging, breaking with Poetry on purpose. |

## Instructions

| Document | What it is |
|---|---|
| [../AGENTS.md](../AGENTS.md) | The only source of working instructions: language, stack, the hard rules, what is out of scope for V1, and how a change is carried out. |
| [../CLAUDE.md](../CLAUDE.md) | One line, importing `AGENTS.md`, so Claude Code and any other agent read the same file. |

## Where each kind of knowledge belongs

Keeping these apart is what stops documents from contradicting each other. One
authoritative source per topic; nothing repeats what another file already says.

| Place | Holds | Does not hold |
|---|---|---|
| `docs/` | Reference: what is true about the domain and why the closed decisions were closed. | How work should be carried out. |
| `AGENTS.md` | Instructions: the rules for working in this repository, and a map to these documents. | The content of these documents. |
| `openspec/` | Work in flight: the changes being planned and built, and the current specs. | Anything not being built. |
| `IDEAS.md` | The inbox: ideas with no commitment, dated, one per entry. | Decisions, plans or a backlog. |

New knowledge goes in exactly one of them. If it feels like it belongs in two, it is
probably a fact that belongs in `docs/` plus a rule that belongs in `AGENTS.md` — write
each half where it goes and do not duplicate.

## Not in this repository

The product plan and the bootstrap checklist are kept locally and deliberately left
untracked: they describe how this repository was built, which is of no use to anyone
reading the code.

`IDEAS.md` is untracked for a different reason. An inbox holds raw material — half-formed,
unpromised, sometimes never acted on — and published in a public repository it would read
as a roadmap. It lives in the repository root on the author's machine; the rule for
capturing into it is in `AGENTS.md`, which is where it belongs, because the rule is about
how we work and the entries are not.
