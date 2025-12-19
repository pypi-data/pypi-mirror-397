# HANDOFF: Launch Kytchen - Specific Agent Instructions

**Date:** 2025-12-17
**Status:** Pre-launch - NOT a real product yet
**Goal:** Unified product across MCP/CLI/API that matches Render/Vercel/Supabase elegance

---

## COMPLETED THIS SESSION

### Git Tools Added to MCP Server
- `git_status`, `git_diff`, `git_log`, `git_blame`, `git_show`, `git_branch`
- File: `kytchen/mcp/local_server.py` (now 3210 lines, 44 tools)
- **MCP server needs restart to use new tools**

### Master Chef Aesthetic (Gemini completed)
- **Typography**: Playfair Display (serif) added to `layout.tsx` and `globals.css`
- **Font stack**: Playfair (headers) + Oswald (headings) + Inter (body)
- **No Emojis**: Unicode cleaned - em-dashes to hyphens, bullets to pipes, arrows to Lucide icons
- **Design System**: High-contrast "Sharpie" borders, Lucide icons only, no unicode

---

## AGENT ROUTING TABLE

Use this table to decide which agent to spawn:

| Task Type | Agent | Model | When to Use |
|-----------|-------|-------|-------------|
| Linear issues, project audit, bulk updates | `linear-project-manager` | Opus | Any Linear MCP operations |
| Strategic decisions, feature prioritization | `kytchen-master` | Opus | "Should we build X?" questions |
| File renaming, import updates, restructuring | `repo-organizer` | Haiku | SHA-111 Kitchen->Kytchen rename |
| UI components, styling, UX polish | `frontend-specialist` | Opus | New components, design quality |
| General implementation tasks | `general-executor` | inherit | Everything else |

### When to Use Jules CLI (NOT an agent)

**Jules = Google's coding agent for menial frontend tasks**

Use Jules for:
- Writing unit tests for components
- Fixing ESLint/TypeScript errors
- Adding comments/documentation
- Simple CSS tweaks
- Repetitive file updates

```bash
# Example Jules commands
jules new "write tests for the ThermalReceipt component"
jules new "fix all TypeScript errors in kytchen-web/app"
jules new "add JSDoc comments to all exported functions in components/ui"
jules new --repo shannonlabs/kytchen "update all Button components to use the new variant prop"
```

**DO NOT use Jules for:**
- Strategic decisions (use `kytchen-master`)
- Complex multi-file refactors (use `repo-organizer`)
- New feature design (use `frontend-specialist`)

---

## CRITICAL PATH TO LAUNCH

### Phase 1: Unify the Product (DO FIRST)

#### Task 1.1: Rename Kitchen to Kytchen (SHA-111)
**Agent:** `repo-organizer`
**Priority:** URGENT
**Prompt:**
```
Rename all instances of "Kitchen" to "Kytchen" throughout the codebase:
1. kytchen/api/routes/kitchens.py -> kytchens.py (delete duplicate)
2. kytchen/api/schemas/kitchen.py -> kytchen.py
3. Database table: kitchens -> kytchens
4. All class names: Kitchen -> Kytchen
5. All variable names: kitchen_id -> kytchen_id
6. Update all imports after renames
Search with: grep -r "kitchen" --include="*.py" kytchen/
```

#### Task 1.2: Add Git Tools to CLI
**Agent:** `general-executor`
**Files:** `kytchen/cli/git.py` (create), `kytchen/cli/main.py` (update)
**Prompt:**
```
Add git commands to the Kytchen CLI that mirror the MCP git tools:
- kytchen git status
- kytchen git diff [target]
- kytchen git log [--limit N] [--oneline]
- kytchen git blame <file>
- kytchen git show [ref]
- kytchen git branch [--all]

Use the same subprocess execution pattern from mcp/local_server.py lines 537-573.
Register the git command group in cli/main.py.
```

