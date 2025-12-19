# Kytchen Runtime Specification v1.0

**Status**: Strategic Blueprint
**Priority**: This is the path to unicorn

---

## The Strategic Pivot

### Before (Tool Thinking)
- Kytchen is a context management tool
- Recipes are config files you share
- Fork = copy a JSON file

### After (Platform Thinking)
- Kytchen is **The Runtime Layer for the Agentic Web**
- Kitchens are **live environments** that agents connect to
- Fork = **full environment** (indexed data + tools + config)
- This is the network effect

---

## Core Concepts (Updated Hierarchy)

```
Chef (user)
  └── Recipe Books (collections, like GitHub repos)
        └── Recipes (workflow definitions, like Dockerfiles)
              └── Kitchens (running environments, like Heroku apps)
                    ├── Pantry (indexed data, ready to query)
                    ├── Menu (available tools, OpenAI-compatible schema)
                    ├── Tickets (active queries)
                    ├── Receipts (logs)
                    └── Sauce (evidence trail)
```

### The Key Distinction

| Concept | What It Is | Analogy |
|---------|------------|---------|
| **Recipe** | Definition of how to set up a Kitchen | Dockerfile |
| **Kitchen** | Running environment with data + tools | Heroku app |
| **Pantry** | Pre-indexed, parsed data ready to query | Database snapshot |
| **Menu** | Available tools in OpenAI function format | API documentation |

---

## The "Menu" API (Priority #1)

### Why This Matters

If Kytchen is where agents live, agents need a standard way to know **what's for dinner**.

The Menu endpoint returns an OpenAI-compatible tool schema, so ANY agent (Cursor, Windsurf, AutoGen, CrewAI, LangChain) can instantly plug in without custom code.

**This is how we become "The Backend for Cursor."**

### Endpoint

```
GET /v1/kitchens/{kitchen_id}/menu
```

### Response Schema

```json
{
  "$schema": "https://kytchen.dev/schemas/menu.v1.json",
  "version": "1.0.0",

  "kitchen": {
    "id": "kyt_abc123",
    "name": "Legal Research Kitchen",
    "description": "Pre-indexed US case law + contract analysis tools",
    "chef": "@mike_the_chef",
    "visibility": "public",
    "forked_from": null,
    "created_at": "2025-12-16T10:00:00Z"
  },

  "pantry": {
    "datasets": [
      {
        "id": "ds_legal_corpus",
        "name": "US Case Law 2020-2024",
        "format": "text",
        "size_bytes": 450000000,
        "size_tokens_estimate": 112500000,
        "indexed": true,
        "content_hash": "sha256:a1b2c3..."
      }
    ],
    "total_size_bytes": 450000000,
    "total_tokens_estimate": 112500000,
    "indexed_at": "2025-12-15T08:00:00Z"
  },

  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_cases",
        "description": "Search US case law by keyword, citation, or legal concept",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Search query (keywords, case citation, or legal concept)"
            },
            "jurisdiction": {
              "type": "string",
              "enum": ["federal", "state", "all"],
              "default": "all"
            },
            "year_range": {
              "type": "array",
              "items": {"type": "integer"},
              "description": "Optional [start_year, end_year] filter"
            },
            "max_results": {
              "type": "integer",
              "default": 10
            }
          },
          "required": ["query"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "analyze_contract",
        "description": "Analyze a contract for risks, obligations, and key terms",
        "parameters": {
          "type": "object",
          "properties": {
            "document_id": {
              "type": "string",
              "description": "ID of the document in the pantry"
            },
            "focus_areas": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Specific areas to focus on (e.g., 'termination', 'liability')"
            }
          },
          "required": ["document_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "peek",
        "description": "Read a specific portion of the context",
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
    }
  ],

  "budget_defaults": {
    "max_tokens": 50000,
    "max_cost_usd": 1.00,
    "max_iterations": 20,
    "timeout_seconds": 120
  },

  "endpoints": {
    "menu": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/menu",
    "query": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/tickets",
    "stream": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/tickets/stream",
    "pantry": "https://api.kytchen.dev/v1/kitchens/kyt_abc123/pantry"
  }
}
```

### Usage by External Agents

