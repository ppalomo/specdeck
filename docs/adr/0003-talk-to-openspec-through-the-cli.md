---
title: "ADR 0003 — Talk to OpenSpec through its CLI"
status: accepted
date: 2026-09-12
---

# ADR 0003 — Talk to OpenSpec through its CLI

## Status

Accepted (2026-09-12).

## Context

Specdeck needs what OpenSpec knows: the artifact graph of a schema, the status of every
change, validation issues, resolved paths. There are three ways to get it — import the npm
package and call its internals, reimplement its logic, or run the CLI and read its JSON.

The npm package does not publicly expose the artifact graph or the parsers, so the first
option means depending on internals that carry no compatibility promise. The second means
maintaining a second implementation of a tool that ships often, and being subtly wrong
about the tool the user actually runs.

OpenSpec 1.11 exposes `--json` on `list`, `status`, `show`, `validate`, `doctor`,
`instructions` and `schemas` — everything the UI needs.

## Decision

All canonical state comes from the **CLI**, invoked as `openspec … --json` with the root
as working directory, through `asyncio.create_subprocess_exec` — argument lists, no shell.
Each output is parsed into a Pydantic model declared with `extra='ignore'`.

Specdeck never reimplements OpenSpec's rules: what is valid, what a schema requires, what
status an artifact has, is whatever the CLI says.

One deliberate exception: **parsing for rendering**. Spawning the CLI costs around half a
second per invocation whatever the root ([the CLI contract](../openspec-cli-contract.md)),
far too slow for every keystroke-sized change on disk, so `tasks.md` and `spec.md` are
parsed in-process for display and task counts, with the CLI refreshed on a longer debounce
as the canonical answer. In-process parsing renders; it never decides.

## Consequences

- Specdeck survives OpenSpec releases: new fields are ignored, and the contract is the
  documented CLI surface rather than internals.
- The `openspec` binary — and therefore Node — is a hard runtime requirement. `specdeck
  doctor` checks for it and explains how to install it.
- A version mismatch is a real risk: `openspec --version` is read at startup and a warning
  is shown when it is not a tested version. Fixtures are kept per version.
- Subprocess cost shapes the design: a debounce per root, a cap on concurrent spawns, and a
  60 s timeout per run.
- Two code paths describe the same data (in-process parse and CLI JSON). They must agree on
  vocabulary; the CLI wins on conflicts, and the glossary records the shared terms.

## Alternatives considered

- **Import `@fission-ai/openspec` internals.** Rejected: no public API, no stability
  guarantee, and it would force the server to be Node.
- **Reimplement the parsing and validation rules.** Rejected: duplicating a moving target,
  with the failure mode of disagreeing with the tool the user trusts.