#### Task 1.3: Add Git Endpoints to API
**Agent:** `general-executor`
**Files:** `kytchen/api/routes/git.py` (create), `kytchen/api/app.py` (update)
**Prompt:**
```
Add git endpoints to the REST API:
- GET /v1/kytchens/:id/git/status
- GET /v1/kytchens/:id/git/diff?target=HEAD~1
- GET /v1/kytchens/:id/git/log?limit=10
- GET /v1/kytchens/:id/git/blame?path=file.py
- GET /v1/kytchens/:id/git/show?ref=HEAD
- GET /v1/kytchens/:id/git/branch

These operate within the context of a Kitchen's workspace.
```

### Phase 2: Wire E2B Sandboxes ("Lines")

#### Task 2.1: Connect E2B to API (SHA-117)
**Agent:** `general-executor`
**Files:** `kytchen/sandbox/e2b.py` (exists), `kytchen/api/routes/lines.py` (create)
**Prompt:**
```
Wire the existing E2B integration to the API:
1. Read kytchen/sandbox/e2b.py - E2B code already exists
2. Read kytchen/sandbox/__init__.py - Selection logic exists
3. Create API endpoints:
   - POST /v1/kytchens/:id/lines (create sandbox)
   - GET /v1/kytchens/:id/lines (list sandboxes)
   - POST /v1/kytchens/:id/lines/:line_id/exec (execute in sandbox)
   - DELETE /v1/kytchens/:id/lines/:line_id (destroy sandbox)
4. Enforce tier limits: Starter=0, Chef=1, Sous Chef=3
```

### Phase 3: Complete Billing (SHA-113)

#### Task 3.1: Audit Stripe Integration
**Agent:** `linear-project-manager`
**Prompt:**
```
Audit SHA-113 (Stripe billing integration) status:
1. List all requirements from the issue
2. Check which webhook handlers exist in kytchen/api/routes/billing.py
3. Identify what's missing
4. Update the Linear issue with current status
```

#### Task 3.2: Implement Missing Billing
**Agent:** `general-executor`
**Files:** `kytchen/api/routes/billing.py`, `kytchen/api/limits.py`
**Based on Linear issue SHA-113 audit results**

### Phase 4: Frontend Polish

#### Task 4.1: Landing Page (SHA-118)
**Agent:** `frontend-specialist`
**Prompt:**
```
Implement the landing page at kytchen-web/app/page.tsx:
- Hero: "GitHub charges per minute. We charge per storage."
- Pricing table: Starter (Free), Chef ($35), Sous Chef ($99)
- Master Chef aesthetic: Playfair Display headers, no emojis, Lucide icons
- High-contrast "Sharpie" borders
- Industrial kitchen vibe
```

#### Task 4.2: Menial Frontend Tasks
**Use:** `jules` CLI (not an agent)
```bash
jules new "ensure all components in kytchen-web use Lucide icons, not emojis"
jules new "add loading skeletons to all dashboard pages"
jules new "fix any accessibility issues in the auth forms"
```

---

## DOGFOODING CHECKLIST

**You MUST use Kytchen MCP tools during development:**

```python
# After MCP restart, use these tools:
mcp__kytchen__git_status()  # Instead of git status in bash
mcp__kytchen__git_log(limit=5, oneline=True)  # Instead of git log
mcp__kytchen__git_diff(target="HEAD~1")  # Instead of git diff

# For code exploration:
mcp__kytchen__load_context(context="<file contents>")
mcp__kytchen__search_context(pattern="class Kitchen")
mcp__kytchen__exec_python(code="len(ctx)")

# Report any bugs found in these tools!
```

---

## FILE REFERENCE

### Python Backend
```
kytchen/
├── mcp/local_server.py    # MCP server (44 tools) - PRIMARY SURFACE
├── cli/main.py            # CLI entry point
├── cli/query.py           # kytchen query/run
├── api/routes/
│   ├── kytchens.py        # Kitchen API (RENAME THIS)
│   ├── kitchens.py        # DELETE after rename
│   ├── billing.py         # Stripe webhooks
│   └── keys.py            # API keys
├── sandbox/e2b.py         # E2B integration (EXISTS, NOT WIRED)
└── core.py                # RLM engine
```

### Frontend (Next.js)
```
kytchen-web/
├── app/
│   ├── layout.tsx         # Playfair Display configured
│   ├── globals.css        # font-serif variable
│   ├── page.tsx           # Landing page (needs work)
│   └── dashboard/         # Dashboard pages
└── components/
    └── ui/                # shadcn components
```

