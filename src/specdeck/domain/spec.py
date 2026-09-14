"""What a capability's behaviour says, whether it is in force or only proposed."""

from typing import Literal

from pydantic import computed_field

from specdeck.domain.location import Location
from specdeck.domain.model import DomainModel

Operation = Literal["ADDED", "MODIFIED", "REMOVED", "RENAMED"]
"""The kind of edit a delta declares over a capability."""


class Scenario(DomainModel):
    """A concrete case that proves a requirement."""

    name: str
    location: Location
    steps: tuple[str, ...] = ()
    """The WHEN / THEN / AND lines, kept as written rather than split into fields."""


class Requirement(DomainModel):
    """A single statement of behaviour, with the cases that prove it."""

    name: str
    text: str
    location: Location
    scenarios: tuple[Scenario, ...] = ()


class Spec(DomainModel):
    """The current, authoritative behaviour of one capability."""

    id: str
    """The capability's directory name under `openspec/specs/`."""

    purpose: str | None = None
    requirements: tuple[Requirement, ...] = ()

    @computed_field
    @property
    def requirement_count(self) -> int:
        """How many requirements this capability states."""
        return len(self.requirements)


class Delta(DomainModel):
    """What one change proposes to do to one capability.

    Never the whole spec: a delta states only the edit, which is why it carries the
    operation and the current spec does not.
    """

    capability: str
    operation: Operation
    requirements: tuple[Requirement, ...] = ()
