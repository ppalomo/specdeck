"""Running the OpenSpec CLI: what may be run, how it is run, and what a hang costs.

These use a stand-in executable rather than the real `openspec`, so they say something about
how Specdeck starts a process — arguments as a list, the root as cwd, no shell anywhere near
it — on a machine that has no Node at all.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from specdeck.infrastructure.openspec_cli import (
    ARGUMENTS,
    CliTimedOutError,
    CliUnavailableError,
    NotAllowedError,
    OpenSpecProcess,
)

if TYPE_CHECKING:
    from specdeck.application.ports import Invocation


def a_stand_in(tmp_path: Path, body: str) -> str:
    """An executable that behaves however a test needs the CLI to behave."""
    script = tmp_path / "stand-in"
    script.write_text(f"#!{sys.executable}\nimport json, os, sys, time\n{body}\n")
    script.chmod(0o755)
    return str(script)


REPORTS_ITSELF = "print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))"


def an_awkwardly_named_root(tmp_path: Path) -> Path:
    """A root whose own name would take a shell command with it."""
    awkward = tmp_path / "a root; rm -rf $HOME && echo"
    (awkward / "openspec").mkdir(parents=True)
    return awkward


async def test_the_arguments_arrive_as_a_list_and_the_root_as_the_directory(
    tmp_path: Path, full_root: Path
) -> None:
    cli = OpenSpecProcess(a_stand_in(tmp_path, REPORTS_ITSELF))

    output = cli.run(full_root, "status")
    document = (await output).document

    assert document == {"argv": ["status", "--all", "--json"], "cwd": str(full_root)}


async def test_a_root_a_shell_would_have_mangled_is_just_a_path(tmp_path: Path) -> None:
    # If any of this ever went through a shell, this root would take the command with it.
    awkward = an_awkwardly_named_root(tmp_path)
    cli = OpenSpecProcess(a_stand_in(tmp_path, REPORTS_ITSELF))

    document = (await cli.run(awkward, "changes")).document

    assert isinstance(document, dict)
    assert document["cwd"] == str(awkward)
    assert document["argv"] == ["list", "--json"]


async def test_only_the_four_invocations_are_permitted(tmp_path: Path, full_root: Path) -> None:
    assert set(ARGUMENTS) == {"changes", "specs", "status", "validate"}
    assert all("--json" in arguments for arguments in ARGUMENTS.values())
    # Nothing in the allowlist writes: no archive, no init, no update, no new.
    assert all(
        arguments[0] in {"list", "status", "validate"} for arguments in ARGUMENTS.values()
    )

    # Nothing at this path, so anything that reached the point of starting a process would
    # fail differently from the refusal we expect.
    cli = OpenSpecProcess(str(tmp_path / "there-is-no-executable-here"))

    with pytest.raises(NotAllowedError, match="archive"):
        await cli.run(full_root, cast("Invocation", "archive"))


async def test_a_command_that_never_finishes_is_stopped(
    tmp_path: Path, full_root: Path
) -> None:
    cli = OpenSpecProcess(a_stand_in(tmp_path, "time.sleep(30)"), timeout=0.3)

    with pytest.raises(CliTimedOutError, match=r"did not finish within 0\.3s"):
        await cli.run(full_root, "validate")


async def test_a_cli_that_is_not_installed_says_so(tmp_path: Path, full_root: Path) -> None:
    cli = OpenSpecProcess(str(tmp_path / "openspec-that-is-not-there"))

    with pytest.raises(CliUnavailableError, match="not installed or not on the PATH"):
        await cli.run(full_root, "changes")


async def test_a_non_zero_exit_is_reported_beside_the_document_not_instead_of_it(
    tmp_path: Path, full_root: Path
) -> None:
    # What `openspec validate` does when something is invalid: the whole report, and exit 1.
    cli = OpenSpecProcess(
        a_stand_in(tmp_path, "print(json.dumps({'items': [], 'summary': {}}))\nsys.exit(1)")
    )

    output = await cli.run(full_root, "validate")

    assert output.exit_code == 1
    assert output.document == {"items": [], "summary": {}}


async def test_what_the_cli_says_beside_its_answer_is_kept(
    tmp_path: Path, full_root: Path
) -> None:
    # The real CLI warns on stderr about an unparseable config and answers anyway.
    says_both = (
        "print('Warning: could not parse config.yaml', file=sys.stderr)\n"
        "print(json.dumps({'changes': []}))"
    )
    cli = OpenSpecProcess(a_stand_in(tmp_path, says_both))

    output = await cli.run(full_root, "changes")

    assert output.exit_code == 0
    assert output.document == {"changes": []}
    assert "could not parse" in output.stderr


async def test_an_answer_that_is_not_json_is_said_to_be_missing_not_raised_over(
    tmp_path: Path, full_root: Path
) -> None:
    cli = OpenSpecProcess(a_stand_in(tmp_path, "print('command not found, probably')"))

    output = await cli.run(full_root, "status")

    assert output.document is None
    assert output.exit_code == 0