```python
# Any agent framework can now use Kytchen
import requests

# 1. Discover what's available
menu = requests.get(
    "https://api.kytchen.dev/v1/kitchens/kyt_abc123/menu",
    headers={"Authorization": "Bearer kyt_sk_..."}
).json()

# 2. Menu["tools"] is OpenAI-compatible - pass directly to your agent
tools = menu["tools"]

# 3. When agent wants to call a tool, fire a ticket
response = requests.post(
    menu["endpoints"]["query"],
    headers={"Authorization": "Bearer kyt_sk_..."},
    json={
        "tool": "search_cases",
        "arguments": {"query": "fair use doctrine", "jurisdiction": "federal"}
    }
)
```

---

## The Fork = Full Environment Mechanism

### What Happens When You Fork

1. **Recipes are copied** to your Recipe Book
2. **Pantry is snapshotted** (copy-on-write reference)
   - You get instant access to pre-indexed data
   - No re-parsing, no re-indexing
   - Original chef's 10 minutes of setup = your 0 seconds
3. **Tool configs are copied**
4. **You can spin up your own Kitchens**

### Why This Is The Network Effect

If @mike_the_chef indexed 500MB of legal documents:
- **His cost**: 10 minutes + $5 compute
- **Your fork**: instant + free (reference the snapshot)
- **His incentive**: Stars, followers, reputation
- **Platform incentive**: More forks = more lock-in

The Pantry is the moat. Pre-indexed data is valuable.

### Pantry Snapshot Storage

```sql
-- Pantry snapshots are immutable, content-addressed
CREATE TABLE pantry_snapshots (
  id UUID PRIMARY KEY,
  content_hash TEXT UNIQUE NOT NULL,  -- SHA256 of all data
  size_bytes BIGINT NOT NULL,
  size_tokens_estimate BIGINT NOT NULL,
  indexed_at TIMESTAMPTZ NOT NULL,
  created_by UUID REFERENCES chefs(id),
  storage_url TEXT NOT NULL,  -- S3/MinIO location

  -- Reference counting for garbage collection
  ref_count INT DEFAULT 1
);

-- Kitchens reference snapshots (CoW)
CREATE TABLE kitchens (
  id UUID PRIMARY KEY,
  chef_id UUID REFERENCES chefs(id),
  recipe_id UUID REFERENCES recipes(id),
  pantry_snapshot_id UUID REFERENCES pantry_snapshots(id),

  -- When you modify the pantry, you get a new snapshot
  -- Original snapshot's ref_count decrements
);
```

---

## The Kitchen API (Full Spec)

### Endpoints

```
# Kitchen Management
GET    /v1/kitchens                      # List my kitchens
POST   /v1/kitchens                      # Create kitchen (from recipe or scratch)
GET    /v1/kitchens/{id}                 # Get kitchen details
DELETE /v1/kitchens/{id}                 # 86 the kitchen

# The Menu (Agent Discovery)
GET    /v1/kitchens/{id}/menu            # OpenAI-compatible tool schema

# The Pantry (Data)
GET    /v1/kitchens/{id}/pantry          # Pantry status and dataset list
POST   /v1/kitchens/{id}/pantry          # Add ingredients to pantry
DELETE /v1/kitchens/{id}/pantry/{ds_id}  # 86 an ingredient

# Tickets (Queries)
POST   /v1/kitchens/{id}/tickets         # Fire a ticket
GET    /v1/kitchens/{id}/tickets/{tid}   # Get ticket status/result
GET    /v1/kitchens/{id}/tickets         # List recent tickets

# Receipts (Logs) & Sauce (Evidence)
GET    /v1/kitchens/{id}/receipts        # Get audit logs
GET    /v1/kitchens/{id}/sauce           # Get evidence bundle

# Streaming
POST   /v1/kitchens/{id}/tickets/stream  # Fire ticket with SSE streaming
```

### Creating a Kitchen

```bash
# From scratch
POST /v1/kitchens
{
  "name": "My Analysis Kitchen",
  "description": "For analyzing quarterly reports"
}

# From a recipe
POST /v1/kitchens
{
  "recipe_id": "rec_abc123",
  "name": "My Legal Kitchen"  # Optional override
}

# Fork from another kitchen (gets their pantry snapshot!)
POST /v1/kitchens
{
  "fork_from": "kyt_xyz789",
  "name": "My Fork of Legal Kitchen"
}
```

---

## Updated Pitch (The Marketing AI's Refinement)

### Landing Page Hero

> **GitHub is where code sleeps. Kytchen is where code cooks.**
>
> We are the **Runtime Layer** for the Agentic Web.

