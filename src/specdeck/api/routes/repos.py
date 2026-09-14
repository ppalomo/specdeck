"""The registered roots: what is registered, registering one, and letting one go."""

from fastapi import APIRouter, HTTPException, status

from specdeck.api.dependencies import Wired, index_of
from specdeck.api.views import RegisteredRepo, Registration
from specdeck.application.registry import NotAnOpenSpecRootError, NotRegisteredError
from specdeck.domain.index import Index

router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.get("")
async def registered(wired: Wired) -> list[RegisteredRepo]:  # noqa: D103
    return [
        RegisteredRepo.of(repo, wired.indexes.get(repo.id)) for repo in wired.registry.repos()
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def register(wired: Wired, registration: Registration) -> RegisteredRepo:  # noqa: D103
    try:
        repo = wired.registry.add(registration.path)
    except NotAnOpenSpecRootError as refused:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(refused)
        ) from refused

    # Read it now, so that what was just registered can be looked at rather than being
    # registered and empty until something else happens.
    return RegisteredRepo.of(repo, await wired.indexes.rebuild(repo.id))


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister(wired: Wired, repo_id: str) -> None:  # noqa: D103
    try:
        wired.registry.remove(repo_id)
    except NotRegisteredError as unknown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(unknown)
        ) from unknown

    wired.indexes.forget(repo_id)


@router.get("/{repo_id}")
async def one(wired: Wired, repo_id: str) -> Index:  # noqa: D103
    return index_of(wired, repo_id)


@router.post("/{repo_id}/reading")
async def read_again(wired: Wired, repo_id: str) -> Index:
    """Read a registered root again.

    Nothing watches the files yet, so this is how what is held catches up with what is on
    disk. It writes nothing anywhere: it re-reads a root and replaces what was known.
    """
    try:
        return await wired.indexes.rebuild(repo_id)
    except NotRegisteredError as unknown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(unknown)
        ) from unknown
