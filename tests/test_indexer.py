"""Indexing a root: the disk first, the CLI over the top, and neither one alone."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from conftest import CapturedCli
from specdeck.application.indexer import Indexer
from specdeck.application.ports import CliTimedOutError, CliUnavailableError
from specdeck.domain.availability import Availability
from specdeck.domain.repo import Repo
from specdeck.infrastructure.disk import DiskRootReader


def a_repo(path: Path, name: str = "full") -> Repo:
    return Repo(id=f"{name}-abc123", name=name, path=path, kind="repo")


async def test_a_root_is_read_into_its_specs_changes_and_archive(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    assert index.schema_name == "spec-driven"
    assert {spec.id: spec.requirement_count for spec in index.specs} == {
        "task-management": 2,
        "reports": 1,
    }
    assert [change.id for change in index.changes] == ["add-reminders", "retire-old-reports"]
    assert [change.id for change in index.archived] == ["2026-08-01-date-every-task"]


async def test_the_task_counts_are_the_ones_the_cli_reports(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    counted = {change.id: (change.tasks.done, change.tasks.total) for change in index.changes}
    assert counted == {"add-reminders": (1, 4), "retire-old-reports": (2, 3)}


async def test_a_pipeline_with_a_hole_keeps_its_hole(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    # `tasks.md` written while `design.md` is not is ordinary. Tidying it into an order the
    # disk does not have would be inventing the one thing the CLI is asked about.
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))
    holed = next(change for change in index.changes if change.id == "retire-old-reports")

    assert {artifact.id: artifact.status for artifact in holed.artifacts} == {
        "proposal": "done",
        "specs": "done",
        "design": "ready",
        "tasks": "done",
    }
    assert holed.artifacts[3].requires == ("specs", "design")


async def test_the_pipeline_comes_from_the_schema_the_root_resolves(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    assert all(change.schema_name == "spec-driven" for change in index.changes)
    assert all(change.artifacts for change in index.changes)


async def test_the_deltas_of_a_change_arrive_with_their_operations(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))
    retiring = next(change for change in index.changes if change.id == "retire-old-reports")

    assert [(delta.capability, delta.operation) for delta in retiring.deltas] == [
        ("reports", "MODIFIED"),
        ("reports", "REMOVED"),
        ("reports", "RENAMED"),
    ]


async def test_the_verdict_on_a_change_is_the_clis(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))
    change = index.changes[0]

    assert change.validation is not None
    assert change.validation.valid
    assert change.validation.warnings == 2
    assert change.validation.errors == 0


async def test_an_archived_change_says_it_is_archived_and_when(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))
    archived = index.archived[0]

    assert archived.status == "archived"
    assert archived.archived_on == date(2026, 8, 1)
    assert archived.tasks.total == 2


async def test_an_empty_root_indexes_to_an_empty_index_not_an_error(empty_root: Path) -> None:
    index = await Indexer(DiskRootReader(), CapturedCli(answers={"changes": "nothing"})).index(
        a_repo(empty_root, "empty")
    )

    assert index.specs == ()
    assert index.changes == ()
    assert index.unreadable == ()
    assert index.schema_name == "spec-driven"


async def test_an_index_says_when_it_was_built(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    # Nothing is watching the files yet, so the honest answer to "is this current?" is when
    # it was read rather than a promise that it is.
    before = datetime.now(UTC)

    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    assert before <= index.built_at <= datetime.now(UTC)


async def test_a_cli_that_is_not_installed_leaves_the_index_standing(full_root: Path) -> None:
    absent = CapturedCli(fails=CliUnavailableError("openspec"))

    index = await Indexer(DiskRootReader(), absent).index(a_repo(full_root))

    # Everything the disk knows is here.
    assert len(index.specs) == 2
    assert [change.id for change in index.changes] == ["add-reminders", "retire-old-reports"]
    assert index.changes[0].tasks.total == 4
    # And the two things only the CLI may decide are absent, with a reason.
    assert not index.canonical.available
    assert index.canonical.reason is not None
    assert "not installed" in index.canonical.reason
    assert all(change.validation is None for change in index.changes)
    assert all(change.artifacts == () for change in index.changes)


async def test_a_cli_that_hangs_is_treated_the_same_as_one_that_is_missing(
    full_root: Path,
) -> None:
    hung = CapturedCli(fails=CliTimedOutError("validate", 60.0))

    index = await Indexer(DiskRootReader(), hung).index(a_repo(full_root))

    assert len(index.changes) == 2
    assert not index.canonical.available
    assert index.canonical.reason is not None
    assert "did not finish" in index.canonical.reason


async def test_an_answer_that_is_not_json_leaves_the_index_standing(full_root: Path) -> None:
    asked = ("changes", "specs", "status", "validate")
    nonsense = CapturedCli(answers=dict.fromkeys(asked, "nothing"))

    index = await Indexer(DiskRootReader(), nonsense).index(a_repo(full_root))

    assert len(index.changes) == 2
    assert not index.canonical.available


async def test_a_root_the_cli_does_not_recognise_is_explained_in_its_own_words(
    full_root: Path,
) -> None:
    elsewhere = CapturedCli(answers={"changes": "not-a-root"})

    index = await Indexer(DiskRootReader(), elsewhere).index(a_repo(full_root))

    assert not index.canonical.available
    assert index.canonical.reason == "No OpenSpec root found from the current directory."


async def test_what_could_not_be_read_is_named_and_the_rest_indexed(broken_root: Path) -> None:
    absent = CapturedCli(fails=CliUnavailableError("openspec"))

    index = await Indexer(DiskRootReader(), absent).index(a_repo(broken_root, "broken"))

    assert index.schema_name is None
    assert [unread.file for unread in index.unreadable] == [
        "openspec/config.yaml",
        "openspec/changes/half-written/proposal.md",
    ]
    # The change beside the broken config is still here, with the tasks that could be read.
    assert index.changes[0].id == "half-written"
    assert index.changes[0].tasks.total == 1


async def test_a_root_that_is_not_there_is_not_even_read(tmp_path: Path) -> None:
    gone = Repo(
        id="gone-abc123",
        name="gone",
        path=tmp_path / "not-here",
        kind="repo",
        availability=Availability.missing("the path no longer exists"),
    )
    never_asked = CapturedCli()

    index = await Indexer(DiskRootReader(), never_asked).index(gone)

    assert never_asked.asked == []
    assert index.changes == ()
    assert index.canonical.reason == "the path no longer exists"


@pytest.mark.parametrize("invocation", ["changes", "specs", "status", "validate"])
async def test_the_cli_is_asked_for_all_four_things_at_once(
    full_root: Path, captured_cli: CapturedCli, invocation: str
) -> None:
    await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    assert (full_root, invocation) in captured_cli.asked


async def test_a_capability_says_which_changes_are_touching_it(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    reports = next(spec for spec in index.specs if spec.id == "reports")
    touching = {(one.change, one.operation) for one in reports.touched_by}

    # `retire-old-reports` modifies it, removes a requirement and renames another.
    assert touching == {
        ("retire-old-reports", "MODIFIED"),
        ("retire-old-reports", "REMOVED"),
        ("retire-old-reports", "RENAMED"),
    }


async def test_a_capability_nobody_is_touching_says_so_with_an_empty_list(
    tmp_path: Path, captured_cli: CapturedCli
) -> None:
    root = tmp_path / "quiet"
    (root / "openspec" / "specs" / "untouched").mkdir(parents=True)
    (root / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    (root / "openspec" / "specs" / "untouched" / "spec.md").write_text(
        "## Purpose\n\nNadie la está tocando.\n"
    )

    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(root, "quiet"))

    assert index.specs[0].touched_by == ()


async def test_an_archived_change_is_not_reported_as_touching_a_capability(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    # The archive is history, not work in flight: a capability's list is what is being
    # proposed about it now.
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))

    tasks = next(spec for spec in index.specs if spec.id == "task-management")

    assert all(one.change != "2026-08-01-date-every-task" for one in tasks.touched_by)


async def test_a_change_carries_the_markdown_of_its_artifacts(
    full_root: Path, captured_cli: CapturedCli
) -> None:
    index = await Indexer(DiskRootReader(), captured_cli).index(a_repo(full_root))
    reminders = next(change for change in index.changes if change.id == "add-reminders")

    written = {one.artifact: one for one in reminders.documents}

    assert set(written) == {"proposal", "design"}
    assert written["proposal"].text.startswith("## Why")
    assert written["proposal"].file == "openspec/changes/add-reminders/proposal.md"
    # The tasks are parsed rather than rendered, so they are not among the documents.
    assert "tasks" not in written