### The Three Bullets

> - **Don't build a sandbox.** `pip install kytchen`
> - **Don't stuff context.** Let Kytchen sieve it.
> - **Don't trust the output.** Check the Sauce.

### The Promise

> **Stop paying $50/query to send raw PDFs to Claude.**
> Send your Agent to Kytchen, and let it cook for pennies.

### The Value Proof (Token Counter)

Show in the dashboard:
```
┌────────────────────────────────────┐
│ TOKENS SAVED THIS MONTH            │
│ ════════════════════════           │
│ 847,293 tokens ($25.42 saved)      │
│                                    │
│ Your subscription: $20/mo          │
│ Net savings: $5.42 ✓               │
└────────────────────────────────────┘
```

---

## Build Order (Ruthless Prioritization)

### Phase 1: The Menu API (Week 1) ★ CRITICAL
**Goal**: Make Kytchen plug-and-play for Cursor/Windsurf

- [ ] Implement `GET /v1/kitchens/{id}/menu`
- [ ] Return OpenAI-compatible tool schema
- [ ] Document for Cursor/Windsurf users
- [ ] Blog post: "Give Your Cursor Agent a Backend"

**Why first**: This is how we get first 100 users.

### Phase 2: Kitchen as First-Class Object (Week 2)
**Goal**: Restructure API around Kitchens

- [ ] Create Kitchen model and endpoints
- [ ] Migrate existing datasets/queries to Kitchen paradigm
- [ ] Kitchen = Pantry + Menu + Tickets

### Phase 3: The Sauce Viewer (Week 3)
**Goal**: Visual demo moment

- [ ] Stream logs in real-time with thermal receipt aesthetic
- [ ] This is the "wow" moment for demos
- [ ] Screenshots for marketing

### Phase 4: Fork = Full Environment (Week 4)
**Goal**: Network effect begins

- [ ] Implement Pantry snapshots (CoW)
- [ ] Fork copies Recipe + Pantry reference
- [ ] Show "forked from @chef_name" attribution

### Phase 5: Recipe Books Go Live (Week 5-6)
**Goal**: Community flywheel

- [ ] Public Recipe Books with Pantry snapshots
- [ ] Star/fork mechanics
- [ ] Discovery page
- [ ] "Most forked" = most valuable

---

## The Cursor/Windsurf Pitch

### Specific Marketing Message

> **"Give Your Cursor Agent a Backend"**
>
> Cursor can write code. But can it understand your whole codebase?
>
> Kytchen is the context layer that makes Cursor actually useful.
>
> 1. Index your repo: `kytchen index ./`
> 2. Connect Cursor: Add your Kitchen URL to MCP
> 3. Ask anything: "How does authentication work in this codebase?"
>
> Cursor + Kytchen = AI that actually understands your code.

### Integration Path

1. User creates a Kitchen
2. Indexes their codebase into the Pantry
3. Gets a Menu URL: `https://api.kytchen.dev/v1/kitchens/kyt_abc/menu`
4. Adds to Cursor's MCP config
5. Cursor can now call Kitchen tools

---

## The CHEF.md Update

The marketing AI didn't see `CHEF.md`. Here's what it already has that aligns:

**Already in CHEF.md**:
- MCP tool usage guide
- Kitchen metaphors (load_context, peek, search, exec_python)
- The "prep station" concept

**Needs to be added**:
- Menu API documentation
- How to connect to Cursor/Windsurf
- Fork mechanism explanation

---

## Files to Create/Modify

### New Files
- `kytchen/api/routes/kitchens.py` - Kitchen CRUD + Menu endpoint
- `kytchen/schemas/menu.py` - Pydantic models for Menu response
- `docs/MENU_API.md` - Developer documentation
- `examples/cursor_integration.md` - How to connect Cursor

### Modify
- `kytchen/api/app.py` - Add kitchen routes
- `CHEF.md` - Add Menu/Kitchen documentation
- `HANDOFF_PROMPT.md` - Update priorities

---

## Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Menu API calls/day | 1,000+ | Adoption by agent frameworks |
| Kitchens created | 500+ | Active users |
| Fork rate | 20%+ | Network effect working |
| Tokens saved/$ spent | >5x | Value prop proven |

---

*Strategic blueprint synthesized from marketing AI feedback + technical reality*
*2025-12-16*
