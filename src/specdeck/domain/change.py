"""A unit of planned work: its artifacts, its tasks and what it proposes."""

from datetime import date, datetime
from typing import Literal

from pydantic import computed_field

from specdeck.domain.location import Location
from specdeck.domain.model import DomainModel
from specdeck.domain.spec import Delta
from specdeck.domain.validation import Validation

ArtifactStatus = Literal["done", "ready", "blocked", "skipped"]
"""Where an artifact stands. It follows from whether its file exists, not from the order
of the pipeline, so a change can have its tasks written and its design missing."""

ChangeStatus = Literal["planning", "in-progress", "complete", "archived"]
"""How far along a change is, as OpenSpec reports it."""


class Artifact(DomainModel):
    """One node of the change's pipeline, as the root's schema declares it."""

    id: str
    status: ArtifactStatus
    files: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    """The artifacts this one depends on. What draws the pipeline, instead of a list of
    four steps written into Specdeck."""


class Task(DomainModel):
    """One checkbox in `tasks.md`."""

    number: str
    """The number the task is written with, such as `1.2`. Empty when it has none."""

    text: str
    done: bool
    location: Location


class TaskGroup(DomainModel):
    """The tasks under one `## N. Title` heading."""

    title: str
    location: Location
    tasks: tuple[Task, ...] = ()


class Tasks(DomainModel):
    """Everything in a change's `tasks.md`, and how much of it is done."""

    groups: tuple[TaskGroup, ...] = ()

    @computed_field
    @property
    def total(self) -> int:
        """How many tasks the change has."""
        return sum(len(group.tasks) for group in self.groups)

    @computed_field
    @property
    def done(self) -> int:
        """How many of them are checked off."""
        return sum(1 for group in self.groups for task in group.tasks if task.done)


class ArtifactDocument(DomainModel):
    """What one of a change's artifacts says, and where it is."""

    artifact: str
    file: str
    text: str


class Change(DomainModel):
    """A plan: the documents that describe a piece of work and the tasks that carry it out.

    A change is not a git object. It usually maps to a branch and several commits, and it
    exists before any of them.
    """

    id: str
    """The change's directory name, which is also the branch the repository uses for it."""

    status: ChangeStatus
    schema_name: str | None = None
    artifacts: tuple[Artifact, ...] = ()
    tasks: Tasks = Tasks()
    deltas: tuple[Delta, ...] = ()
    documents: tuple[ArtifactDocument, ...] = ()
    """The markdown of the change's artifacts, so a proposal can be read as what it is."""
    validation: Validation | None = None
    """Absent when the OpenSpec CLI could not be asked. Never inferred from our own parse."""

    last_modified: datetime | None = None
    archived_on: date | None = None
    """The date in the archive directory's name. Only set once the change is archived."""
