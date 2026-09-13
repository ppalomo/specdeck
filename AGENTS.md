# Specdeck — working instructions

A local web dashboard that reads the OpenSpec directories of several repositories at once
and shows them properly: the pipeline of each change, its deltas, its tasks, its validation,
refreshed live from disk. **V1 is read-only**: it shows, validates and opens your editor,
and never writes to a repository.

This file is the only source of instructions. Facts about the domain live in `docs/`; do
not restate them here.

## Language

Everything committed to this repository is written in **English**: code, comments, docs,
commit messages and UI strings. The one exception is the artifacts OpenSpec generates
inside `openspec/changes/`, which are written in **Spanish** as `openspec/config.yaml`
declares. Never add an i18n layer: the interface is English only.

## Stack — decided, not open

| Side | Stack |
|---|---|
| Server | Python 3.13 · FastAPI · uvicorn · Pydantic v2 · watchfiles · markdown-it-py · Typer, managed with **uv** |
| Web | React 19 · Vite · TypeScript · TanStack Router/Query · Tailwind v4 · shadcn/ui · Framer Motion, managed with **pnpm** |
| Contracts | Pydantic models → FastAPI `/openapi.json` → `openapi-typescript`. Types are generated, never hand-written |
| Quality | ruff · pyright · pytest + pytest-asyncio · Vitest · Playwright |

Proposing a different library is fine; proposing a different stack is reopening a closed
decision, and needs a reason that the ADR does not already answer.

## Hard rules

1. **Never write to a registered repository.** Not a file, not a checkbox, not a command
   that would. The only path Specdeck writes to is `~/.config/specdeck/`. Actions that
   would write are surfaced as a command for the user to copy. ([ADR 0004](docs/adr/0004-v1-is-read-only.md))
2. **The files are the truth.** No database. Everything in memory is a cache derived from
   disk and invalidated by the watcher. ([ADR 0002](docs/adr/0002-files-are-the-source-of-truth.md))
3. **Canonical state comes from the CLI.** `openspec … --json`, parsed into Pydantic models
   with `extra='ignore'`. In-process parsing exists to render fast; it never decides what is
   valid or what an artifact's status is. ([ADR 0003](docs/adr/0003-talk-to-openspec-through-the-cli.md))
4. **No arbitrary execution.** Allowlisted read-only commands only, `create_subprocess_exec`
   with an argument list, never `shell=True`, `cwd` always the root, 60 s timeout.
5. **Stay inside registered roots.** Resolve every path and check the prefix before reading
   it. Listen on `127.0.0.1` only.
6. **Design is a requirement, not a finish.** Empty and error states are designed. Nothing
   flickers on refresh. No horizontal scroll in any view.
7. **Say what you do not know.** When a spec or a task is ambiguous, write
   `[NEEDS CLARIFICATION: the question]` and stop. Never invent a decision and never claim
   work is done without having run it.

## Out of scope for V1

Writing to repositories · automatic repository discovery · OpenSpec stores beyond
registering one by path · a markdown editor · an embedded terminal · worksets. These are
V2. A proposal that includes one of them is out of scope, however small it looks.

## How we work

- Every unit of work is an OpenSpec change: `/opsx:propose` → `/opsx:apply` → `/opsx:verify`
  → `/opsx:sync` → `/opsx:archive`. Plan first; write no code during `propose`.
- `/opsx:apply` does **one task at a time**, then stops and says which requirement it covers.
- Claims of completion need executed evidence — the command and its output — not an
  assertion. Stopping when work merely looks done is the failure mode to avoid.
- Commits follow Conventional Commits, in English, one concern per commit.
- Each change is developed on its own branch, named after the change id.
- When a change closes, update this file with the one line that says what now exists, and
  prune whatever it made obsolete.
- When something is an idea rather than the current task, it does not become a change. See
  the inbox rule below.

## Map

- [docs/INDEX.md](docs/INDEX.md) — every document, one line each, and where new knowledge belongs.
- [docs/glossary.md](docs/glossary.md) — the canonical name of every concept. Use these names in code, endpoints and UI.
- [docs/adr/](docs/adr/) — why the closed decisions are closed. Read before reopening one.

## Ideas

When the user says "apunta esto", "idea:" or otherwise hands over something that is not the
current task, add a dated entry at the top of [IDEAS.md](IDEAS.md), implement nothing, and
return to the task in progress. Never turn an idea into an OpenSpec change directly: ideas
reach OpenSpec through `/opsx:explore` and `/opsx:propose`, and the entry is deleted from
`IDEAS.md` when its change is proposed.
