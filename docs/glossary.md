---
title: Glossary
description: Canonical vocabulary for Specdeck — OpenSpec concepts and Specdeck's own.
updated: 2026-09-13
---

# Glossary

One canonical term per concept, defined once. No other document redefines these terms;
they are the names to use in code, endpoints, UI strings and artifacts.

Names in `code font` are the identifiers used in the codebase. Where OpenSpec's own CLI
uses a different word, it is noted — OpenSpec's wording wins for anything that maps to
its output.

## OpenSpec

**Root** — a directory that contains `openspec/config.yaml`. Every repository and every
store is a root. Specdeck indexes roots, not projects.

**Change** (`Change`) — a unit of planned work, living in `openspec/changes/<change-id>/`.
It holds the artifacts that describe the work and the tasks that carry it out. A change is
a *plan*, not a git object: see [Change vs commit](#terms-that-get-confused).

**Change id** — the folder name of a change (`add-context7-mcp`). Kebab-case, stable, and
also the branch name the repository uses for that change.

**Artifact** (`Artifact`) — one of the documents a change is made of: `proposal.md`,
the delta specs, `design.md`, `tasks.md`. Each artifact has a status in the change's
pipeline: `done`, `ready`, `blocked` or `skipped`.

**Schema** — the artifact graph a change follows, with the dependencies between artifacts.
The default is `spec-driven` (`proposal → specs → design → tasks`). Resolved per project,
then user, then package. Specdeck draws the pipeline from the schema instead of hardcoding
the four steps.

**Capability** — a named area of behaviour, one folder under `openspec/specs/<capability>/`.
The unit that specs are grouped by.

**Spec** (`Spec`) — the current, authoritative description of a capability's behaviour,
at `openspec/specs/<capability>/spec.md`. Also called the *current spec* when it needs to
be told apart from a delta.

**Delta spec** (`Delta`) — the fragment of a spec that a change proposes, at
`openspec/changes/<change-id>/specs/<capability>/spec.md`. It is not the whole spec: it
only states what the change adds, modifies, removes or renames.

**Operation** — the kind of edit a delta declares: `ADDED`, `MODIFIED`, `REMOVED` or
`RENAMED`. It drives the colour semantics of the UI.

**Requirement** (`Requirement`) — a single behavioural statement inside a spec, written
as `### Requirement: …`.

**Scenario** (`Scenario`) — a concrete case that proves a requirement, written as
`#### Scenario: …` with `WHEN` / `THEN` / `AND` lines.

**Task** (`Task`) — one checkbox in `tasks.md` (`- [ ] 1.2 …`), grouped under a
**task group** (`## N. Title`). Tasks track execution; requirements track behaviour.

**Validation** (`Validation`) — the result of `openspec validate`, a list of **issues**
with a level (`ERROR`, `WARNING`), a path and a message. `--strict` promotes warnings.

**Doctor** — the health check of a root (`openspec doctor`): structure and references,
not the content of individual artifacts.

**Sync** — applying a change's deltas onto the current specs, so the specs describe the
new behaviour. The change stays where it is.

**Archive** — moving a finished change to `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`.
It is the step after sync, and it is what closes a change.

**Store** — a root that lives outside any code repository, marked by
`.openspec-store/store.yaml` and registered in a machine-wide registry. Used to plan
across repositories. Beta in OpenSpec 1.11; V2 for Specdeck, but a store registered by
path is indexed like any other root.

**Workset** — OpenSpec's grouping of related changes. Not used in V1.

**skip_specs** — a flag in a change's `.openspec.yaml` marking a change with no effect on
behaviour, so validation does not demand delta specs. Reserved for exactly that; never a
way to park an idea.

## Specdeck

**Registry** — Specdeck's list of roots the user registered by path, persisted in
`~/.config/specdeck/repos.json`. The only file Specdeck writes. Registration is manual;
there is no discovery.

**Registered repo** (`Repo`) — an entry in the registry: id, name, path, accent colour,
and `kind` (`repo` or `store`, decided by the presence of the store marker). "Repo" in
Specdeck always means a registered root, never an arbitrary git repository.

**Indexer** — the component that turns a root on disk into the in-memory model: config,
resolved schema, specs, active changes and archived changes.

**Parser** — the pure functions that read a single markdown file (`tasks.md`, `spec.md`)
into structured data with the source line of every item, so the editor can be opened at
that exact line.

**Watcher** — the per-root filesystem watch over `openspec/` that triggers selective
reindexing and the WebSocket events behind live refresh.

**Run** (`Run`) — one execution of an allowlisted command: what was run, when, exit code,
duration and captured output. Shown as history in the UI.

**Allowlist** — the closed set of read-only commands Specdeck is permitted to execute.
Nothing outside it runs; arguments are validated, never concatenated into a shell.

**Artifact pipeline** — the visual row of artifact nodes at the head of a change view,
drawn from the schema, each node carrying its status.

**Snapshot** — the full state the server sends a client on connect or reconnect, as
opposed to the incremental events that follow.

**Copy command** — the V1 answer to any action that would write to a repository: the exact
command is offered for the user to paste elsewhere, and Specdeck does not run it.

## Terms that get confused

| Not this | But this | Distinction |
|---|---|---|
| Change = commit | Change = plan | A change is a folder of documents describing intended work. It usually maps to a branch and several commits, but it is not a git object and it exists before any code. |
| Spec = delta spec | Current spec ≠ delta spec | The current spec, under `openspec/specs/`, states today's behaviour. A delta, under a change, states only the proposed edit. |
| Archive = sync | Sync then archive | Sync writes the deltas into the current specs. Archive moves the finished change aside. Syncing without archiving is normal; archiving without syncing loses the behaviour. |
| Store = repo | Store ≠ code repository | A store is a root with no code, used to plan across repositories. Same `openspec/` shape, different purpose. |
| Artifact = file | Artifact = node in the schema | `tasks.md` is a file; *tasks* is an artifact with a status and dependencies. Some artifacts span several files, as delta specs do. |
| Validate = doctor | Validate ≠ doctor | Validate checks artifact content against the schema. Doctor checks that the root itself is sound. |
| Task = requirement | Task ≠ requirement | Tasks are work to execute and get checked off. Requirements are behaviour and live in specs. |
