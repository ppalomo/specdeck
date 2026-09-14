"""What the API answers with, where that is not simply a domain model."""

from datetime import datetime
from pathlib import Path

from specdeck.domain.availability import Availability
from specdeck.domain.index import Index
from specdeck.domain.model import DomainModel
from specdeck.domain.repo import Repo, RepoKind


class RegisteredRepo(DomainModel):
    """A registered root, with how it is doing and how current what is known about it is.

    Availability and canonical state are answered separately and always: an interface that
    cannot tell "there are no changes" from "the disk is unplugged", or from "the OpenSpec
    CLI is not installed", has no way to say anything true to whoever is looking at it.
    """

    id: str
    name: str
    path: Path
    kind: RepoKind
    availability: Availability
    canonical: Availability | None = None
    """Whether the CLI could be asked. Absent when the root has not been read yet."""

    built_at: datetime | None = None
    """When what is known about this root was read. Absent when it has not been."""

    @classmethod
    def of(cls, repo: Repo, index: Index | None) -> "RegisteredRepo":
        """Put a registered root together with whatever is known about it."""
        return cls(
            id=repo.id,
            name=repo.name,
            path=repo.path,
            kind=repo.kind,
            availability=repo.availability,
            canonical=index.canonical if index is not None else None,
            built_at=index.built_at if index is not None else None,
        )


class Registration(DomainModel):
    """What has to be said to register a root: where it is."""

    path: Path
