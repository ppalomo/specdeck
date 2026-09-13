"""The FastAPI application: the API Specdeck serves and the contract that describes it."""

from importlib.metadata import version
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

PRODUCT_NAME = "Specdeck"
PACKAGE_NAME = "specdeck"


def product_version() -> str:
    """The version of the installed package, so it cannot drift from what is running."""
    return version(PACKAGE_NAME)


class Health(BaseModel):
    """What the server answers when asked whether it is alive and who it is."""

    name: str
    status: Literal["ok"]
    version: str


def create_app() -> FastAPI:
    """Build the application. Everything it answers depends only on this process."""
    app = FastAPI(title=PRODUCT_NAME, version=product_version())

    @app.get("/api/health")
    async def health() -> Health:
        return Health(name=PRODUCT_NAME, status="ok", version=product_version())

    return app


app = create_app()
