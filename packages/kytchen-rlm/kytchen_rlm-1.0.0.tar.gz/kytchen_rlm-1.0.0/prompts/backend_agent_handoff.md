# Kytchen Backend Implementation - Agent Handoff

## Your Mission

You are implementing the **Menu API**, **Kitchen** abstractions, and **streaming endpoints** for Kytchen - "The Heroku for AI Agents."

**Priorities**:
1. Menu API (SHA-107) - OpenAI-compatible tool discovery
2. Streaming `/v1/query/stream` - SSE for realtime progress
3. Full `QueryResult` from `/v1/query` - answer, evidence, metrics

## Deployment Architecture

```
app.kytchen.dev  → Vercel (Next.js frontend)
api.kytchen.dev  → Railway/Render/Fly (FastAPI Python)
```

The Python backend deploys to Railway (not Vercel). Vercel is for the Next.js frontend only.

---

## Project Context

**Kytchen** is a BYOLLM context orchestration platform. Instead of stuffing context into prompts, we store data in a sandboxed REPL and let agents explore surgically.

**The Pitch**: "GitHub is where code sleeps. Kytchen is where code cooks."

**Repo**: `/Volumes/VIXinSSD/kytchen`
**Linear**: https://linear.app/shannonlabs/ (Project: "Kytchen Cloud v1.0")

---

## Key Files to Read First

```
docs/KITCHEN_RUNTIME_SPEC.md    # Full technical spec for Kitchen/Menu API
schemas/menu.v1.schema.json     # OpenAI-compatible Menu schema
kytchen/api/app.py              # Existing FastAPI backend
kytchen/recipe.py               # Recipe/Kytchenfile implementation
kytchen/core.py                 # Core orchestration loop
CHEF.md                         # Usage guide for agents (how to cook)
```

---

## The Core Abstraction

```
Kitchen = Running Environment (like a Heroku app)
├── Pantry (indexed data, ready to query)
├── Menu (available tools, OpenAI-compatible schema)
├── Tickets (active queries)
├── Receipts (logs)
└── Sauce (evidence trail)

Recipe = Definition (like a Dockerfile)
```

---

## Task 1: Menu API (SHA-107) ★ CRITICAL

### The Endpoint

```
GET /v1/kitchens/{kitchen_id}/menu
```

Returns OpenAI-compatible tool schema so ANY agent (Cursor, Windsurf, AutoGen, CrewAI) can plug in without custom code.

### Response Format

See `schemas/menu.v1.schema.json` for full schema. Key structure:

```json
{
  "version": "1.0.0",
  "kitchen": {
    "id": "kyt_abc123",
    "name": "Legal Research Kitchen",
    "chef": "@mike",
    "visibility": "public"
  },
  "pantry": {
    "datasets": [...],
    "total_tokens_estimate": 112500000
  },
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search",
        "description": "Regex search across pantry data",
        "parameters": {
          "type": "object",
          "properties": {
            "pattern": {"type": "string"},
            "max_results": {"type": "integer", "default": 10}
          },
          "required": ["pattern"]
        }
      }
    }
  ],
  "endpoints": {
    "menu": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/menu",
    "query": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/tickets"
  }
}
```

### Implementation Steps

1. Create `kytchen/api/routes/kitchens.py`
2. Create Pydantic models in `kytchen/api/schemas/menu.py`:
   - `KitchenMeta`
   - `PantryStatus`
   - `ToolDefinition` (OpenAI function format)
   - `MenuResponse`
3. Implement `GET /v1/kitchens/{id}/menu`
4. Return default tools (peek, search, exec_python) + any custom tools
5. Include pantry metadata (datasets, sizes, token estimates)
6. Add to main app in `kytchen/api/app.py`
7. Write test in `tests/test_menu_api.py`

### Default Tools to Include

These are always available in every Kitchen:

```python
DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "peek",
            "description": "Read a specific portion of the context by line numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "description": "Start line (0-indexed)"},
                    "end": {"type": "integer", "description": "End line"}
                },
                "required": ["start", "end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Regex search across all pantry data",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "max_results": {"type": "integer", "default": 10}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lines",
            "description": "Get specific line range from context",
            "parameters": {
                "type": "object",
                "properties": {
                    "start": {"type": "integer"},
                    "end": {"type": "integer"}
                },
                "required": ["start", "end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chunk",
            "description": "Split context into chunks for processing",
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_size": {"type": "integer", "default": 2000},
                    "overlap": {"type": "integer", "default": 200}
                }
            }
        }
    }
]
```

