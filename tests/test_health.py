"""What the server answers: its health, and the contract that describes its API."""

from importlib.metadata import version

from httpx import ASGITransport, AsyncClient

from specdeck.app import create_app


async def test_health_reports_the_product_and_the_installed_version() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Specdeck",
        "status": "ok",
        "version": version("specdeck"),
    }


async def test_the_openapi_document_is_served() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/health" in response.json()["paths"]
