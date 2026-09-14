"""The `specdeck` executable starts the server and publishes its contract."""

import json
import socket
from importlib.metadata import version

import typer
import typer.core
from typer.testing import CliRunner

from specdeck.cli import HOST, PORT, app

runner = CliRunner()


def test_version_reports_the_installed_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == version("specdeck")


def test_openapi_writes_the_contract_without_listening() -> None:
    result = runner.invoke(app, ["openapi"])

    assert result.exit_code == 0
    document = json.loads(result.stdout)
    assert "/api/health" in document["paths"]


def test_serve_fails_naming_the_port_when_it_is_taken() -> None:
    taken = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    taken.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    taken.bind((HOST, PORT))
    taken.listen()
    try:
        result = runner.invoke(app, ["serve"])
    finally:
        taken.close()

    assert result.exit_code == 1
    assert str(PORT) in result.output
    assert "different port" in result.output


def test_serve_offers_a_reload_flag_for_development() -> None:
    # Asked of the command itself rather than of its help text, which rich colours when it
    # believes it is on a terminal, splitting the flag across escape codes. Typer carries
    # its own click, so the group is Typer's, not the one click installs.
    command = typer.main.get_command(app)
    assert isinstance(command, typer.core.TyperGroup)

    flags = [flag for parameter in command.commands["serve"].params for flag in parameter.opts]

    assert "--reload" in flags
