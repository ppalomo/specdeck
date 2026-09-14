"""The registry on disk: what it writes, what it reads back, and what a crash leaves."""

import json
from pathlib import Path

import pytest

from specdeck.domain.availability import Availability
from specdeck.domain.repo import Repo
from specdeck.infrastructure.registry import DEFAULT_PATH, JsonRegistryStore


def a_repo(name: str, path: str, kind: str = "repo") -> Repo:
    entry = {"id": f"{name}-abc123", "name": name, "path": path, "kind": kind}
    return Repo.model_validate(entry)


def test_the_default_location_is_the_one_place_specdeck_writes() -> None:
    assert DEFAULT_PATH.parent == Path.home() / ".config" / "specdeck"


def test_an_absent_store_reads_as_nothing_registered(tmp_path: Path) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")

    assert store.load() == ()


def test_what_is_saved_is_what_is_read_back(tmp_path: Path) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")
    repos = (
        a_repo("specdeck", "/Users/someone/specdeck"),
        a_repo("plans", "/Users/someone/plans", "store"),
    )

    store.save(repos)

    assert store.load() == repos


def test_availability_is_worked_out_again_rather_than_written_down(tmp_path: Path) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")
    unreachable = a_repo("gone", "/Volumes/external/gone").model_copy(
        update={"availability": Availability.missing("the disk is not plugged in")}
    )

    store.save([unreachable])
    written = json.loads((tmp_path / "repos.json").read_text())

    assert "availability" not in written["repos"][0]
    # And it comes back available, because what is on the machine right now is not a
    # decision anybody made and is not the registry's to remember.
    assert store.load()[0].availability.available


def test_the_file_says_what_version_of_itself_it_is(tmp_path: Path) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")

    store.save([a_repo("specdeck", "/Users/someone/specdeck")])

    assert json.loads((tmp_path / "repos.json").read_text())["version"] == 1


def test_saving_creates_the_configuration_directory(tmp_path: Path) -> None:
    store = JsonRegistryStore(tmp_path / "config" / "specdeck" / "repos.json")

    store.save([a_repo("specdeck", "/Users/someone/specdeck")])

    assert store.load()[0].name == "specdeck"


def test_a_crash_halfway_through_leaves_the_previous_registry_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")
    store.save([a_repo("specdeck", "/Users/someone/specdeck")])
    before = (tmp_path / "repos.json").read_text()

    def cut_off(self: Path, data: str, encoding: str | None = None) -> int:
        """Write half of it and die, which is what a power cut looks like from here."""
        half = data[: len(data) // 2]
        Path.write_bytes(self, half.encode(encoding or "utf-8"))
        message = "the machine went away"
        raise OSError(message)

    monkeypatch.setattr(Path, "write_text", cut_off)

    with pytest.raises(OSError, match="the machine went away"):
        store.save([a_repo("plans", "/Users/someone/plans")])

    monkeypatch.undo()
    assert (tmp_path / "repos.json").read_text() == before
    assert store.load()[0].name == "specdeck"


def test_a_crash_leaves_no_half_written_file_lying_about(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = JsonRegistryStore(tmp_path / "repos.json")

    def refuse(self: Path, data: str, encoding: str | None = None) -> int:
        Path.write_bytes(self, data.encode(encoding or "utf-8"))
        message = "the machine went away"
        raise OSError(message)

    monkeypatch.setattr(Path, "write_text", refuse)
    with pytest.raises(OSError, match="the machine went away"):
        store.save([a_repo("specdeck", "/Users/someone/specdeck")])
    monkeypatch.undo()

    assert [path.name for path in tmp_path.iterdir()] == []
