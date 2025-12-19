# Kytchen - Full Context for Marketing/Branding AI

## Your Role
You're helping position and market **Kytchen**, an infrastructure product for the AI agent era. Think of this as helping position Heroku in 2008 or Stripe in 2011 - we're at the infrastructure layer, not the application layer.

---

## The 30-Second Pitch

> **"We're the Heroku for AI Agents."**
>
> Before Heroku, developers wasted 50% of their time managing servers.
> Before Kytchen, developers waste 50% of their time managing context.
>
> Heroku said: "Don't think about servers. Just write code."
> Kytchen says: **"Don't think about context. Just write prompts."**
>
> GitHub is where code sleeps. **Kytchen is where agents live.**

---

## What Kytchen Actually Does (Technical)

### The Problem
When you give an LLM a task that requires reading documents, code, or data:

1. **Context stuffing fails**: You can't fit 100 files into a prompt
2. **RAG is lossy**: Chunking loses structure, retrieval misses things
3. **Long context hallucinates**: 1M token models get "lost in the middle"
4. **No audit trail**: You can't prove what the AI actually read
5. **Token costs explode**: Re-sending context every turn burns money

### The Solution
Kytchen stores your data in a **sandboxed Python REPL** (we call it the "Pantry"). The LLM doesn't see the full data - it sees metadata and uses code to explore:

```python
# LLM writes this code, Kytchen executes it
results = search("authentication", max_results=10)  # grep-like
chunk = peek(500, 1000)  # read specific lines
data = ctx["users.json"]  # access loaded data
```

**Result**:
- 10-50x token savings (we track baseline vs actual)
- Cryptographic evidence of what was read ("sauce")
- Reproducible analysis (same recipe = same dish)
- Budget controls (stop before you burn $100)

### The Magic Command
```bash
kytchen run recipe.json --ingredients ./docs/
```

You give us a recipe (what to analyze) and ingredients (data). We provision the sandbox, parse documents, manage memory, run the analysis, and return results with evidence.

---

## Current Technical Stack

### Backend (Python)
```
kytchen/
├── api/app.py           # FastAPI backend (runs on port 8000)
│   ├── /v1/datasets     # Upload ingredients to pantry
│   ├── /v1/query        # Fire a ticket (run analysis)
│   ├── /v1/runs/{id}    # Get results + sauce
│   └── /v1/tool/{name}  # Direct tool access
│
├── mcp/server.py        # MCP server for IDE integration
│   └── Tools: load_context, peek, search, exec_python
│
├── sandbox/             # Code execution abstraction
│   ├── local.py         # Local Python sandbox
│   └── e2b.py           # E2B cloud sandboxes (isolated VMs)
│
├── recipe.py            # Kytchenfile spec (reproducible workflows)
├── core.py              # Main orchestration loop
└── converters/          # PDF, DOCX, XLSX → text
```

### Frontend (Next.js 14)
```
kytchen-web/
├── app/
│   ├── dashboard/       # Main dashboard
│   │   ├── page.tsx     # Overview
│   │   ├── savings/     # Token savings analytics
│   │   └── activity/    # Realtime query progress
│   └── (auth)/          # Login/signup
│
├── components/
│   ├── savings/
│   │   ├── token-arbitrage.tsx   # Efficiency metrics
│   │   └── savings-chart.tsx     # Visual savings over time
│   ├── activity/
│   │   └── open-kitchen.tsx      # Realtime SSE progress
│   └── thermal-receipt.tsx       # Audit log visualization
│
└── packages/client/     # TypeScript SDK
    └── src/client.ts    # KytchenClient with streaming
```

### Infrastructure
- **Database**: Supabase (PostgreSQL) - auth, storage, realtime
- **Sandboxes**: E2B for cloud execution, local for dev
- **Storage**: MinIO (S3-compatible) for self-host, Supabase Storage for cloud
- **Self-host**: Docker Compose (postgres + minio + kytchen-api)

### What's Built vs Planned

| Component | Status | Notes |
|-----------|--------|-------|
| Core orchestration loop | ✅ Done | `kytchen/core.py` |
| Sandbox execution | ✅ Done | Local + E2B |
| MCP server (IDE integration) | ✅ Done | Works in Claude, Cursor, VSCode |
| FastAPI backend | ✅ Done | All routes functional |
| Docker self-host | ✅ Done | `docker-compose.yml` |
| Token savings dashboard | ✅ Done | `app/dashboard/savings/` |
| Realtime progress | ✅ Done | SSE streaming |
| TypeScript SDK | ✅ Done | `@kytchen/client` |
| Python SDK | 🔄 Planned | For backend integrations |
| Recipe Books (social) | 🔄 Planned | GitHub-like sharing |
| Leaderboards | 🔄 Planned | Efficiency competition |

---

## The Bigger Vision (Beyond Compliance)

### Who This Is For

**NOT just compliance teams.** That's a wedge, not the whole market.

Kytchen is for **any developer building with AI agents**:

1. **AI-native apps**: Cursor, Windsurf, Devin, etc. - they all need context management
2. **Code review/refactoring**: Analyze entire codebases, not just snippets
3. **Documentation generation**: Read code → produce docs with citations
4. **Test generation**: Understand codebase → generate meaningful tests
5. **Migration assistance**: "Convert this Express app to FastAPI" across 100 files
6. **Bug hunting**: "Find security vulnerabilities" with evidence
7. **Onboarding**: New devs ask questions, get answers with file references

### The CI/CD Evolution

You mentioned "life beyond CI/CD." Here's the vision:

**Old world (CI/CD)**:
1. Developer writes code
2. Push to GitHub
3. CI runs tests
4. CD deploys if green
5. Hope nothing breaks

**New world (Agent-assisted)**:
1. Developer describes intent
2. Agent analyzes codebase (via Kytchen)
3. Agent writes code with full context
4. Agent verifies against requirements
5. Agent produces evidence trail
6. Human reviews evidence, approves
7. Deploy with confidence

**Kytchen's role**: We're the "context layer" that makes step 2-5 possible at scale. Without us, agents can only see what fits in a prompt. With us, agents can surgically explore any codebase.

### The Market Expansion

```
         Compliance           Developer Tools           AI Infrastructure
         (Wedge)              (Expansion)               (Endgame)
         ─────────────────────────────────────────────────────────────────►

Year 1:  SOC2 Gap Analysis    Code Review Agents
         Audit Evidence       Documentation Gen
         $50K ACV            Refactoring Assist

Year 2:                       Test Generation           MCP Standard
                              Migration Agents          Agent Memory Layer
                              Onboarding Bots           Multi-Agent Orchestration
                              $5K-50K ACV

Year 3:                                                 "Every AI agent
                                                         runs on Kytchen"
                                                         Platform fees
```

---

## Brand Identity: "Industrial Kitchen Chic"

### Core Aesthetic
- **Vibe**: Deterministic. Auditable. "Grep first. Generate second."
- **Visuals**: Reduction pipelines, thermal receipts, ticket rails
- **Feel**: Professional kitchen - efficient, observable, no waste

### Kitchen Metaphor (Consistent Terminology)

| Concept | Kytchen Term | Why It Works |
|---------|--------------|--------------|
| Input data | **Ingredients** | Raw materials |
| Storage | **Pantry** | Where ingredients live |
| Sandbox | **Prep Station** | Where work happens |
| Workflow | **Recipe** | Reproducible instructions |
| Output | **Dish** | Plated result |
| Evidence | **Sauce** | "Where's the sauce?" = show your sources |
| User | **Chef** | Creator/operator |
| Collection | **Recipe Book** | GitHub repo equivalent |
| Copy | **Fork** | Take and modify |
| Favorite | **Star** | Mark as good |
| Delete | **86** | Kitchen slang for "out of" |
| Logs | **Receipts** | Thermal printer aesthetic |
| Query | **Ticket** | Order being worked |

### Key Hooks

**For CTOs/Architects**:
- "Grep first. Generate second."
- "Your LLM reads metadata. Not your monorepo."
- "Malpractice insurance for your AI."

**For Developers**:
- "Stop stuffing prompts. Prep context. Ship answers."
- "Infinite pantry. 500-token plate."
- "See the prep work. Trust the dish."

**For the Market**:
- "The Heroku for AI Agents."
- "GitHub is where code sleeps. Kytchen is where agents live."

---

## What We Need From You (Marketing AI)

1. **Expand the positioning** beyond compliance - how do we talk to the broader developer market?

2. **Refine the messaging** - the Heroku analogy is strong, but what else resonates?

3. **Landing page structure** - what's the hero, what are the sections, what's the CTA?

4. **Developer marketing strategy** - content, community, evangelism

5. **Competitive positioning** - how do we differentiate from:
   - RAG platforms (Pinecone, Weaviate)
   - AI coding tools (Cursor, Copilot)
   - Agent frameworks (LangChain, CrewAI)
   - Context management (MemGPT, Zep)

6. **Pricing narrative** - we're BYOLLM (bring your own LLM), so we charge for orchestration, not tokens. How do we explain this?

7. **"Recipe Books" feature positioning** - this is our GitHub moment. How do we make sharing recipes feel valuable?

---

## Files to Reference

- `kytchen_brand_bible.md` - Full brand guidelines
- `docs/ICP_AND_WEDGE.md` - Current ICP and market wedge
- `prompts/recipe_books_feature.md` - Recipe Books spec
- `kytchen/recipe.py` - Technical recipe/Kytchenfile implementation
- `CHEF.md` - User-facing usage guide (how to cook with Kytchen)

---

## Quick Hits

- **Domain**: kytchen.dev (or similar)
- **Tagline**: "The Heroku for AI Agents"
- **Company**: Shannon Labs
- **Stage**: Pre-seed, building in public
- **Target**: Developers building AI-native applications

---

*Context prepared by Claude Opus 4.5 - 2025-12-16*
