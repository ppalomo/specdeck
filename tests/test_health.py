"""The server says whether it is alive and who it is."""

from importlib.metadata import version

import pytest
from httpx import ASGITransport, AsyncClient

from specdeck.app import create_app


@pytest.mark.asyncio
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
