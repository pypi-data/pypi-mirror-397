# Kytchen v1.0 - Launch Viability Handoff

## TL;DR - What Needs to Happen

**Kytchen is 80% done. The backend works, tests pass, but the frontend is showing mock data instead of real API calls. Wire it up and we're launch-ready.**

---

## Project Context

**Kytchen** = "Heroku for AI Agents" - BYOLLM context orchestration platform.

Instead of stuffing context into prompts, Kytchen stores data in a sandboxed REPL (the "Pantry") and lets LLMs explore surgically. Every operation produces a "Receipt" (audit log) with "Sauce" (evidence trail).

**Repo**: https://github.com/Shannon-Labs/Kytchen
**Linear**: https://linear.app/shannonlabs/ (Project: "Kytchen Cloud v1.0")

---

## What's DONE (Don't Redo This)

### Backend (Python/FastAPI) - FULLY WORKING
- [x] Kitchen CRUD: `/v1/kitchens` (list, create, get, update, delete)
- [x] Menu API: `/v1/kitchens/{id}/menu` - OpenAI-compatible tool schema
- [x] Pantry: `/v1/kitchens/{id}/pantry` - dataset management
- [x] Tickets API: `/v1/kitchens/{id}/tickets` - fire queries
- [x] SSE Streaming: `/v1/kitchens/{id}/tickets/stream` - real-time progress
- [x] Kitchen-scoped tickets with proper filtering
- [x] Metrics persistence (tokens, cost, iterations)
- [x] SQLite dev mode for testing
- [x] Cross-database UUID compatibility (PostgreSQL + SQLite)
- [x] **All 19 tests passing**: `pytest tests/test_menu_api.py -v`

### Frontend (Next.js) - UI EXISTS BUT NOT WIRED
- [x] Dashboard layout and pages
- [x] Ticket Rail component (visual tickets)
- [x] Thermal Receipt component (logs)
- [x] "The Line" terminal component (live activity)
- [x] Heat effects, animations, industrial kitchen aesthetic
- [x] Supabase auth integration

### Infrastructure
- [x] Docker for local dev (`Dockerfile`, `docker-compose.yml`) - NOT for distribution
- [x] Supabase linked with migrations
- [x] E2B sandbox integration

**Note**: Kytchen is commercial-only. No self-host/OSS distribution. The moat is the hosted platform.

---

## What's NOT DONE (This Is Your Job)

### 0. Rename "Kitchen" to "Kytchen" Everywhere (CRITICAL - DO THIS FIRST)

**The product is called Kytchen. Having a "Kitchen" API is confusing and bad branding.**

This needs to be renamed:
- API endpoints: `/v1/kitchens` → `/v1/kytchens`
- Database table: `kitchens` → `kytchens`
- Model class: `Kitchen` → `Kytchen`
- All references in code: `kitchen_id` → `kytchen_id`, etc.

**Files to update:**
- `kytchen/api/routes/kitchens.py` → rename to `kytchens.py`
- `kytchen/api/models.py` - rename `Kitchen` class to `Kytchen`
- `kytchen/api/schemas/kitchen.py` → rename to `kytchen.py`
- `kytchen/api/app.py` - update router imports
- `tests/test_menu_api.py` - update endpoint paths
- Database migration needed for table rename

**Search and replace (careful, case-sensitive):**
```
Kitchen → Kytchen (class names)
kitchen → kytchen (variables, endpoints)
kitchens → kytchens (table names, routes)
```

This is not optional. The product name IS the API resource name.

### 1. Wire Frontend to Real API (CRITICAL)

The frontend components exist but display **mock data**. Need to connect to the real Kytchen API.

**File**: `kytchen-web/lib/hooks/use-run-stream.ts`
- Currently returns mock events in a setInterval
- Has commented-out real SSE implementation
- Needs to call: `POST /v1/kitchens/{kitchen_id}/tickets/stream`

**File**: `kytchen-web/app/dashboard/workspaces/[slug]/runs/page.tsx`
- Shows hardcoded mock runs
- Should fetch from: `GET /v1/kitchens/{kitchen_id}/tickets`

**File**: `kytchen-web/packages/client/src/client.ts`
- TypeScript SDK exists but uses OLD endpoints (`/v1/query`)
- Update to use Kitchen endpoints:
  - `POST /v1/kitchens/{kitchen_id}/tickets` (not `/v1/query`)
  - `POST /v1/kitchens/{kitchen_id}/tickets/stream` (not `/v1/query/stream`)
  - `GET /v1/kitchens/{kitchen_id}/menu`
  - `GET /v1/kitchens/{kitchen_id}/pantry`

### 2. Auth Flow for API Calls

Frontend needs to pass API key to backend. Check:
- `kytchen-web/services/supabase-api.ts` - may need Kitchen API integration
- API keys are `kyt_sk_...` format
- Backend expects `Authorization: Bearer kyt_sk_...` header

