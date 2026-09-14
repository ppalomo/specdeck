"""What the routers are given, and where the one real wiring of it lives."""

from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status

from specdeck.application.indexer import Indexer
from specdeck.application.indexes import Indexes
from specdeck.application.registry import Registry
from specdeck.domain.index import Index
from specdeck.infrastructure.disk import DiskRootReader
from specdeck.infrastructure.openspec_cli import OpenSpecProcess
from specdeck.infrastructure.registry import JsonRegistryStore


class Services:
    """Everything the API is built out of, put together once."""

    def __init__(self, registry: Registry, indexes: Indexes) -> None:
        """Serve from the given registry and the roots it holds."""
        self.registry = registry
        self.indexes = indexes

    @classmethod
    def real(cls) -> "Services":
        """Wire Specdeck as it actually runs: the user's registry, the disk, the CLI."""
        registry = Registry(JsonRegistryStore())
        return cls(registry, Indexes(registry, Indexer(DiskRootReader(), OpenSpecProcess())))


def services(request: Request) -> Services:
    """Hand over the services this application was built with."""
    return cast("Services", request.app.state.services)


Wired = Annotated[Services, Depends(services)]


def index_of(wired: Services, repo_id: str) -> Index:
    """Give what is known about a registered root, or say plainly that it is not here.

    "There is no such repository" and "there is one and it holds nothing" are different
    answers, and an empty list that stands for both is the kind of shape an interface
    quietly renders as an empty screen with no explanation on it.
    """
    index = wired.indexes.get(repo_id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No repository {repo_id!r} has been read. Register it first.",
        )
    return index
