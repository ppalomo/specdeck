"""The real `openspec`, run against the fixture roots.

Everything else about the CLI is tested against answers captured from it, which is what lets
the suite run where it is not installed. Captured answers age, though, and these are what
notice: they run the binary itself and check that what it says now still reads into the same
shapes. They skip where it is missing, so they report in local work and never fail a build
for the machine it ran on.
"""

import shutil
from pathlib import Path
from typing import Any, cast

import pytest

from specdeck.application.openspec import (
    ChangeList,
    SpecList,
    StatusReport,
    ValidationReport,
    as_validation,
    not_a_root,
    read,
)
from specdeck.infrastructure.openspec_cli import OpenSpecProcess

pytestmark = pytest.mark.skipif(
    shutil.which("openspec") is None,
    reason="the openspec executable is not on this machine",
)


async def test_the_active_changes_are_still_what_was_captured(full_root: Path) -> None:
    listing = read(await OpenSpecProcess().run(full_root, "changes"), ChangeList)

    counts = {
        change.name: (change.completed_tasks, change.total_tasks) for change in listing.changes
    }
    assert counts == {"add-reminders": (1, 4), "retire-old-reports": (2, 3)}


async def test_the_specs_are_still_what_was_captured(full_root: Path) -> None:
    listing = read(await OpenSpecProcess().run(full_root, "specs"), SpecList)

    assert {spec.id: spec.requirement_count for spec in listing.specs} == {
        "task-management": 2,
        "reports": 1,
    }


async def test_the_pipeline_of_the_holed_root_still_has_its_hole(holed_root: Path) -> None:
    report = read(await OpenSpecProcess().run(holed_root, "status"), StatusReport)

    statuses = {artifact.id: artifact.status for artifact in report.changes[0].artifacts}
    assert statuses["tasks"] == "done"
    assert statuses["design"] == "ready"


async def test_spanish_specs_still_validate_green_while_warning(full_root: Path) -> None:
    report = read(await OpenSpecProcess().run(full_root, "validate"), ValidationReport)
    verdicts = [as_validation(item) for item in report.items]

    assert all(verdict.valid for verdict in verdicts)
    assert sum(verdict.warnings for verdict in verdicts) > 0
    assert sum(verdict.errors for verdict in verdicts) == 0


async def test_an_empty_root_answers_emptily_rather_than_failing(empty_root: Path) -> None:
    output = await OpenSpecProcess().run(empty_root, "changes")
    listing = read(output, ChangeList)

    assert output.exit_code == 0
    assert listing.changes == ()
    assert not_a_root(listing) is None


async def test_the_cli_warns_about_a_broken_config_and_answers_anyway(
    broken_root: Path,
) -> None:
    # Measured behaviour, and the reason stderr is never read as failure: the CLI complains
    # about a config it could not parse, ignores it, and still answers on stdout with 0.
    output = await OpenSpecProcess().run(broken_root, "changes")

    assert output.exit_code == 0
    assert "could not parse" in output.stderr
    assert read(output, ChangeList).changes[0].name == "half-written"


async def test_a_directory_with_no_root_above_it_still_says_so_in_json(tmp_path: Path) -> None:
    # Somewhere with no root anywhere above it, which the fixture directory is not: see the
    # test below for why that matters.
    output = await OpenSpecProcess().run(tmp_path, "changes")
    listing = read(output, ChangeList)

    assert output.exit_code != 0
    assert not_a_root(listing) is not None


async def test_the_cli_answers_for_the_nearest_root_above_wherever_it_is_run(
    not_a_root_dir: Path,
) -> None:
    """Which is why Specdeck decides what a root is instead of asking the CLI.

    This directory has no `openspec/` of its own, and it sits inside one that has. The CLI
    walks upwards and answers for the repository it found, reporting `source: nearest`. A
    registration that trusted the CLI to say "that is not a root" would quietly register a
    subdirectory and then show its parent's changes under the wrong name.
    """
    output = await OpenSpecProcess().run(not_a_root_dir, "changes")
    listing = read(output, ChangeList)

    assert output.exit_code == 0
    assert not_a_root(listing) is None
    document = cast("dict[str, Any]", output.document)
    assert document["root"] == {"path": str(Path.cwd()), "source": "nearest"}
