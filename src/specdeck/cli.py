"""The `specdeck` executable: how the server is started and what it can tell about itself."""

import json
import socket
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from uvicorn.supervisors import ChangeReload

from specdeck.app import create_app, product_version

HOST = "127.0.0.1"
PORT = 4820

# The import string uvicorn needs to build the application again after a reload, and
# the directory whose changes are worth reloading for.
APP = "specdeck.app:app"
SOURCE = Path(__file__).parent

app = typer.Typer(
    help="Specdeck — a local dashboard over the OpenSpec directories of several repositories.",
    no_args_is_help=True,
    add_completion=False,
)


def _show_version(value: bool) -> None:  # noqa: FBT001  (Typer hands the flag positionally)
    if value:
        typer.echo(product_version())
        raise typer.Exit


@app.callback()
def main(
    _version: Annotated[  # noqa: FBT002  (a flag is a boolean option with a default)
        bool,
        typer.Option(
            "--version",
            callback=_show_version,
            is_eager=True,
            help="Show the installed version and exit.",
        ),
    ] = False,
) -> None:
    """Specdeck reads the OpenSpec directories of your repositories and shows them."""


def _listening_socket(host: str, port: int) -> socket.socket:
    """Take the port before uvicorn does, so a conflict is reported in our own words."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
    except OSError as error:
        sock.close()
        typer.echo(
            f"Port {port} on {host} is already taken by another process ({error.strerror}). "
            f"Specdeck does not listen on a different port: free {port} and start it again.",
            err=True,
        )
        raise typer.Exit(code=1) from error
    sock.listen()
    return sock


@app.command()
def serve(
    *,
    reload: Annotated[
        bool,
        typer.Option(
            "--reload",
            help="Restart the server when its own code changes. For development.",
        ),
    ] = False,
) -> None:
    """Start the server on the local loopback."""
    sock = _listening_socket(HOST, PORT)
    typer.echo(f"Specdeck is listening on http://{HOST}:{PORT}")

    if reload:
        # Reloading means building the application again in a fresh process, so uvicorn is
        # given the import string rather than the object. The port stays ours: the socket
        # bound above is what the reloaded processes inherit.
        config = uvicorn.Config(
            app=APP, host=HOST, port=PORT, reload=True, reload_dirs=[str(SOURCE)]
        )
        ChangeReload(config, target=uvicorn.Server(config).run, sockets=[sock]).run()
        return

    server = uvicorn.Server(uvicorn.Config(app=create_app(), host=HOST, port=PORT))
    server.run(sockets=[sock])


@app.command()
def openapi() -> None:
    """Write the OpenAPI document to standard output, without listening anywhere."""
    typer.echo(json.dumps(create_app().openapi(), indent=2, sort_keys=True))
