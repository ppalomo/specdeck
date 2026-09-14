"""The API over the index: changes, one change, capabilities, and what is simply not there."""

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
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    registry = Registry(JsonRegistryStore(tmp_path / "repos.json"))
    wired = Services(registry, Indexes(registry, Indexer(DiskRootReader(), CapturedCli())))
    app = create_app(static_dir=Path("/no-interface-here"), services=wired)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as opened,
    ):
        yield opened


async def registered(client: AsyncClient, root: Path) -> str:
    return str((await client.post("/api/repos", json={"path": str(root)})).json()["id"])


async def test_the_changes_of_a_root_are_the_active_ones_then_the_archive(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    changes = (await client.get(f"/api/repos/{repo_id}/changes")).json()

    assert [change["id"] for change in changes] == [
        "add-reminders",
        "retire-old-reports",
        "2026-08-01-date-every-task",
    ]
    assert changes[2]["status"] == "archived"
    assert changes[2]["archived_on"] == "2026-08-01"


async def test_a_change_arrives_with_its_pipeline_tasks_and_deltas(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    change = (await client.get(f"/api/repos/{repo_id}/changes/retire-old-reports")).json()

    assert {one["id"]: one["status"] for one in change["artifacts"]} == {
        "proposal": "done",
        "specs": "done",
        "design": "ready",
        "tasks": "done",
    }
    assert (change["tasks"]["done"], change["tasks"]["total"]) == (2, 3)
    assert [delta["operation"] for delta in change["deltas"]] == [
        "MODIFIED",
        "REMOVED",
        "RENAMED",
    ]
    assert change["validation"]["valid"] is True


async def test_every_task_arrives_with_the_line_it_is_written_on(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    change = (await client.get(f"/api/repos/{repo_id}/changes/add-reminders")).json()
    task = change["tasks"]["groups"][0]["tasks"][1]

    assert task["location"] == {
        "file": "openspec/changes/add-reminders/tasks.md",
        "line": 5,
    }


async def test_the_capabilities_of_a_root_arrive_with_their_requirements(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    specs = (await client.get(f"/api/repos/{repo_id}/specs")).json()
    one = (await client.get(f"/api/repos/{repo_id}/specs/task-management")).json()

    assert {spec["id"]: spec["requirement_count"] for spec in specs} == {
        "reports": 1,
        "task-management": 2,
    }
    assert one["purpose"].startswith("Qué puede hacer alguien")
    assert len(one["requirements"][0]["scenarios"]) == 2


async def test_a_root_with_nothing_in_it_answers_emptily_and_says_so(
    client: AsyncClient, empty_root: Path
) -> None:
    repo_id = await registered(client, empty_root)

    changes = await client.get(f"/api/repos/{repo_id}/changes")
    specs = await client.get(f"/api/repos/{repo_id}/specs")

    # Empty, and successfully so: distinguishable from a repository that is not there.
    assert (changes.status_code, changes.json()) == (200, [])
    assert (specs.status_code, specs.json()) == (200, [])


async def test_a_repository_that_is_not_registered_is_not_an_empty_list(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/repos/never-added/changes")

    assert response.status_code == 404
    assert "never-added" in response.json()["detail"]


async def test_a_change_that_does_not_exist_says_what_was_looked_for(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    response = await client.get(f"/api/repos/{repo_id}/changes/never-proposed")

    assert response.status_code == 404
    assert "never-proposed" in response.json()["detail"]
    assert repo_id in response.json()["detail"]


async def test_a_capability_that_does_not_exist_says_what_was_looked_for(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    response = await client.get(f"/api/repos/{repo_id}/specs/never-written")

    assert response.status_code == 404
    assert "never-written" in response.json()["detail"]


async def test_a_nested_capability_is_asked_for_by_its_whole_path(
    client: AsyncClient, tmp_path: Path
) -> None:
    root = tmp_path / "nested"
    nested = root / "openspec" / "specs" / "identity" / "user-auth"
    nested.mkdir(parents=True)
    (root / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    (nested / "spec.md").write_text("## Purpose\n\nQuién es quién y cómo se comprueba.\n")
    repo_id = await registered(client, root)

    response = await client.get(f"/api/repos/{repo_id}/specs/identity/user-auth")

    assert response.status_code == 200
    assert response.json()["id"] == "identity/user-auth"


async def test_the_index_of_a_root_says_when_it_was_read(
    client: AsyncClient, full_root: Path
) -> None:
    repo_id = await registered(client, full_root)

    index = (await client.get(f"/api/repos/{repo_id}")).json()

    assert index["built_at"] is not None
    assert index["schema_name"] == "spec-driven"
    assert index["canonical"]["available"] is True
    assert index["unreadable"] == []
