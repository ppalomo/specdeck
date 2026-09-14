"""What is held in memory: how it gets there, and that asking for it reads nothing."""

import asyncio
import time
from pathlib import Path

import pytest

from conftest import CapturedCli
from specdeck.application.contents import RootContents
from specdeck.application.indexer import Indexer
from specdeck.application.indexes import Indexes
from specdeck.application.ports import CliOutput, Invocation
from specdeck.application.registry import NotRegisteredError, Registry
from specdeck.infrastructure.disk import DiskRootReader
from specdeck.infrastructure.registry import JsonRegistryStore

SLOW = 0.25
"""Long enough to tell a sum from a maximum, short enough not to slow the suite down."""


class CountingReader:
    """A root reader that says how often it was asked to read anything."""

    def __init__(self, inner: DiskRootReader) -> None:
        """Count for the given reader."""
        self.inner = inner
        self.reads = 0

    async def read(self, root: Path) -> RootContents:
        """Read, and remember having been asked."""
        self.reads += 1
        return await self.inner.read(root)


class SlowReader:
    """A root reader that takes its time, as a real one does."""

    async def read(self, root: Path) -> RootContents:  # noqa: ARG002
        """Take as long as reading a root takes, and say nothing much."""
        await asyncio.sleep(SLOW)
        return RootContents(schema_name="spec-driven")


class SlowCli(CapturedCli):
    """A CLI that costs what the real one costs."""

    async def run(self, root: Path, invocation: Invocation) -> CliOutput:
        """Cost what an invocation costs, then answer as the captured one would."""
        await asyncio.sleep(SLOW)
        return await super().run(root, invocation)


@pytest.fixture
def registry(tmp_path: Path) -> Registry:
    return Registry(JsonRegistryStore(tmp_path / "repos.json"))


def a_root(where: Path) -> Path:
    (where / "openspec").mkdir(parents=True)
    (where / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    return where


async def test_every_registered_root_is_read_when_specdeck_starts(
    registry: Registry, full_root: Path, empty_root: Path, captured_cli: CapturedCli
) -> None:
    registry.add(full_root)
    registry.add(empty_root)
    indexes = Indexes(registry, Indexer(DiskRootReader(), captured_cli))

    built = await indexes.build()

    assert [index.repo.name for index in built] == ["full", "empty"]
    assert len(indexes.all()) == 2


async def test_asking_for_what_is_held_reads_nothing_at_all(
    registry: Registry, full_root: Path
) -> None:
    reader, cli = CountingReader(DiskRootReader()), CapturedCli()
    repo = registry.add(full_root)
    indexes = Indexes(registry, Indexer(reader, cli))
    await indexes.build()

    reads_after_building, asked_after_building = reader.reads, len(cli.asked)
    for _ in range(10):
        assert indexes.get(repo.id) is not None
        assert len(indexes.all()) == 1

    assert reader.reads == reads_after_building == 1
    assert len(cli.asked) == asked_after_building


async def test_reading_again_happens_only_when_something_says_to(
    registry: Registry, full_root: Path
) -> None:
    reader = CountingReader(DiskRootReader())
    repo = registry.add(full_root)
    indexes = Indexes(registry, Indexer(reader, CapturedCli()))
    await indexes.build()

    first = indexes.get(repo.id)
    again = await indexes.rebuild(repo.id)

    assert reader.reads == 2
    assert first is not None
    assert again.built_at >= first.built_at
    assert indexes.get(repo.id) is again


async def test_reading_again_what_is_not_registered_says_so(registry: Registry) -> None:
    indexes = Indexes(registry, Indexer(DiskRootReader(), CapturedCli()))

    with pytest.raises(NotRegisteredError, match="never-added"):
        await indexes.rebuild("never-added")


async def test_roots_are_read_together_rather_than_one_after_another(
    registry: Registry, tmp_path: Path
) -> None:
    for name in ("one", "two", "three"):
        registry.add(a_root(tmp_path / name))
    indexes = Indexes(registry, Indexer(SlowReader(), SlowCli()))

    started = time.perf_counter()
    await indexes.build()
    took = time.perf_counter() - started

    # Three roots, each costing a read and four invocations, and none of the fifteen waits
    # on any other: one after another they would be fifteen, together they are one.
    assert len(indexes.all()) == 3
    assert took < 3 * SLOW


async def test_what_is_held_about_a_root_can_be_forgotten(
    registry: Registry, full_root: Path, captured_cli: CapturedCli
) -> None:
    repo = registry.add(full_root)
    indexes = Indexes(registry, Indexer(DiskRootReader(), captured_cli))
    await indexes.build()

    indexes.forget(repo.id)

    assert indexes.get(repo.id) is None
    assert indexes.all() == ()


async def test_a_root_registered_after_the_start_is_simply_not_held_yet(
    registry: Registry, full_root: Path, empty_root: Path, captured_cli: CapturedCli
) -> None:
    registry.add(full_root)
    indexes = Indexes(registry, Indexer(DiskRootReader(), captured_cli))
    await indexes.build()

    late = registry.add(empty_root)

    assert indexes.get(late.id) is None
    assert len(indexes.all()) == 1
