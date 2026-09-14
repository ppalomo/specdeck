"""The changes of a registered root, active and archived."""

from fastapi import APIRouter, HTTPException, status

from specdeck.api.dependencies import Wired, index_of
from specdeck.domain.change import Change

router = APIRouter(prefix="/api/repos/{repo_id}/changes", tags=["changes"])


@router.get("")
async def all_of(wired: Wired, repo_id: str) -> list[Change]:
    """Every change of a root, the archived ones after the active ones."""
    index = index_of(wired, repo_id)
    return [*index.changes, *index.archived]


@router.get("/{change_id}")
async def one(wired: Wired, repo_id: str, change_id: str) -> Change:  # noqa: D103
    index = index_of(wired, repo_id)
    found = next(
        (change for change in (*index.changes, *index.archived) if change.id == change_id), None
    )
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{repo_id!r} has no change called {change_id!r}.",
        )
    return found