### 3. Event Shape Mapping

Backend SSE events have this shape:
```typescript
{
  type: "started" | "step" | "completed" | "error",
  data: {
    id: string,
    kitchen_id: string,
    step_number?: number,
    action_type?: string,
    result_preview?: string,
    answer?: string,
    metrics?: { baseline_tokens, tokens_served, iterations, cost_usd }
  },
  timestamp: number
}
```

Frontend `RunEvent` expects:
```typescript
{
  id: string,
  type: "grep" | "read" | "llm" | "db" | "system" | "step",
  message: string,
  timestamp: string,
  duration?: string
}
```

Need a mapper function to transform backend events to frontend format.

### 4. Vercel Deployment (Interactive)

```bash
cd kytchen-web
vercel login    # Interactive - needs human
vercel link     # Interactive - needs human
vercel deploy
```

---

## Key Files Map

```
kytchen/
├── api/
│   ├── app.py              # FastAPI app, middleware, startup
│   ├── routes/kitchens.py  # All Kitchen endpoints (THIS IS THE API)
│   ├── models.py           # SQLAlchemy models
│   ├── state.py            # RunRecord, PostgresStore, MemoryStore
│   └── schemas/            # Pydantic request/response models
├── core.py                 # Kytchen engine (RLM loop)
└── mcp/server.py           # MCP server for Claude/Cursor

kytchen-web/
├── app/dashboard/          # Next.js pages
├── components/
│   ├── runs/
│   │   ├── open-kitchen.tsx    # "The Line" terminal (rename later if you want)
│   │   └── ticket-rail.tsx     # Visual ticket rail
│   └── ui/
│       └── thermal-receipt.tsx # Receipt component
├── lib/hooks/
│   └── use-run-stream.ts   # SSE hook (NEEDS REAL IMPLEMENTATION)
├── packages/client/
│   └── src/client.ts       # TypeScript SDK (NEEDS ENDPOINT UPDATES)
└── services/
    └── supabase-api.ts     # Current data fetching (may need Kitchen API)

tests/
└── test_menu_api.py        # 19 tests - all passing
```

---

## Commands

```bash
# Run backend tests (should all pass)
cd /Volumes/VIXinSSD/kytchen
.venv/bin/python -m pytest tests/test_menu_api.py -v

# Run backend server
KYTCHEN_DEV_MODE=1 .venv/bin/python -m uvicorn kytchen.api.app:app --reload

# Run frontend
cd kytchen-web
npm install && npm run dev

# Test API manually
curl -X POST http://localhost:8000/v1/kitchens \
  -H "Authorization: Bearer kyt_sk_test_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Kitchen"}'
```

---

## API Quick Reference (AFTER RENAME)

