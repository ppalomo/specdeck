"""The FastAPI application: the API Specdeck serves and the contract that describes it."""

from importlib.metadata import version
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

PRODUCT_NAME = "Specdeck"
PACKAGE_NAME = "specdeck"

# Where `make build` leaves the compiled web interface, so a built package carries it.
STATIC_DIR = Path(__file__).parent / "static"


def product_version() -> str:
    """The version of the installed package, so it cannot drift from what is running."""
    return version(PACKAGE_NAME)


class Health(BaseModel):
    """What the server answers when asked whether it is alive and who it is."""

    name: str
    status: Literal["ok"]
    version: str


def create_app(static_dir: Path | None = None) -> FastAPI:
    """Build the application. Everything it answers depends only on this process."""
    app = FastAPI(title=PRODUCT_NAME, version=product_version())

    @app.get("/api/health")
    async def health() -> Health:
        return Health(name=PRODUCT_NAME, status="ok", version=product_version())

    directory = STATIC_DIR if static_dir is None else static_dir
    if directory.is_dir():
        _serve_web_interface(app, directory)

    return app


def _serve_web_interface(app: FastAPI, directory: Path) -> None:
    """Serve the compiled interface at the root, falling back to its entry document.

    The fallback is what makes the client's own routing survive a reload. It is registered
    after the API, which keeps it from swallowing an endpoint, and it never leaves the
    directory it was given.
    """
    root = directory.resolve()
    index = root / "index.html"

    @app.get("/{requested:path}", include_in_schema=False)
    async def web_interface(requested: str) -> FileResponse:
        candidate = (root / requested).resolve()
        if requested and candidate.is_file() and candidate.is_relative_to(root):
            return FileResponse(candidate)
        return FileResponse(index)


app = create_app()
