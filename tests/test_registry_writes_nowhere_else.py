"""Specdeck writes in one place. This is the test that says so about the registry.

The first hard rule of the product is that a registered repository is never written to. It
is the kind of rule that is true until someone adds a convenience, so it is checked against
a real root on disk rather than trusted.
"""

import hashlib
from pathlib import Path

from specdeck.application.registry import Registry
from specdeck.infrastructure.registry import JsonRegistryStore


def fingerprint(root: Path) -> dict[str, tuple[int, str]]:
    """Every file under a directory, by size and by content. Enough to catch any edit."""
    return {
        str(path.relative_to(root)): (
            path.stat().st_size,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_registering_listing_and_removing_leave_the_root_byte_for_byte(
    tmp_path: Path, full_root: Path
) -> None:
    before = fingerprint(full_root)
    registry = Registry(JsonRegistryStore(tmp_path / "config" / "specdeck" / "repos.json"))

    repo = registry.add(full_root)
    registry.repos()
    registry.remove(repo.id)

    assert fingerprint(full_root) == before


def test_the_only_thing_written_is_the_registry_itself(tmp_path: Path, full_root: Path) -> None:
    configuration = tmp_path / "config" / "specdeck"
    registry = Registry(JsonRegistryStore(configuration / "repos.json"))

    registry.add(full_root)
    registry.repos()

    files = (path for path in tmp_path.rglob("*") if path.is_file())
    written = sorted(path.relative_to(tmp_path) for path in files)

    assert written == [Path("config/specdeck/repos.json")]


def test_the_registry_never_reaches_inside_the_root_to_write(
    tmp_path: Path, full_root: Path
) -> None:
    # The registry is told about a root, and what it keeps is a path. Nothing it writes is
    # anywhere near that path.
    store = JsonRegistryStore(tmp_path / "repos.json")
    Registry(store).add(full_root)

    assert store.path.is_file()
    assert not store.path.is_relative_to(full_root)
    assert not any(path.name.startswith("repos.json") for path in full_root.rglob("*"))
