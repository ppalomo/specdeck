"""The fixture roots, and what each one is here to prove.

They are written for this repository rather than copied from a real one: this repository is
public, and publishing fragments of another project's plans is a price no test justifies.
Each root exists because something measured in `docs/openspec-cli-contract.md` needs a place
to happen.
"""

import json
from pathlib import Path

import pytest

from specdeck.application.ports import CliOutput, Invocation

ROOTS = Path(__file__).resolve().parent / "fixtures" / "roots"
CAPTURED = Path(__file__).resolve().parent / "fixtures" / "cli"


@pytest.fixture
def full_root() -> Path:
    """A root with everything in it.

    Specs written in Spanish with DEBE, which validate green while carrying standing
    warnings; two active changes, one of them with all four delta operations; an archived
    change under its `YYYY-MM-DD-` prefix; grouped tasks; and one checkbox whose text
    continues over several indented lines, which the CLI counts as the single task it is.
    """
    return ROOTS / "full"


@pytest.fixture
def holed_root() -> Path:
    """A root whose only change has `tasks.md` written and `design.md` missing.

    Artifact status follows from whether a file exists, not from the order of the pipeline,
    so this is ordinary and has to survive being indexed without being tidied up.
    """
    return ROOTS / "holed"


@pytest.fixture
def empty_root() -> Path:
    """A root that is nothing but its `config.yaml`.

    No changes and no specs at all is not an error.
    """
    return ROOTS / "empty"


@pytest.fixture
def broken_root() -> Path:
    """A root with a `config.yaml` YAML refuses and an artifact that is not valid UTF-8.

    File permissions do not survive git, so the file that cannot be read is one whose bytes
    cannot be decoded — which does survive, and which raises on read exactly like the
    unreadable file it stands in for. A readable `tasks.md` sits beside it, so a test can
    tell "degraded" from "gave up".
    """
    return ROOTS / "broken"


@pytest.fixture
def not_a_root_dir() -> Path:
    """An ordinary directory with no `openspec/`. Registering it has to be refused."""
    return ROOTS / "not-a-root"


class CapturedCli:
    """An OpenSpec CLI that answers with what the real one answered, once, for the full root.

    Standing in for the real thing is what lets the indexer be tested where `openspec` is not
    installed — which is every continuous integration run. The answers are captured rather
    than invented, and `tests/test_openspec_cli_integration.py` is what notices when they
    stop being true.
    """

    def __init__(
        self, *, fails: Exception | None = None, answers: dict[str, str] | None = None
    ) -> None:
        """Answer from the captured documents, or fail the same way every time."""
        self.fails = fails
        self.answers = answers or {}
        self.asked: list[tuple[Path, str]] = []

    async def run(self, root: Path, invocation: Invocation) -> CliOutput:
        """Answer as the real CLI did, and remember having been asked."""
        self.asked.append((root, invocation))
        if self.fails is not None:
            raise self.fails

        name = self.answers.get(invocation, invocation)
        captured = CAPTURED / f"{name}.json"
        if not captured.is_file():
            return CliOutput(exit_code=0, document=None)

        return CliOutput(
            exit_code=1 if "invalid" in name or "not-a-root" in name else 0,
            document=json.loads(captured.read_text()),
        )


@pytest.fixture
def captured_cli() -> CapturedCli:
    """The OpenSpec CLI, answering what it answered when the fixtures were captured."""
    return CapturedCli()
