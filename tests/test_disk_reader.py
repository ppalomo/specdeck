"""Reading a root off the disk: what is found, what is skipped, and what is never followed."""

from datetime import date
from pathlib import Path

from specdeck.infrastructure.disk import DiskRootReader


def a_root(where: Path, schema: str = "schema: spec-driven\n") -> Path:
    (where / "openspec").mkdir(parents=True)
    (where / "openspec" / "config.yaml").write_text(schema)
    return where


async def test_a_root_gives_up_its_schema_specs_and_changes(full_root: Path) -> None:
    contents = await DiskRootReader().read(full_root)

    assert contents.schema_name == "spec-driven"
    assert [spec.capability for spec in contents.specs] == ["reports", "task-management"]
    assert [change.id for change in contents.changes] == ["add-reminders", "retire-old-reports"]


async def test_the_archive_is_read_from_disk_because_nothing_lists_it(full_root: Path) -> None:
    # `openspec list --json` reports active changes only, so the archive is known this way
    # or not at all.
    contents = await DiskRootReader().read(full_root)

    assert [change.id for change in contents.archived] == ["2026-08-01-date-every-task"]
    assert contents.archived[0].archived_on == date(2026, 8, 1)
    assert all(change.archived_on is None for change in contents.changes)


async def test_the_archive_is_not_mistaken_for_a_change(full_root: Path) -> None:
    contents = await DiskRootReader().read(full_root)

    assert "archive" not in [change.id for change in contents.changes]


async def test_an_archived_directory_with_no_date_is_kept_anyway(tmp_path: Path) -> None:
    root = a_root(tmp_path / "root")
    (root / "openspec/changes/archive/no-date-here").mkdir(parents=True)
    archived = root / "openspec/changes/archive/no-date-here/tasks.md"
    archived.write_text("## 1. G\n\n- [x] 1.1 A.\n")

    contents = await DiskRootReader().read(root)

    assert [change.id for change in contents.archived] == ["no-date-here"]
    assert contents.archived[0].archived_on is None
    assert contents.archived[0].tasks is not None


async def test_every_file_is_named_relative_to_the_root(full_root: Path) -> None:
    contents = await DiskRootReader().read(full_root)
    change = contents.changes[0]

    assert change.tasks is not None
    assert change.tasks.file == "openspec/changes/add-reminders/tasks.md"
    assert change.deltas[0].file.startswith("openspec/changes/add-reminders/specs/")
    assert not Path(contents.specs[0].file).is_absolute()


async def test_a_link_that_leads_out_of_the_root_is_not_followed(tmp_path: Path) -> None:
    outside = tmp_path / "somewhere-else"
    outside.mkdir()
    (outside / "spec.md").write_text("## Purpose\n\nSecrets from another project.\n")

    root = a_root(tmp_path / "root")
    (root / "openspec/specs").mkdir(parents=True)
    (root / "openspec/specs/borrowed").symlink_to(outside)

    contents = await DiskRootReader().read(root)

    assert contents.specs == ()
    # Not an error either: it was never part of this root, so nothing here failed.
    assert contents.unreadable == ()


async def test_a_capability_nested_a_level_down_is_still_found(tmp_path: Path) -> None:
    root = a_root(tmp_path / "root")
    nested = root / "openspec/specs/identity/user-auth"
    nested.mkdir(parents=True)
    (nested / "spec.md").write_text("## Purpose\n\nQuién es quién.\n")

    contents = await DiskRootReader().read(root)

    assert [spec.capability for spec in contents.specs] == ["identity/user-auth"]


async def test_a_file_that_cannot_be_read_is_named_and_the_rest_still_arrives(
    broken_root: Path,
) -> None:
    contents = await DiskRootReader().read(broken_root)

    # The config is not YAML and the proposal is not text. Both are named, and the tasks
    # beside them are read as if nothing had happened.
    assert contents.schema_name is None
    assert contents.changes[0].tasks is not None
    assert {unread.file for unread in contents.unreadable} == {
        "openspec/config.yaml",
        "openspec/changes/half-written/proposal.md",
    }
    assert contents.changes[0].documents == ()


async def test_a_delta_that_cannot_be_read_is_named(tmp_path: Path) -> None:
    root = a_root(tmp_path / "root")
    delta = root / "openspec/changes/half/specs/board"
    delta.mkdir(parents=True)
    (delta / "spec.md").write_bytes(b"## ADDED Requirements\n\n\xff\xfe roto\n")

    contents = await DiskRootReader().read(root)

    assert contents.changes[0].deltas == ()
    assert [unread.file for unread in contents.unreadable] == [
        "openspec/changes/half/specs/board/spec.md"
    ]
    assert "utf-8" in contents.unreadable[0].reason


async def test_an_empty_root_reads_as_empty_rather_than_as_a_failure(empty_root: Path) -> None:
    contents = await DiskRootReader().read(empty_root)

    assert contents.schema_name == "spec-driven"
    assert (contents.specs, contents.changes, contents.archived) == ((), (), ())
    assert contents.unreadable == ()


async def test_a_directory_that_is_not_a_root_reads_as_nothing(not_a_root_dir: Path) -> None:
    contents = await DiskRootReader().read(not_a_root_dir)

    assert contents.schema_name is None
    assert contents.changes == ()


async def test_a_change_says_when_it_last_changed(full_root: Path) -> None:
    contents = await DiskRootReader().read(full_root)

    assert all(change.last_modified is not None for change in contents.changes)