---

## Task 2: Kitchen CRUD (SHA-108)

### Endpoints

```
GET    /v1/kitchens                      # List my kitchens
POST   /v1/kitchens                      # Create kitchen
GET    /v1/kitchens/{id}                 # Get kitchen details
DELETE /v1/kitchens/{id}                 # 86 the kitchen

GET    /v1/kitchens/{id}/menu            # Tool schema (Task 1)
GET    /v1/kitchens/{id}/pantry          # Pantry status
POST   /v1/kitchens/{id}/pantry          # Add ingredients
POST   /v1/kitchens/{id}/tickets         # Fire a ticket (query)
GET    /v1/kitchens/{id}/tickets/{tid}   # Get ticket result
```

### Database Model

For now, use the existing Supabase setup. Add a `kitchens` table:

```sql
CREATE TABLE kitchens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  chef_id UUID REFERENCES auth.users(id),
  visibility TEXT DEFAULT 'private',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(chef_id, slug)
);

CREATE TABLE kitchen_datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kitchen_id UUID REFERENCES kitchens(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  format TEXT DEFAULT 'text',
  size_bytes BIGINT,
  size_tokens_estimate BIGINT,
  content_hash TEXT,
  storage_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Task 3: Integrate with Existing Code

The existing codebase has:

- `kytchen/api/app.py` - FastAPI app with `/v1/datasets`, `/v1/query` routes
- `kytchen/core.py` - The `Kytchen` class that runs the orchestration loop
- `kytchen/repl/` - Sandbox execution (helpers like peek, search, lines)

You need to:

1. **Map existing `/v1/datasets` to Pantry concept**
2. **Map existing `/v1/query` to Tickets concept**
3. **Add Kitchen as the container for both**

The existing code works - don't break it. Add the Kitchen abstraction on top.

---

## Environment Setup

```bash
cd /Volumes/VIXinSSD/kytchen

# Install dependencies
pip install -e '.[api,mcp]'

# Run tests
python -m pytest tests/ -v

# Run API server
uvicorn kytchen.api.app:app --reload --port 8000

# Environment variables (already in .env)
# ANTHROPIC_API_KEY, SUPABASE_URL, etc.
```

---

## Testing

Create `tests/test_menu_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from kytchen.api.app import app

client = TestClient(app)

def test_menu_returns_openai_format():
    """Menu should return OpenAI-compatible tool schema."""
    # Create a kitchen first (or use fixture)
    response = client.get("/v1/kitchens/test-kitchen/menu")
    assert response.status_code == 200

    data = response.json()
    assert "tools" in data
    assert "pantry" in data
    assert "endpoints" in data

    # Verify OpenAI format
    for tool in data["tools"]:
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "parameters" in tool["function"]

def test_menu_includes_default_tools():
    """Menu should include peek, search, lines, chunk."""
    response = client.get("/v1/kitchens/test-kitchen/menu")
    data = response.json()

    tool_names = [t["function"]["name"] for t in data["tools"]]
    assert "peek" in tool_names
    assert "search" in tool_names
```

---

## Success Criteria

1. **Menu API works**: `GET /v1/kitchens/{id}/menu` returns valid OpenAI tool schema
2. **Any agent can connect**: Schema is compatible with Cursor, Windsurf, AutoGen
3. **Tests pass**: All existing tests + new menu tests
4. **Documented**: Add usage example to `docs/MENU_API.md`

---

## What NOT to Do

- Don't refactor existing code unnecessarily
- Don't change the core orchestration loop
- Don't add auth complexity yet (use existing patterns)
- Don't over-engineer - get Menu API working first

---

## Linear Issues

- **SHA-107**: Menu API - OpenAI-Compatible Tool Discovery (URGENT)
- **SHA-108**: Kitchen as First-Class Object (HIGH)
- **SHA-109**: Fork = Full Environment (HIGH, depends on SHA-108)

Start with SHA-107. Mark as "In Progress" when you begin.

---

## Quick Reference

| Concept | Kytchen Term |
|---------|--------------|
| Running environment | Kitchen |
| Indexed data | Pantry |
| Tool schema | Menu |
| Active query | Ticket |
| Logs | Receipt |
| Evidence | Sauce |
| Delete | 86 |

---

*Handoff prepared 2025-12-16*