---

## LINEAR ISSUES PRIORITY

Run this to see current status:
```
Use linear-project-manager agent:
"Audit all Shannonlabs issues. Show: In Progress, then URGENT backlog, grouped by priority."
```

### URGENT - Must Complete for Launch
| Issue | Title | Agent |
|-------|-------|-------|
| SHA-111 | Kitchen -> Kytchen rename | `repo-organizer` |
| SHA-113 | Stripe billing completion | `general-executor` |
| SHA-117 | E2B Lines integration | `general-executor` |
| SHA-118 | Landing page | `frontend-specialist` |
| SHA-119 | E2B Session Management API | `general-executor` |
| SHA-120 | JWT/OAuth authentication | `general-executor` |
| SHA-121 | Evidence/Sauce API endpoints | `general-executor` |
| SHA-122 | Workspace & Member Management | `general-executor` |
| SHA-123 | Logout endpoint & auth flow | `general-executor` |
| SHA-124 | .env.example & Stripe webhook | `general-executor` |

### HIGH Priority
| Issue | Title | Agent |
|-------|-------|-------|
| SHA-125 | RLS policies | `general-executor` |
| SHA-126 | Usage tracking endpoints | `general-executor` |
| SHA-127 | Audit log endpoints | `general-executor` |
| SHA-128 | RBAC middleware | `general-executor` |
| SHA-129 | GitHub OAuth | `general-executor` |
| SHA-130 | Zod API validation | `general-executor` |
| SHA-131 | Subscription enforcement | `general-executor` |

### MEDIUM Priority
| Issue | Title | Agent |
|-------|-------|-------|
| SHA-132 | API key management UI | `frontend-specialist` |
| SHA-110 | Industrial Kitchen UI effects | `frontend-specialist` |
| SHA-102 | Python/TypeScript SDKs | `general-executor` |

---

## SUCCESS CRITERIA

The product is "real" when:

| Capability | Current | Target |
|------------|---------|--------|
| Unified naming | Kitchen/Kytchen mixed | Kytchen everywhere |
| Git in MCP | 6 tools | 6 tools |
| Git in CLI | 0 commands | 6 commands |
| Git in API | 0 endpoints | 6 endpoints |
| E2B sandboxes | Code exists, not wired | API endpoints working |
| Stripe billing | Partial | All webhooks handled |
| Landing page | "Prep Station" | Full marketing page |
| Dashboard | In progress | Functional CRUD |

---

## AGENT INVOCATION EXAMPLES

### Starting a work session
```
"Use linear-project-manager to audit Shannonlabs project status and identify blockers."
```

### Strategic question
```
"Use kytchen-master to evaluate: Should we prioritize E2B integration or SDK release?"
```

### Bulk rename
```
"Use repo-organizer to rename all Kitchen references to Kytchen across the Python codebase."
```

### UI work
```
"Use frontend-specialist to implement the pricing cards on the landing page with Master Chef aesthetic."
```

### General implementation
```
"Use general-executor to add git commands to the CLI."
```

### Menial frontend
```bash
jules new "write tests for ThermalReceipt component"
jules new "fix TypeScript errors in kytchen-web"
```

---

## THE MAGIC WORDS

To actually launch this product, the next Claude must:

1. **START** by using `linear-project-manager` to audit current state
2. **IMMEDIATELY** use `repo-organizer` for SHA-111 (Kitchen->Kytchen)
3. **USE** `general-executor` to unify git tools across CLI and API
4. **USE** `general-executor` to wire E2B to API
5. **USE** `frontend-specialist` for landing page
6. **DELEGATE** menial frontend to Jules CLI
7. **DOGFOOD** by using `mcp__kytchen__git_*` tools for all git operations
8. **TRACK** progress by updating Linear issues via `linear-project-manager`

**DO NOT:**
- Use Bash for git operations (use Kytchen MCP tools instead)
- Do strategic thinking without `kytchen-master`
- Do bulk renames without `repo-organizer`
- Do UI work without `frontend-specialist`
- Do menial frontend without Jules

The product launches when all three surfaces (MCP/CLI/API) have unified capabilities.
