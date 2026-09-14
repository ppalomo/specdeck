"""Turning a registered root into what Specdeck knows about it.

Two steps, in this order and never the other way round. The disk gives the structure and the
content: what changes there are, what specs, what text, on what lines. The OpenSpec CLI is
then laid over the top for the two things only it may decide — whether something is valid,
and what state each artifact is in. If the second step fails the first still stands, which
is what lets a root without the CLI installed be read at all.
"""

import asyncio
from datetime import UTC, datetime

from pydantic import ValidationError

from specdeck.application.contents import ChangeDocuments, RootContents
from specdeck.application.openspec import (
    ChangeList,
    ChangeStatus,
    SpecList,
    StatusReport,
    UnreadableAnswerError,
    ValidationItem,
    ValidationReport,
    as_artifact,
    as_validation,
    not_a_root,
    read,
)
from specdeck.application.ports import (
    CliTimedOutError,
    CliUnavailableError,
    Invocation,
    OpenSpecCli,
    RootReader,
)
from specdeck.domain.availability import Availability
from specdeck.domain.change import Artifact, ArtifactDocument, Change, Tasks
from specdeck.domain.change import ChangeStatus as Status
from specdeck.domain.index import Index
from specdeck.domain.model import DomainModel
from specdeck.domain.parsers.spec import parse_deltas, parse_spec
from specdeck.domain.parsers.tasks import parse_tasks
from specdeck.domain.repo import Repo
from specdeck.domain.spec import Spec, TouchedBy
from specdeck.domain.validation import Validation

ASKED: tuple[Invocation, ...] = ("changes", "specs", "status", "validate")

STATUSES: dict[str, Status] = {
    "planning": "planning",
    "in-progress": "in-progress",
    "complete": "complete",
}
UNKNOWN_STATUS: Status = "planning"


class Canonical(DomainModel):
    """What the OpenSpec CLI had to say about a root, or why it had nothing to say."""

    availability: Availability = Availability(available=True)
    changes: ChangeList = ChangeList()
    specs: SpecList = SpecList()
    status: StatusReport = StatusReport()
    validation: ValidationReport = ValidationReport()

    @classmethod
    def missing(cls, reason: str) -> "Canonical":
        """Nothing to say, and this is why."""
        return cls(availability=Availability.missing(reason))


class Indexer:
    """Reads a registered root into the index Specdeck answers from."""

    def __init__(self, reader: RootReader, cli: OpenSpecCli) -> None:
        """Read roots with the given reader, and ask the given CLI about them."""
        self._reader = reader
        self._cli = cli

    async def index(self, repo: Repo) -> Index:
        """Read one root. Whatever fails, an index comes back."""
        if not repo.availability.available:
            return Index(
                repo=repo,
                canonical=Availability.missing(
                    repo.availability.reason or "the root is not there"
                ),
                built_at=datetime.now(UTC),
            )

        contents, canonical = await asyncio.gather(
            self._reader.read(repo.path), self._canonical(repo)
        )

        # Parsing a root is on the order of a tenth of a second of pure work, which is worth
        # keeping off the loop that is serving every other root at the same time.
        return await asyncio.to_thread(compose, repo, contents, canonical)

    async def _canonical(self, repo: Repo) -> Canonical:
        try:
            answers = await asyncio.gather(
                *(self._cli.run(repo.path, invocation) for invocation in ASKED)
            )
        except (CliUnavailableError, CliTimedOutError) as why:
            return Canonical.missing(str(why))

        try:
            canonical = Canonical(
                changes=read(answers[0], ChangeList),
                specs=read(answers[1], SpecList),
                status=read(answers[2], StatusReport),
                validation=read(answers[3], ValidationReport),
            )
        except (UnreadableAnswerError, ValidationError) as why:
            return Canonical.missing(str(why))

        # The CLI answers for the nearest root above where it was run, so a path it does not
        # recognise is worth hearing in its own words rather than ours.
        refused = not_a_root(canonical.changes)
        return Canonical.missing(refused) if refused is not None else canonical


def compose(repo: Repo, contents: RootContents, canonical: Canonical) -> Index:
    """Put the two readings together into one index. Pure, and where the parsing happens."""
    changes = tuple(_change(documents, canonical) for documents in contents.changes)

    return Index(
        repo=repo,
        schema_name=contents.schema_name or _schema_the_cli_saw(canonical),
        specs=tuple(
            _touched(
                parse_spec(written.text, id=written.capability, file=written.file), changes
            )
            for written in contents.specs
        ),
        changes=changes,
        archived=tuple(_change(documents, canonical) for documents in contents.archived),
        canonical=canonical.availability,
        unreadable=contents.unreadable,
        built_at=datetime.now(UTC),
    )


def _touched(spec: Spec, changes: tuple[Change, ...]) -> Spec:
    """Say which active changes propose something about this capability."""
    return spec.model_copy(
        update={
            "touched_by": tuple(
                TouchedBy(change=change.id, operation=delta.operation)
                for change in changes
                for delta in change.deltas
                if delta.capability == spec.id
            )
        }
    )


def _change(documents: ChangeDocuments, canonical: Canonical) -> Change:
    summary = next((one for one in canonical.changes.changes if one.name == documents.id), None)
    reported = next(
        (one for one in canonical.status.changes if one.change_name == documents.id), None
    )
    verdict = next(
        (
            one
            for one in canonical.validation.items
            if one.id == documents.id and one.type in {"change", ""}
        ),
        None,
    )

    return Change(
        id=documents.id,
        status=_status(documents, summary.status if summary is not None else None),
        schema_name=reported.schema_name if reported is not None else None,
        artifacts=_artifacts(reported),
        tasks=_tasks(documents),
        deltas=tuple(
            delta
            for written in documents.deltas
            for delta in parse_deltas(
                written.text, capability=written.capability, file=written.file
            )
        ),
        documents=tuple(
            ArtifactDocument(artifact=one.artifact, file=one.file, text=one.text)
            for one in documents.documents
        ),
        validation=_validation(verdict, canonical),
        last_modified=(
            summary.last_modified
            if summary is not None and summary.last_modified is not None
            else documents.last_modified
        ),
        archived_on=documents.archived_on,
    )


def _status(documents: ChangeDocuments, reported: str | None) -> Status:
    if documents.archived_on is not None or reported is None:
        # The CLI lists active changes only, so a change it did not mention is either
        # archived or something it could not be asked about.
        return "archived" if documents.archived_on is not None else UNKNOWN_STATUS
    return STATUSES.get(reported, UNKNOWN_STATUS)


def _artifacts(reported: ChangeStatus | None) -> tuple[Artifact, ...]:
    return () if reported is None else tuple(as_artifact(one) for one in reported.artifacts)


def _tasks(documents: ChangeDocuments) -> Tasks:
    if documents.tasks is None:
        return Tasks()
    return parse_tasks(documents.tasks.text, file=documents.tasks.file)


def _validation(verdict: ValidationItem | None, canonical: Canonical) -> Validation | None:
    """Take the CLI's verdict, or nothing at all — never a guess of our own."""
    if verdict is None:
        return None
    return as_validation(verdict) if canonical.availability.available else None


def _schema_the_cli_saw(canonical: Canonical) -> str | None:
    """Fall back to the schema the CLI resolved, for a root whose config could not be read."""
    return next(
        (change.schema_name for change in canonical.status.changes if change.schema_name), None
    )
