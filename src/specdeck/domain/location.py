"""Where something lives in the files it was read from."""

from specdeck.domain.model import DomainModel


class Location(DomainModel):
    """The exact point a piece of an artifact was read from.

    Carried by every task, requirement and scenario so an editor can later be opened on it
    without searching the file again for text that may appear more than once.
    """

    file: str
    """Path of the file, relative to the root that was indexed."""

    line: int
    """Line the item starts on, counting from 1, as an editor counts."""
