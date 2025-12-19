from __future__ import annotations

import pytest

from kytchen.api.app import create_app


fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
sqlalchemy = pytest.importorskip("sqlalchemy")


@pytest.mark.asyncio
async def test_healthz_ok() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_requires_bearer_key() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/v1/query", json={"query": "hi"})
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_rate_limit_429() -> None:
    app = create_app()
    headers = {"Authorization": "Bearer kyt_sk_test_key"}
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # free plan is 5 req/min in middleware
        for _ in range(5):
            r = await client.get("/healthz", headers=headers)
            assert r.status_code == 200
        r = await client.get("/healthz", headers=headers)
        assert r.status_code == 429
