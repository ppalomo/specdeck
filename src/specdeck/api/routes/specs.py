"""The capabilities of a registered root, as they are in force today."""

from fastapi import APIRouter, HTTPException, status

from specdeck.api.dependencies import Wired, index_of
from specdeck.domain.spec import Spec

router = APIRouter(prefix="/api/repos/{repo_id}/specs", tags=["specs"])


@router.get("")
async def all_of(wired: Wired, repo_id: str) -> list[Spec]:  # noqa: D103
    return list(index_of(wired, repo_id).specs)


@router.get("/{spec_id:path}")
async def one(wired: Wired, repo_id: str, spec_id: str) -> Spec:
    """One capability's current spec.

    The identifier is a path because a capability may be nested — `identity/user-auth` is
    one capability, not a capability inside another.
    """
    found = next((spec for spec in index_of(wired, repo_id).specs if spec.id == spec_id), None)
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{repo_id!r} has no capability called {spec_id!r}.",
        )
    return found
