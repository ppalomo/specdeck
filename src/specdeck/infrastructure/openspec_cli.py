"""Running the OpenSpec command line, which is the only process Specdeck starts."""

import asyncio
import json
from pathlib import Path

from specdeck.application.ports import CliOutput, Invocation

EXECUTABLE = "openspec"
TIMEOUT = 60.0
"""Long enough for any root, short enough that a command that will never finish does not
hold a reader for ever."""

ARGUMENTS: dict[Invocation, tuple[str, ...]] = {
    "changes": ("list", "--json"),
    "specs": ("list", "--specs", "--json"),
    "status": ("status", "--all", "--json"),
    "validate": ("validate", "--all", "--json"),
}
"""The whole allowlist, written out. Arguments are fixed here rather than assembled from
anything a caller passes, so there is nothing to inject into and nothing to validate."""


class NotAllowedError(Exception):
    """Something asked for an invocation that is not one of the four."""

    def __init__(self, invocation: str) -> None:
        """Say what was asked for and what is permitted."""
        self.invocation = invocation
        allowed = ", ".join(sorted(ARGUMENTS))
        message = f"{invocation!r} is not an OpenSpec invocation Specdeck may run: {allowed}."
        super().__init__(message)


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


class OpenSpecProcess:
    """The OpenSpec CLI, run as a subprocess.

    Never through a shell and never with an assembled string: the executable and its
    arguments go as a list, the root goes as the working directory, and a command that hangs
    is killed rather than waited on. A root path with a space or a semicolon in it is then
    just a path, which is the whole reason for doing it this way.
    """

    def __init__(self, executable: str = EXECUTABLE, timeout: float = TIMEOUT) -> None:
        """Run the given executable, allowing each invocation the given seconds."""
        self._executable = executable
        self._timeout = timeout

    async def run(self, root: Path, invocation: Invocation) -> CliOutput:
        """Ask the CLI one of the four things it may be asked, with the root as cwd."""
        arguments = ARGUMENTS.get(invocation)
        if arguments is None:
            raise NotAllowedError(invocation)

        try:
            process = await asyncio.create_subprocess_exec(
                self._executable,
                *arguments,
                cwd=root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except (FileNotFoundError, NotADirectoryError) as missing:
            raise CliUnavailableError(self._executable) from missing

        try:
            out, err = await asyncio.wait_for(process.communicate(), self._timeout)
        except TimeoutError as expired:
            process.kill()
            await process.wait()
            raise CliTimedOutError(invocation, self._timeout) from expired

        return CliOutput(
            exit_code=process.returncode if process.returncode is not None else 0,
            document=_document(out),
            stderr=err.decode(errors="replace"),
        )


def _document(out: bytes) -> object | None:
    """Read the answer as JSON, or say it was not JSON rather than raising over it."""
    try:
        return json.loads(out)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
