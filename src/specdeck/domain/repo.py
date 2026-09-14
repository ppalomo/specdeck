"""A root Specdeck was told to watch."""

from pathlib import Path
from typing import Literal

from specdeck.domain.availability import Availability
from specdeck.domain.model import DomainModel

RepoKind = Literal["repo", "store"]
"""Whether the root sits inside a code repository or stands on its own. A label only: both
have the same `<directory>/openspec/` shape and are read identically."""


class Repo(DomainModel):
    """One entry of the registry: a root registered by path, and how it is doing."""

    id: str
    name: str
    path: Path
    """Resolved to its absolute, real form, so the same root reached by a relative path, by
    `~` or through a symlink is recognised as the one it already is."""

    kind: RepoKind
    availability: Availability = Availability(available=True)
