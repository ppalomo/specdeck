"""What OpenSpec says about whether a root's artifacts hold up."""

from typing import Literal

from pydantic import computed_field

from specdeck.domain.model import DomainModel

IssueLevel = Literal["ERROR", "WARNING", "INFO"]
"""The severities OpenSpec reports. Only ERROR makes an item invalid."""


class Issue(DomainModel):
    """One thing OpenSpec has to say about one artifact."""

    level: IssueLevel
    path: str
    message: str


class Validation(DomainModel):
    """The verdict on one item, as the OpenSpec CLI gave it.

    The counts are kept apart on purpose. A root of specs written in Spanish carries
    hundreds of standing warnings about RFC 2119 wording while passing every check, so a
    single number that adds the three levels together describes nothing at all.
    """

    valid: bool
    issues: tuple[Issue, ...] = ()

    @computed_field
    @property
    def errors(self) -> int:
        """How many issues are the kind that makes an item invalid."""
        return sum(1 for issue in self.issues if issue.level == "ERROR")

    @computed_field
    @property
    def warnings(self) -> int:
        """How many issues are worth seeing but leave the item valid."""
        return sum(1 for issue in self.issues if issue.level == "WARNING")
