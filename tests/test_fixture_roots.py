"""The fixture roots are what the tests that use them are going to assume."""

from pathlib import Path

import pytest


def test_the_full_root_has_specs_changes_and_an_archive(full_root: Path) -> None:
    openspec = full_root / "openspec"

    assert (openspec / "config.yaml").is_file()
    capabilities = {path.name for path in (openspec / "specs").iterdir()}
    assert capabilities == {"task-management", "reports"}

    changes = openspec / "changes"
    assert {path.name for path in changes.iterdir() if path.is_dir()} == {
        "add-reminders",
        "retire-old-reports",
        "archive",
    }
    archived = list((changes / "archive").iterdir())
    assert [path.name for path in archived] == ["2026-08-01-date-every-task"]


def test_the_full_root_carries_all_four_delta_operations(full_root: Path) -> None:
    deltas = (full_root / "openspec/changes").rglob("specs/*/spec.md")
    written = "\n".join(path.read_text() for path in deltas)

    for operation in ("ADDED", "MODIFIED", "REMOVED", "RENAMED"):
        assert f"## {operation} Requirements" in written


def test_the_full_root_has_a_checkbox_whose_text_wraps(full_root: Path) -> None:
    tasks = (full_root / "openspec/changes/add-reminders/tasks.md").read_text().splitlines()
    checkbox = next(index for index, line in enumerate(tasks) if line.startswith("- [ ] 1.2"))

    # The lines under it are the same task continued, not tasks of their own.
    assert tasks[checkbox + 1].startswith("      ")
    assert not tasks[checkbox + 1].lstrip().startswith("- [")


def test_the_holed_root_has_tasks_written_and_design_missing(holed_root: Path) -> None:
    change = holed_root / "openspec/changes/rename-the-columns"

    assert (change / "tasks.md").is_file()
    assert not (change / "design.md").exists()


def test_the_empty_root_is_a_root_and_nothing_else(empty_root: Path) -> None:
    assert (empty_root / "openspec/config.yaml").is_file()
    assert [path.name for path in (empty_root / "openspec").iterdir()] == ["config.yaml"]


def test_the_broken_root_is_broken_in_both_ways(broken_root: Path) -> None:
    change = broken_root / "openspec/changes/half-written"

    with pytest.raises(UnicodeDecodeError):
        (change / "proposal.md").read_text()

    assert "1.1" in (change / "tasks.md").read_text()
    assert "\t" in (broken_root / "openspec/config.yaml").read_text()


def test_the_directory_that_is_not_a_root_has_no_openspec(not_a_root: Path) -> None:
    assert not_a_root.is_dir()
    assert not (not_a_root / "openspec").exists()
