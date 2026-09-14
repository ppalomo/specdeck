"""Registering roots by path: what is accepted, what is refused, and what is never touched."""

from pathlib import Path

import pytest

from specdeck.application.registry import NotAnOpenSpecRootError, NotRegisteredError, Registry
from specdeck.infrastructure.registry import JsonRegistryStore


@pytest.fixture
def registry(tmp_path: Path) -> Registry:
    """A registry whose store is this test's own, never the machine's."""
    return Registry(JsonRegistryStore(tmp_path / "config" / "repos.json"))


def a_root(where: Path, *, store: bool = False) -> Path:
    """The smallest thing that counts as a root: a config, and a marker if it is a store."""
    (where / "openspec").mkdir(parents=True)
    (where / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    if store:
        (where / ".openspec-store").mkdir()
        (where / ".openspec-store" / "store.yaml").write_text("id: plans\n")
    return where


def test_a_root_is_registered_by_its_path(registry: Registry, full_root: Path) -> None:
    repo = registry.add(full_root)

    assert repo.name == "full"
    assert repo.path == full_root.resolve()
    assert repo.kind == "repo"
    assert registry.repos() == (repo,)


def test_the_identifier_is_readable_and_survives_a_restart(
    registry: Registry, full_root: Path
) -> None:
    first = registry.add(full_root)
    registry.remove(first.id)

    assert first.id.startswith("full-")
    assert registry.add(full_root).id == first.id


def test_two_roots_of_the_same_name_do_not_collide(registry: Registry, tmp_path: Path) -> None:
    one = registry.add(a_root(tmp_path / "one" / "web"))
    other = registry.add(a_root(tmp_path / "other" / "web"))

    assert one.name == other.name == "web"
    assert one.id != other.id


def test_a_path_that_is_not_a_root_is_refused_saying_what_was_looked_for(
    registry: Registry, not_a_root_dir: Path
) -> None:
    with pytest.raises(NotAnOpenSpecRootError) as refused:
        registry.add(not_a_root_dir)

    assert str(not_a_root_dir.resolve()) in str(refused.value)
    assert "openspec/config.yaml" in str(refused.value)
    assert registry.repos() == ()


def test_the_same_root_reached_another_way_is_the_root_it_already_is(
    registry: Registry, tmp_path: Path, full_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = registry.add(full_root)

    through_a_link = tmp_path / "link-to-full"
    through_a_link.symlink_to(full_root)
    monkeypatch.chdir(full_root.parent)

    assert registry.add(through_a_link) == first
    assert registry.add(Path("full")) == first
    assert registry.add(full_root / "openspec" / "..") == first
    assert len(registry.repos()) == 1


def test_a_store_is_recognised_as_one_and_read_like_any_other(
    registry: Registry, tmp_path: Path
) -> None:
    repo = registry.add(a_root(tmp_path / "plans", store=True))

    assert repo.kind == "store"
    assert repo.availability.available


def test_a_root_with_no_store_marker_is_a_repository(
    registry: Registry, tmp_path: Path
) -> None:
    assert registry.add(a_root(tmp_path / "code")).kind == "repo"


def test_removing_takes_the_entry_and_leaves_the_root_alone(
    registry: Registry, tmp_path: Path
) -> None:
    root = a_root(tmp_path / "code")
    before = sorted(path.name for path in root.rglob("*"))
    repo = registry.add(root)

    removed = registry.remove(repo.id)

    assert removed.id == repo.id
    assert registry.repos() == ()
    assert sorted(path.name for path in root.rglob("*")) == before


def test_removing_one_leaves_the_others(registry: Registry, tmp_path: Path) -> None:
    stays = registry.add(a_root(tmp_path / "stays"))
    goes = registry.add(a_root(tmp_path / "goes"))

    registry.remove(goes.id)

    assert [repo.id for repo in registry.repos()] == [stays.id]


def test_removing_what_is_not_registered_says_so(registry: Registry) -> None:
    with pytest.raises(NotRegisteredError, match="never-added"):
        registry.remove("never-added")


def test_a_root_that_has_gone_is_still_listed_and_says_why(
    registry: Registry, tmp_path: Path
) -> None:
    root = a_root(tmp_path / "on-a-disk")
    registry.add(root)

    (root / "openspec" / "config.yaml").unlink()
    (root / "openspec").rmdir()
    root.rmdir()

    listed = registry.repos()

    assert len(listed) == 1
    assert not listed[0].availability.available
    assert listed[0].availability.reason == "the path no longer exists"


def test_a_root_that_stopped_being_one_says_that_instead(
    registry: Registry, tmp_path: Path
) -> None:
    root = a_root(tmp_path / "was-a-root")
    registry.add(root)

    (root / "openspec" / "config.yaml").unlink()

    reason = registry.repos()[0].availability.reason
    assert reason is not None
    assert "openspec/config.yaml" in reason


def test_one_root_being_gone_does_not_hide_the_others(
    registry: Registry, tmp_path: Path, full_root: Path
) -> None:
    gone = a_root(tmp_path / "gone")
    registry.add(gone)
    registry.add(full_root)

    (gone / "openspec" / "config.yaml").unlink()

    listed = registry.repos()

    assert [repo.availability.available for repo in listed] == [False, True]
    assert listed[1].name == "full"
