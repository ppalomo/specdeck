"""The `specdeck` executable's own commands for the registry."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

import specdeck.infrastructure.registry as registry_module
from specdeck.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def a_registry_of_our_own(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the executable at this test's registry, never at the machine's."""
    ours = tmp_path / "config" / "repos.json"
    monkeypatch.setattr(registry_module, "DEFAULT_PATH", ours)
    return ours


def test_adding_a_repository_reports_what_was_registered(full_root: Path) -> None:
    result = runner.invoke(app, ["add", str(full_root)])

    assert result.exit_code == 0
    assert "full" in result.output
    assert str(full_root) in result.output


def test_what_was_added_is_listed(full_root: Path) -> None:
    runner.invoke(app, ["add", str(full_root)])

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert str(full_root) in result.output
    assert "repo" in result.output


def test_nothing_registered_says_how_to_register_something() -> None:
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "specdeck add" in result.output


def test_adding_a_directory_that_is_not_a_root_fails_naming_the_path(
    not_a_root_dir: Path,
) -> None:
    result = runner.invoke(app, ["add", str(not_a_root_dir)])

    assert result.exit_code == 1
    assert str(not_a_root_dir.resolve()) in result.output
    assert "openspec/config.yaml" in result.output


def test_removing_says_the_repository_was_not_touched(full_root: Path) -> None:
    added = runner.invoke(app, ["add", str(full_root)]).output
    repo_id = added.split(" as ")[1].split(" ")[0]

    result = runner.invoke(app, ["remove", repo_id])

    assert result.exit_code == 0
    assert "not touched" in result.output
    assert runner.invoke(app, ["list"]).output.count(str(full_root)) == 0


def test_removing_what_is_not_registered_fails_saying_so() -> None:
    result = runner.invoke(app, ["remove", "never-added"])

    assert result.exit_code == 1
    assert "never-added" in result.output


def test_a_repository_that_has_gone_is_listed_as_unavailable(tmp_path: Path) -> None:
    root = tmp_path / "on-a-disk"
    (root / "openspec").mkdir(parents=True)
    (root / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    runner.invoke(app, ["add", str(root)])

    (root / "openspec" / "config.yaml").unlink()
    (root / "openspec").rmdir()
    root.rmdir()

    result = runner.invoke(app, ["list"])

    assert "unavailable" in result.output
    assert "no longer exists" in result.output


def test_reading_a_repository_reports_what_is_in_it(full_root: Path) -> None:
    added = runner.invoke(app, ["add", str(full_root)]).output
    repo_id = added.split(" as ")[1].split(" ")[0]

    result = runner.invoke(app, ["read", repo_id])

    assert result.exit_code == 0
    assert "2 active" in result.output
    assert "1 archived" in result.output
    assert "2 capabilities" in result.output


def test_reading_what_is_not_registered_fails_saying_so() -> None:
    result = runner.invoke(app, ["read", "never-added"])

    assert result.exit_code == 1
    assert "never-added" in result.output


def test_the_help_describes_the_commands_that_exist() -> None:
    result = runner.invoke(app, ["--help"])

    for command in ("serve", "openapi", "add", "remove", "list", "read"):
        assert command in result.output
