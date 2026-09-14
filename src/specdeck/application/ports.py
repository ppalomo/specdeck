"""What the use cases need of the world outside them, and nothing about how it is done.

A port is written here only when something substitutes it: a test that would otherwise need
the machine to be a certain way, or a second implementation already in sight. A port that
does neither is ceremony, and the rule is that it does not get written.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, Protocol

from specdeck.application.contents import RootContents
from specdeck.domain.model import DomainModel
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


Invocation = Literal["changes", "specs", "status", "validate"]
"""Everything Specdeck is allowed to ask the OpenSpec CLI.

The allowlist is a type rather than a list checked at runtime: there is no way to express an
invocation that is not one of these four, so "only read-only commands" is not a rule anybody
has to remember. All four read; none of them writes.
"""


class CliOutput(DomainModel):
    """What came back from one invocation of the OpenSpec CLI.

    The document is what counts and the exit code is a hint. `validate` exits non-zero
    whenever any item is invalid and still writes its whole report, and a path that is not a
    root exits non-zero and explains itself in JSON too. Reading it the other way round
    turns every root with one failing spec into a dead panel.
    """

    exit_code: int
    document: Any = None
    """The parsed JSON, or nothing when what came back was not JSON at all."""

    stderr: str = ""
    """What the CLI said beside its answer. It warns here and carries on, so this is not a
    failure by itself."""


class CliUnavailableError(Exception):
    """The OpenSpec command line is not on this machine."""

    def __init__(self, executable: str) -> None:
        """Say which executable was looked for."""
        self.executable = executable
        message = (
            f"the {executable!r} executable is not installed or not on the PATH, "
            f"so canonical state cannot be read"
        )
        super().__init__(message)


class CliTimedOutError(Exception):
    """An invocation did not finish in the time it is given."""

    def __init__(self, invocation: Invocation, seconds: float) -> None:
        """Say what was being run and how long it was given."""
        self.invocation = invocation
        message = f"openspec {invocation} did not finish within {seconds:g}s and was stopped"
        super().__init__(message)


class OpenSpecCli(Protocol):
    """The OpenSpec command line, which is where canonical state comes from.

    Behind a port because the real one starts a Node process that costs half a second, and
    because it is not installed on the machine that runs continuous integration: without
    something to put in its place, not one test of indexing would run there.
    """

    async def run(self, root: Path, invocation: Invocation) -> CliOutput:
        """Ask the CLI one of the four things it may be asked, with the root as cwd."""
        ...


class RootReader(Protocol):
    """Where the files of a root come from.

    Behind a port because the indexer has to be tried against roots that are a nuisance to
    have on a disk — one whose file raises when opened, one with a link that leads out of
    it, one that changed between two reads — and because what it returns is text, which a
    test can simply write.
    """

    async def read(self, root: Path) -> RootContents:
        """Read everything under the root's `openspec/`, and nothing outside it."""
        ...
