"""Everything indexed, held in memory, and how it gets there.

Asking what is in a root must not read it. A single invocation of the OpenSpec CLI costs
around half a second whatever the root holds, and half a second does not belong in the path
of a request. So roots are read when Specdeck starts and when somebody says to read them
again, and everything in between is answered from here.

Nothing watches the files yet, so what is held and what is on disk drift apart the moment
anybody edits one. That is what `Index.built_at` is for, and what rereading is for. The
watcher will make the asking unnecessary; it will not change any of this.
"""

import asyncio

from specdeck.application.indexer import Indexer
from specdeck.application.registry import NotRegisteredError, Registry
from specdeck.domain.index import Index


class Indexes:
    """The index of every registered root, kept in memory until something says otherwise."""

    def __init__(self, registry: Registry, indexer: Indexer) -> None:
        """Index the roots the given registry holds."""
        self._registry = registry
        self._indexer = indexer
        self._indexed: dict[str, Index] = {}

    async def build(self) -> tuple[Index, ...]:
        """Read every registered root, all at once.

        Concurrently because the cost of the CLI is per invocation and not per root: three
        roots read together take about as long as the slowest of the three, and one after
        another take the sum.
        """
        repos = self._registry.repos()
        indexes = await asyncio.gather(*(self._indexer.index(repo) for repo in repos))

        self._indexed = {index.repo.id: index for index in indexes}
        return tuple(indexes)

    async def rebuild(self, repo_id: str) -> Index:
        """Read one registered root again, because somebody said to."""
        repo = next((one for one in self._registry.repos() if one.id == repo_id), None)
        if repo is None:
            raise NotRegisteredError(repo_id)

        index = await self._indexer.index(repo)
        self._indexed[repo_id] = index
        return index

    def forget(self, repo_id: str) -> None:
        """Drop what was held about a root, for when it stops being registered."""
        self._indexed.pop(repo_id, None)

    def all(self) -> tuple[Index, ...]:
        """Everything held, in the order the registry holds it. Reads nothing."""
        held = self._indexed
        return tuple(held[repo.id] for repo in self._registry.repos() if repo.id in held)

    def get(self, repo_id: str) -> Index | None:
        """Give what is held about one root, or nothing if it was never read. Reads nothing."""
        return self._indexed.get(repo_id)