All endpoints require `Authorization: Bearer kyt_sk_...` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/kytchens` | List kytchens |
| POST | `/v1/kytchens` | Create kytchen |
| GET | `/v1/kytchens/{id}` | Get kytchen (by ID or slug) |
| PATCH | `/v1/kytchens/{id}` | Update kytchen |
| DELETE | `/v1/kytchens/{id}` | Delete kytchen |
| GET | `/v1/kytchens/{id}/menu` | Get OpenAI tool schema |
| GET | `/v1/kytchens/{id}/pantry` | List datasets |
| POST | `/v1/kytchens/{id}/pantry` | Add dataset |
| POST | `/v1/kytchens/{id}/tickets` | Fire query (sync) |
| POST | `/v1/kytchens/{id}/tickets/stream` | Fire query (SSE) |
| GET | `/v1/kytchens/{id}/tickets` | List tickets |
| GET | `/v1/kytchens/{id}/tickets/{ticket_id}` | Get ticket |

**Note: Current code uses `/v1/kitchens` - rename is task #0**

---

## Definition of Done (Launch Viability)

1. [ ] **"Kitchen" renamed to "Kytchen" throughout** (API, models, DB)
2. [ ] Frontend fetches real data from Kytchen API (not mocks)
3. [ ] SSE streaming works end-to-end (fire ticket -> see live progress)
4. [ ] Can create a Kytchen, add datasets, fire a query, see results
5. [ ] TypeScript SDK matches actual API endpoints
6. [ ] Deployed to Vercel (or at least deployable)

---

## Brand/Terminology Quick Reference

- **Kytchen** = the product AND the API resource (always with Y)
- **Pantry** = dataset storage
- **Ticket** = query/run
- **Receipt** = logs
- **Sauce** = evidence trail
- **The Line** = live activity view
- **Expo Window** = dashboard
- **86** = delete/cancel

---

## What NOT to Do

- Don't rewrite the backend logic - it works, just rename things
- Don't add new features - just wire what exists and fix naming
- Don't spend time on the CLI - focus on web
- Don't overthink it - the rename is mostly find/replace

---

## PART 2: Commercialization & Pricing (NEW - 2025-12-16)

### Strategic Context

We completed strategic research on Kytchen vs GitHub Actions. Full memo at:
`/Users/hunterbown/.claude/plans/glittery-tumbling-harp.md`

**The thesis:** GitHub is infrastructure for humans who code. Kytchen is infrastructure for LLMs that code.

GitHub just announced $0.002/min platform tax on ALL Actions (March 2026). Developers are furious. This is our wedge.

### Pricing Model: "Costco Model"

**No metering. No overages. No per-minute anxiety.**

Pay membership, use the kitchen. Hit your limit? Slow down or upgrade. That's it.

### Final Pricing Tiers

| Tier | Price | Lines | Storage | Rate Limit |
|------|-------|-------|---------|------------|
| **Starter** | Free | 0 (REPL only) | 1 GB | 5 req/min |
| **Chef** | $35/mo | 1 line | 10 GB | 100 req/min |
| **Sous Chef** | $99/mo | 3 lines | 50 GB | 200 req/min |

### What's a "Line"?

A **line** = a persistent E2B sandbox workspace where LLMs cook. Files persist across sessions.

- **Starter:** Built-in REPL only (`kytchen/repl/sandbox.py`). Try the RLM loop. No persistence. No E2B cost.
- **Chef:** 1 persistent line (E2B). Real development environment. Files persist.
- **Sous Chef:** 3 persistent lines. Multi-project support.

### E2B Cost Control

- Starter = no E2B (built-in REPL, zero marginal cost)
- Chef/Sous Chef = E2B for persistent lines, capped by line count
- **Session cap: 2 hours continuous, then auto-pause** (prevents runaway costs)

### Infrastructure Costs (Fits Pro Plans)

| Service | Plan | Cost |
|---------|------|------|
| Supabase | Pro | $25/mo |
| Vercel | Pro | $20/mo |
| E2B | Pro | $150/mo + usage |
| **Total** | | ~$195/mo baseline |

At 100 Chef users ($35/mo): $3,500 MRR, ~86% gross margin.

---

## Linear Issues to Create

Create these in **Shannonlabs** team (ID: `7551927f-d57b-47bf-b4b4-f50070ff3706`):

### MVP - Billing & Limits

1. **Stripe billing integration**
   - 3 tiers: Starter (free), Chef ($35/mo), Sous Chef ($99/mo)
   - Subscription management, upgrade/downgrade
   - Webhook handling for payment events

2. **Storage metering**
   - Track GB per workspace
   - Update `workspace_usage` table on file uploads
   - Display current usage in dashboard

3. **Storage limits enforcement**
   - Pre-flight check before uploads
   - Reject if over quota (402 status)
   - Clear error message: "Storage limit reached. Upgrade to continue."

4. **Rate limiting**
   - Redis/Upstash implementation
   - Tier-based: 5/100/200 req/min
   - Return 429 with retry-after header

5. **Line management (E2B integration)**
   - Create/destroy E2B sandboxes per workspace
   - Enforce line limits: 0/1/3 by tier
   - 2-hour session auto-pause

6. **Landing page with positioning**
   - "GitHub is where humans store code. Kytchen is where LLMs write it."
   - Costco model messaging: "No per-minute anxiety"
   - Pricing table with Starter/Chef/Sous Chef

### Nice-to-Have (v1.1)

- Usage dashboard (storage used, lines active)
- Upgrade prompts when hitting limits
- Annual billing discount ($29/mo for Chef annual)

### Skip Entirely

- Compute metering (Costco model = no metering)
- Teams/seats (later)
- Self-host option (destroys moat)
- SSO/SAML (enterprise later)

---

## The Pitch (One-Liners)

- "GitHub is where humans store code. Kytchen is where LLMs write it."
- "GitHub charges per minute. We stop the build before it breaks."
- "Pay membership, use the kitchen. No games, no tricks."
- "Upgrade to Chef to get your own line."

---

## Key Decisions (Don't Revisit)

| Decision | Answer | Why |
|----------|--------|-----|
| Pricing model | Costco (no metering) | Anti-GitHub, predictable |
| Tiers | Starter/Chef/Sous Chef | Kitchen hierarchy |
| E2B | Chef+ only | Starter uses free built-in REPL |
| Teams | Later | MVP simplicity |
| Self-host | NO | Destroys moat |
| Compute metering | NO | Costco model |
| BYOLLM | Yes | Users bring own API keys |

---

## Files to Update

- `docs/COSTS_AND_LIMITS.md` - new tier names and limits
- `docs/ICP_AND_WEDGE.md` - update pricing section
- `kytchen_brand_bible.md` - add "line" to terminology

---

*Handoff updated 2025-12-16 by Claude Opus 4.5*
*Part 1: Backend done, frontend needs wiring*
*Part 2: Pricing locked, need Stripe + limits + Linear issues*
