"""Whether the server is alive, and which Specdeck it is."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from specdeck.domain.product import PRODUCT_NAME, product_version

router = APIRouter(prefix="/api")


class Health(BaseModel):
    """What the server answers when asked whether it is alive and who it is."""

    name: str
    status: Literal["ok"]
    version: str


# Deliberately undocumented: FastAPI publishes an endpoint's docstring as its description
# in the contract, and what this endpoint is for is already said by the module and by the
# model it answers with. What the contract carries is decided here, not by a comment.
@router.get("/health")
async def health() -> Health:  # noqa: D103
    return Health(name=PRODUCT_NAME, status="ok", version=product_version())
