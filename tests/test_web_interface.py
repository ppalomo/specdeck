"""The server serves the compiled interface when it carries it, and runs fine without it."""

from pathlib import Path

from httpx import ASGITransport, AsyncClient

from specdeck.api.app import create_app


async def test_the_api_answers_when_there_is_no_compiled_interface(
    tmp_path: Path,
) -> None:
    transport = ASGITransport(app=create_app(static_dir=tmp_path / "never-built"))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        health = await client.get("/api/health")
        root = await client.get("/")

    assert health.status_code == 200
    assert root.status_code == 404


async def test_the_interface_is_served_without_covering_the_api(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<!doctype html><title>Specdeck</title>")

    transport = ASGITransport(app=create_app(static_dir=tmp_path))
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        root = await client.get("/")
        client_route = await client.get("/repos/specdeck")
        health = await client.get("/api/health")

    assert root.status_code == 200
    assert "<title>Specdeck</title>" in root.text
    assert client_route.text == root.text
    assert health.status_code == 200
    assert health.json()["name"] == "Specdeck"
