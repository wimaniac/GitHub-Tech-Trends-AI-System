import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from api.app import app
from database.db import init_db, clear_all_data
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    await clear_all_data()

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_get_categories(async_client):
    response = await async_client.get("/api/categories")
    assert response.status_code == 200
    assert "categories" in response.json()

@pytest.mark.asyncio
async def test_get_stats(async_client):
    response = await async_client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_repos" in data
    assert "total_trends" in data

@pytest.mark.asyncio
async def test_get_trends_empty(async_client):
    response = await async_client.get("/api/trends")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["trends"] == []
