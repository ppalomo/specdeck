"""The FastAPI application: the API Specdeck serves and the contract that describes it."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from specdeck.api.routes import health
from specdeck.domain.product import PRODUCT_NAME, product_version

# Where `make build` leaves the compiled web interface, so a built package carries it.
# `parents[1]` is the package root: the interface ships inside the package, one level up
# from this layer.
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def create_app(static_dir: Path | None = None) -> FastAPI:
    """Build the application. Everything it answers depends only on this process."""
    app = FastAPI(title=PRODUCT_NAME, version=product_version())
    app.include_router(health.router)

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
