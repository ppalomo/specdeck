"""Reading a root off the disk, and never a byte from outside it."""

import asyncio
from datetime import UTC, date, datetime
from pathlib import Path
from typing import cast

import yaml

from specdeck.application.contents import (
    CapabilitySpec,
    ChangeDocuments,
    Document,
    RootContents,
)
from specdeck.domain.availability import Unreadable

OPENSPEC = "openspec"
CONFIG = "config.yaml"
SPECS = "specs"
CHANGES = "changes"
ARCHIVE = "archive"
SPEC_FILE = "spec.md"
TASKS_FILE = "tasks.md"

ARCHIVED_PREFIX = 11
"""How much of `2026-08-01-date-every-task` is the date and the dash after it."""


class DiskRootReader:
    """The files of a root, read from where they are.

    Every path is resolved and checked against the root before it is opened, in this one
    place rather than at each call site. A symlink under `openspec/` that leads somewhere
    else is then simply not followed, and nothing downstream has to remember that it might.
    """

    async def read(self, root: Path) -> RootContents:
        """Read everything under the root's `openspec/`, and nothing outside it."""
        # All of this is blocking, and reading a root costs long enough to be worth keeping
        # off the loop that serves everything else.
        return await asyncio.to_thread(self._read, root)

    def _read(self, given: Path) -> RootContents:
        root = given.resolve()
        openspec = root / OPENSPEC
        unreadable: list[Unreadable] = []

        return RootContents(
            schema_name=self._schema(root, openspec / CONFIG, unreadable),
            specs=self._specs(root, openspec / SPECS, unreadable),
            changes=self._changes(root, openspec / CHANGES, unreadable),
            archived=self._changes(
                root, openspec / CHANGES / ARCHIVE, unreadable, archived=True
            ),
            unreadable=tuple(unreadable),
        )

    def _schema(self, root: Path, config: Path, unreadable: list[Unreadable]) -> str | None:
        text = self._text(root, config, unreadable)
        if text is None:
            return None

        try:
            written = yaml.safe_load(text)
        except yaml.YAMLError as malformed:
            unreadable.append(_could_not(root, config, malformed))
            return None

        if not isinstance(written, dict):
            return None

        schema: object = cast("dict[str, object]", written).get("schema")
        return schema if isinstance(schema, str) else None

    def _specs(
        self, root: Path, specs: Path, unreadable: list[Unreadable]
    ) -> tuple[CapabilitySpec, ...]:
        return tuple(
            written
            for found in _sorted(specs, SPEC_FILE)
            if (written := self._capability(root, specs, found, unreadable)) is not None
        )

    def _changes(
        self, root: Path, changes: Path, unreadable: list[Unreadable], *, archived: bool = False
    ) -> tuple[ChangeDocuments, ...]:
        if not _inside(root, changes) or not changes.is_dir():
            return ()

        found = sorted(
            path
            for path in changes.iterdir()
            if path.is_dir() and (archived or path.name != ARCHIVE)
        )
        return tuple(self._change(root, path, unreadable, archived=archived) for path in found)

    def _change(
        self, root: Path, change: Path, unreadable: list[Unreadable], *, archived: bool
    ) -> ChangeDocuments:
        tasks = change / TASKS_FILE
        text = self._text(root, tasks, unreadable) if tasks.is_file() else None
        written = Document(file=_relative(root, tasks), text=text) if text is not None else None
        specs = change / SPECS

        return ChangeDocuments(
            id=change.name,
            tasks=written,
            deltas=tuple(
                delta
                for found in _sorted(specs, SPEC_FILE)
                if (delta := self._capability(root, specs, found, unreadable)) is not None
            ),
            last_modified=_last_modified(change),
            archived_on=_archived_on(change.name) if archived else None,
        )

    def _capability(
        self, root: Path, specs: Path, found: Path, unreadable: list[Unreadable]
    ) -> CapabilitySpec | None:
        text = self._text(root, found, unreadable)
        if text is None:
            return None

        return CapabilitySpec(
            capability=str(found.parent.relative_to(specs)),
            file=_relative(root, found),
            text=text,
        )

    def _text(self, root: Path, file: Path, unreadable: list[Unreadable]) -> str | None:
        """Read a file, or say why it could not be read and carry on to the next one."""
        if not _inside(root, file):
            # A link out of the root is not followed and not complained about: it was never
            # part of this root, so there is nothing here that failed.
            return None

        try:
            return file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as unread:
            unreadable.append(_could_not(root, file, unread))
            return None


def _inside(root: Path, path: Path) -> bool:
    """Whether a path really is under the root, once links and `..` are resolved away."""
    return path.resolve().is_relative_to(root)


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def _sorted(specs: Path, name: str) -> list[Path]:
    """Every `spec.md` under a specs directory, including ones a level or more down."""
    return sorted(specs.rglob(name)) if specs.is_dir() else []


def _could_not(root: Path, file: Path, why: Exception) -> Unreadable:
    reason = getattr(why, "strerror", None) or str(why).splitlines()[0]
    return Unreadable(file=_relative(root, file), reason=reason)


def _last_modified(change: Path) -> datetime | None:
    """When anything in the change last changed, which is what its card is sorted by."""
    times = [path.stat().st_mtime for path in change.rglob("*") if path.is_file()]
    return datetime.fromtimestamp(max(times), tz=UTC) if times else None


def _archived_on(name: str) -> date | None:
    """Read the date an archived directory is named with, if it is named with one."""
    try:
        return date.fromisoformat(name[:ARCHIVED_PREFIX].rstrip("-"))
    except ValueError:
        return None
