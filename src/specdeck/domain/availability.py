"""Whether something could be read at all, and why not when it could not."""

from typing import Self

from specdeck.domain.model import DomainModel


class Availability(DomainModel):
    """The answer to "could this be read?", kept apart from the thing itself.

    A registered root whose disk is unplugged and an OpenSpec CLI that is not installed are
    both ordinary, and neither is an empty result: without this, "nothing here" and "could
    not look" arrive indistinguishable.
    """

    available: bool
    reason: str | None = None
    """Why not, in words meant for whoever has to fix it. Absent when available."""

    @classmethod
    def present(cls) -> Self:
        """Say that it could be read."""
        return cls(available=True)

    @classmethod
    def missing(cls, reason: str) -> Self:
        """Say that it could not, and why."""
        return cls(available=False, reason=reason)


class Unreadable(DomainModel):
    """A file that was there and could not be read, and what stopped it.

    Kept rather than swallowed: an artifact nobody can open is worth seeing, and a root that
    quietly indexes without it looks complete while it is not.
    """

    file: str
    """Path of the file, relative to the root it was found in."""

    reason: str
