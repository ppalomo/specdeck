"""What the use cases need of the world outside them, and nothing about how it is done.

A port is written here only when something substitutes it: a test that would otherwise need
the machine to be a certain way, or a second implementation already in sight. A port that
does neither is ceremony, and the rule is that it does not get written.
"""

from collections.abc import Sequence
from typing import Protocol

from specdeck.domain.repo import Repo


class RegistryStore(Protocol):
    """Where the list of registered roots is kept between runs.

    The one thing Specdeck writes. Behind a port so that the tests of registering and
    unregistering never touch the configuration of whoever runs the suite.
    """

    def load(self) -> tuple[Repo, ...]:
        """Read the registered roots. An absent store reads as none registered."""
        ...

    def save(self, repos: Sequence[Repo]) -> None:
        """Write the registered roots, leaving what was there whole if it cannot finish."""
        ...
