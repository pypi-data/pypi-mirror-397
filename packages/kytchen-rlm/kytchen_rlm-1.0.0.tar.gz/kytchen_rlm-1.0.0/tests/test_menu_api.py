"""Tests for Menu API (SHA-107).

Tests the Kitchen CRUD endpoints and Menu API that returns
OpenAI-compatible tool schemas.
"""

from __future__ import annotations

import os

import pytest

# Set dev mode before importing app
os.environ["KYTCHEN_DEV_MODE"] = "1"

from kytchen.api.app import create_app


fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
sqlalchemy = pytest.importorskip("sqlalchemy")


AUTH_HEADERS = {"Authorization": "Bearer kyt_sk_test_key"}


@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    return create_app()


@pytest.fixture
async def client(app):
    """Create an async HTTP client with proper startup/shutdown."""
    import kytchen.api.db as db_module

    # Reset global state for fresh in-memory database per test
    db_module._engine = None
    db_module._AsyncSessionLocal = None

    # Initialize database tables for tests
    await db_module.init_db()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Cleanup - dispose engine to allow fresh DB for next test
    engine = db_module._get_engine()
    if engine:
        await engine.dispose()
    db_module._engine = None
    db_module._AsyncSessionLocal = None


# -----------------------------------------------------------------------------
# Kitchen CRUD Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_kitchens_empty(client) -> None:
    """Initially, kitchen list should be empty."""
    r = await client.get("/v1/kytchens", headers=AUTH_HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "kytchens" in data
    assert isinstance(data["kytchens"], list)
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_create_kitchen(client) -> None:
    """Test creating a new Kitchen."""
    payload = {
        "name": "Test Kitchen",
        "description": "A test kitchen for unit tests",
        "visibility": "private",
    }
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Kitchen"
    assert data["slug"] == "test-kitchen"
    assert data["visibility"] == "private"
    assert data["id"].startswith("kyt_")


@pytest.mark.asyncio
async def test_create_kitchen_with_slug(client) -> None:
    """Test creating a Kitchen with custom slug."""
    payload = {
        "name": "My Special Kitchen",
        "slug": "my-slug",
        "visibility": "public",
    }
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["slug"] == "my-slug"


@pytest.mark.asyncio
async def test_get_kitchen_by_id(client) -> None:
    """Test getting a Kitchen by ID."""
    # Create kitchen first
    payload = {"name": "Get Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get by ID
    r = await client.get(f"/v1/kytchens/{kitchen_id}", headers=AUTH_HEADERS)
    assert r.status_code == 200
    assert r.json()["id"] == kitchen_id


@pytest.mark.asyncio
async def test_get_kitchen_by_slug(client) -> None:
    """Test getting a Kitchen by slug."""
    # Create kitchen first
    payload = {"name": "Slug Test Kitchen", "slug": "slug-test"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201

    # Get by slug
    r = await client.get("/v1/kytchens/slug-test", headers=AUTH_HEADERS)
    assert r.status_code == 200
    assert r.json()["slug"] == "slug-test"


@pytest.mark.asyncio
async def test_update_kitchen(client) -> None:
    """Test updating a Kitchen."""
    # Create kitchen first
    payload = {"name": "Update Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Update
    r = await client.patch(
        f"/v1/kytchens/{kitchen_id}",
        json={"name": "Updated Name", "visibility": "public"},
        headers=AUTH_HEADERS,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Name"
    assert r.json()["visibility"] == "public"


@pytest.mark.asyncio
async def test_delete_kitchen(client) -> None:
    """Test deleting (86ing) a Kitchen."""
    # Create kitchen first
    payload = {"name": "Delete Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Delete
    r = await client.delete(f"/v1/kytchens/{kitchen_id}", headers=AUTH_HEADERS)
    assert r.status_code == 204

    # Verify deleted
    r = await client.get(f"/v1/kytchens/{kitchen_id}", headers=AUTH_HEADERS)
    assert r.status_code == 404


# -----------------------------------------------------------------------------
# Menu API Tests (SHA-107)
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_menu_returns_openai_format(client) -> None:
    """Menu should return OpenAI-compatible tool schema."""
    # Create kitchen first
    payload = {"name": "Menu Test Kitchen", "slug": "menu-test"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    data = r.json()
    assert "version" in data
    assert "kytchen" in data
    assert "pantry" in data
    assert "tools" in data
    assert "endpoints" in data


@pytest.mark.asyncio
async def test_menu_includes_default_tools(client) -> None:
    """Menu should include default tools: peek, search, lines, chunk, exec_python."""
    # Create kitchen first
    payload = {"name": "Tools Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    data = r.json()
    tool_names = [t["function"]["name"] for t in data["tools"]]
    assert "peek" in tool_names
    assert "search" in tool_names
    assert "lines" in tool_names
    assert "chunk" in tool_names
    assert "exec_python" in tool_names


@pytest.mark.asyncio
async def test_menu_tools_have_openai_structure(client) -> None:
    """Each tool should have OpenAI function format."""
    # Create kitchen first
    payload = {"name": "Structure Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    for tool in r.json()["tools"]:
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
        assert tool["function"]["parameters"]["type"] == "object"


@pytest.mark.asyncio
async def test_menu_includes_kitchen_metadata(client) -> None:
    """Menu should include kitchen metadata."""
    # Create kitchen first
    payload = {
        "name": "Metadata Test Kitchen",
        "description": "Test description",
        "visibility": "public",
    }
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    kytchen = r.json()["kytchen"]
    assert kytchen["id"] == kitchen_id
    assert kytchen["name"] == "Metadata Test Kitchen"
    assert kytchen["description"] == "Test description"
    assert kytchen["visibility"] == "public"


@pytest.mark.asyncio
async def test_menu_includes_endpoints(client) -> None:
    """Menu should include API endpoints."""
    # Create kitchen first
    payload = {"name": "Endpoints Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    endpoints = r.json()["endpoints"]
    assert "menu" in endpoints
    assert "query" in endpoints
    assert kitchen_id in endpoints["menu"]


@pytest.mark.asyncio
async def test_menu_includes_budget_defaults(client) -> None:
    """Menu should include budget defaults."""
    # Create kitchen first
    payload = {"name": "Budget Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    budget = r.json()["budget_defaults"]
    assert "max_tokens" in budget
    assert "max_cost_usd" in budget
    assert "max_iterations" in budget
    assert "timeout_seconds" in budget


@pytest.mark.asyncio
async def test_menu_requires_auth(client) -> None:
    """Menu endpoint should require authentication."""
    r = await client.get("/v1/kytchens/some-kitchen/menu")
    assert r.status_code == 401


# -----------------------------------------------------------------------------
# Pantry Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pantry_empty_initially(client) -> None:
    """Pantry should be empty for new Kitchen."""
    # Create kitchen first
    payload = {"name": "Pantry Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get pantry
    r = await client.get(f"/v1/kytchens/{kitchen_id}/pantry", headers=AUTH_HEADERS)
    assert r.status_code == 200

    data = r.json()
    assert data["datasets"] == []
    assert data["total_count"] == 0


# -----------------------------------------------------------------------------
# Tickets Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tickets_requires_pantry(client) -> None:
    """Tickets endpoint should fail if pantry is empty."""
    # Create kitchen
    payload = {"name": "Ticket Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Try to create ticket with empty pantry
    ticket_payload = {"query": "What is in this document?"}
    r = await client.post(
        f"/v1/kytchens/{kitchen_id}/tickets",
        json=ticket_payload,
        headers=AUTH_HEADERS,
    )
    assert r.status_code == 400
    assert "No datasets" in r.json()["detail"]


@pytest.mark.asyncio
async def test_tickets_list_empty(client) -> None:
    """Listing tickets should return empty list for new kitchen."""
    # Create kitchen
    payload = {"name": "List Tickets Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # List tickets
    r = await client.get(f"/v1/kytchens/{kitchen_id}/tickets", headers=AUTH_HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "tickets" in data
    assert "total" in data
    assert isinstance(data["tickets"], list)


@pytest.mark.asyncio
async def test_tickets_not_found(client) -> None:
    """Getting non-existent ticket should return 404."""
    # Create kitchen
    payload = {"name": "Ticket 404 Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Try to get non-existent ticket
    r = await client.get(
        f"/v1/kytchens/{kitchen_id}/tickets/nonexistent-id",
        headers=AUTH_HEADERS,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_tickets_requires_auth(client) -> None:
    """Tickets endpoints should require authentication."""
    r = await client.post(
        "/v1/kytchens/some-kitchen/tickets",
        json={"query": "test"},
    )
    assert r.status_code == 401

    r = await client.get("/v1/kytchens/some-kitchen/tickets")
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_menu_includes_chef_handle(client) -> None:
    """Menu should include chef handle."""
    # Create kitchen first
    payload = {"name": "Chef Test Kitchen"}
    r = await client.post("/v1/kytchens", json=payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Get menu
    r = await client.get(f"/v1/kytchens/{kitchen_id}/menu", headers=AUTH_HEADERS)
    assert r.status_code == 200

    kytchen = r.json()["kytchen"]
    # It should be None currently because default workspace creation in tests doesn't have a user owner
    assert kytchen["chef"] is None

@pytest.mark.asyncio
async def test_menu_chef_handle_logic(client) -> None:
    """Test that chef handle is correctly retrieved from DB."""
    # We need to manually set up the DB state because default auth mocks don't create users

    import kytchen.api.db as db_module
    from kytchen.api.models import User, Member, Workspace, MemberRole, Kytchen, KytchenVisibility
    from sqlalchemy import select
    from uuid import uuid4

    async with db_module.AsyncSessionLocal() as session:
        # 1. Create a workspace
        ws_id = uuid4()
        workspace = Workspace(
            id=ws_id,
            name="Chef Workspace",
            slug="chef-workspace",
            plan="free"
        )
        session.add(workspace)

        # 2. Create a user (the chef)
        user_id = uuid4()
        chef_user = User(
            id=user_id,
            email="chef@example.com",
            name="Chef Gordon",
            replit_id="gordonr"
        )
        session.add(chef_user)

        # 3. Link user as owner
        member = Member(
            workspace_id=ws_id,
            user_id=user_id,
            role=MemberRole.owner
        )
        session.add(member)

        # 4. Create a kitchen in this workspace
        kitchen_id = uuid4()
        kitchen = Kytchen(
            id=kitchen_id,
            workspace_id=ws_id,
            slug="gordons-kitchen",
            name="Gordon's Kitchen",
            visibility=KytchenVisibility.public,
            budget_defaults={},
            custom_tools=[]
        )
        session.add(kitchen)

        await session.commit()

    # Now we query the menu for this kitchen
    # Note: the client fixture uses a fresh DB, so we are modifying the DB that the client uses (assuming same engine)

    # We need to use the client to hit the endpoint.
    # The endpoint requires auth. The auth middleware in dev mode just returns a workspace_id.
    # We can pass any workspace_id in auth, because the kitchen is public.

    # Kitchen ID format expected by API is kyt_<12chars> or slug.
    # uuid str replace - and take first 12 is how `_format_kitchen_id` works.
    kitchen_id_str = f"kyt_{str(kitchen_id).replace('-', '')[:12]}"

    r = await client.get(f"/v1/kytchens/{kitchen_id_str}/menu", headers=AUTH_HEADERS)

    assert r.status_code == 200
    data = r.json()
    assert data["kytchen"]["chef"] == "@gordonr"
