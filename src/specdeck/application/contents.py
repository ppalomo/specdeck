"""What a root has on disk, before anything is made of it.

Text and names, exactly as they were found. Turning any of it into requirements, tasks or
pipelines happens afterwards and elsewhere: this is the line between reading a root and
interpreting one.
"""

from datetime import date, datetime

from specdeck.domain.availability import Unreadable
from specdeck.domain.model import DomainModel


class Document(DomainModel):
    """The text of one file, and where it was."""

    file: str
    """Path of the file, relative to the root."""

    text: str


class CapabilitySpec(DomainModel):
    """A spec written about one capability: the one in force, or one a change proposes."""

    capability: str
    file: str
    text: str


class ArtifactDocument(DomainModel):
    """The markdown of one artifact, as it was written."""

    artifact: str
    """The artifact's name, which is its file's without the extension: `proposal`, `design`."""

    file: str
    text: str


class ChangeDocuments(DomainModel):
    """The files of one change, read and not yet understood."""

    id: str
    tasks: Document | None = None
    documents: tuple[ArtifactDocument, ...] = ()
    """Every other markdown file of the change, so its prose can be read rather than
    summarised. Tasks are left out: they are parsed rather than rendered."""
    deltas: tuple[CapabilitySpec, ...] = ()
    last_modified: datetime | None = None
    archived_on: date | None = None
    """Only set for a change found under the archive, taken from its directory's name."""


class RootContents(DomainModel):
    """Everything read from one root."""

    schema_name: str | None = None
    specs: tuple[CapabilitySpec, ...] = ()
    changes: tuple[ChangeDocuments, ...] = ()
    archived: tuple[ChangeDocuments, ...] = ()
    unreadable: tuple[Unreadable, ...] = ()
