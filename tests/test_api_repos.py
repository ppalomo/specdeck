"""The API over the registry: registering a root, listing what is registered, letting go."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from conftest import CapturedCli
from specdeck.api.app import create_app
from specdeck.api.dependencies import Services
from specdeck.application.indexer import Indexer
from specdeck.application.indexes import Indexes
from specdeck.application.registry import Registry
from specdeck.infrastructure.disk import DiskRootReader
from specdeck.infrastructure.registry import JsonRegistryStore


@pytest.fixture
def wired(tmp_path: Path) -> Services:
    """A Specdeck whose registry is this test's own and whose CLI is the captured one."""
    registry = Registry(JsonRegistryStore(tmp_path / "repos.json"))
    return Services(registry, Indexes(registry, Indexer(DiskRootReader(), CapturedCli())))


@pytest.fixture
async def client(wired: Services) -> AsyncIterator[AsyncClient]:
    """A client over an application that has started, so its roots have been read."""
    app = create_app(static_dir=Path("/no-interface-here"), services=wired)
    transport = ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=transport, base_url="http://testserver") as opened,
    ):
        yield opened


async def test_nothing_registered_is_an_empty_list(client: AsyncClient) -> None:
    response = await client.get("/api/repos")

    assert response.status_code == 200
    assert response.json() == []


async def test_a_root_is_registered_by_its_path(client: AsyncClient, full_root: Path) -> None:
    response = await client.post("/api/repos", json={"path": str(full_root)})

    assert response.status_code == 201
    registered = response.json()
    assert registered["name"] == "full"
    assert registered["kind"] == "repo"
    assert registered["availability"] == {"available": True, "reason": None}
    # Read on registration, so what was just registered can be looked at.
    assert registered["built_at"] is not None
    assert registered["canonical"]["available"]


async def test_what_is_registered_is_listed(client: AsyncClient, full_root: Path) -> None:
    await client.post("/api/repos", json={"path": str(full_root)})

    listed = (await client.get("/api/repos")).json()

    assert [repo["name"] for repo in listed] == ["full"]
    assert listed[0]["built_at"] is not None


async def test_a_path_that_is_not_a_root_is_refused_saying_what_was_looked_for(
    client: AsyncClient, not_a_root_dir: Path
) -> None:
    response = await client.post("/api/repos", json={"path": str(not_a_root_dir)})

    assert response.status_code == 422
    assert "openspec/config.yaml" in response.json()["detail"]
    assert (await client.get("/api/repos")).json() == []


async def test_a_root_is_let_go_of(client: AsyncClient, full_root: Path) -> None:
    registered = (await client.post("/api/repos", json={"path": str(full_root)})).json()

    response = await client.delete(f"/api/repos/{registered['id']}")

    assert response.status_code == 204
    assert (await client.get("/api/repos")).json() == []
    assert (await client.get(f"/api/repos/{registered['id']}")).status_code == 404


async def test_letting_go_of_what_is_not_registered_says_so(client: AsyncClient) -> None:
    response = await client.delete("/api/repos/never-added")

    assert response.status_code == 404
    assert "never-added" in response.json()["detail"]


async def test_a_root_can_be_read_again_on_request(
    client: AsyncClient, full_root: Path
) -> None:
    registered = (await client.post("/api/repos", json={"path": str(full_root)})).json()

    response = await client.post(f"/api/repos/{registered['id']}/reading")

    assert response.status_code == 200
    assert response.json()["built_at"] >= registered["built_at"]


async def test_reading_again_what_is_not_registered_says_so(client: AsyncClient) -> None:
    assert (await client.post("/api/repos/never-added/reading")).status_code == 404


async def test_a_registered_root_that_has_gone_is_answered_with_its_reason(
    client: AsyncClient, tmp_path: Path
) -> None:
    root = tmp_path / "on-a-disk"
    (root / "openspec").mkdir(parents=True)
    (root / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    await client.post("/api/repos", json={"path": str(root)})

    (root / "openspec" / "config.yaml").unlink()
    (root / "openspec").rmdir()
    root.rmdir()

    listed = (await client.get("/api/repos")).json()

    assert len(listed) == 1
    assert listed[0]["availability"] == {
        "available": False,
        "reason": "the path no longer exists",
    }
