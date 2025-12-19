# HANDOFF: Kytchen v1.0 Launch - Next Claude Session

**Date:** 2025-12-17
**Status:** Pre-launch - 1-2 weeks from v1.0
**Goal:** Ship credible v1.0 with SDK, docs, and billing enforcement

---

## COMPLETED THIS SESSION

### Surface Unification (DONE)
- Git tools: MCP (6) + CLI (6) + API (6) = 18 total
- SHA-111: Kitchen->Kytchen rename complete
- SHA-113: Tier limits created (limits.py)
- SHA-117: E2B Lines API endpoints (lines.py)
- SHA-118: Landing page production-ready

### Linear Issues Closed
- SHA-111, SHA-113, SHA-117, SHA-118 all marked Done

### New Linear Issues Created (P0 Launch Blockers)
| Issue | Title | Priority |
|-------|-------|----------|
| SHA-133 | Publish kytchen-sdk to PyPI | Urgent |
| SHA-134 | Generate OpenAPI docs from FastAPI | Urgent |
| SHA-135 | Create quickstart.md getting started guide | Urgent |
| SHA-136 | Test E2B sandbox lifecycle in production | Urgent |
| SHA-137 | Integrate Sentry for error tracking | Urgent |
| SHA-138 | Test Stripe billing webhooks end-to-end | Urgent |
| SHA-139 | Enforce tier limits on API requests | Urgent |

---

## AGENT ROUTING TABLE (Updated)

| Task Type | Agent | When to Use |
|-----------|-------|-------------|
| Linear issues, audits | `linear-project-manager` | All Linear MCP operations |
| Strategic decisions | `kytchen-master` | "Should we build X?" questions |
| File renaming, restructuring | `repo-organizer` | Bulk refactors |
| UI components, styling | `frontend-specialist` | New components, design |
| General implementation | `general-executor` | Everything else |

### Jules CLI (for menial tasks)
```bash
jules new "write tests for X"
jules new "fix TypeScript errors in Y"
jules new "add JSDoc comments to Z"
```

---

## JULES VERIFICATION SESSIONS (ALREADY RUNNING)

These sessions were launched to verify this session's work. Check status and pull results:

```bash
# Check which sessions are done
jules remote list --session | grep Shannon-Labs/Kytchen

# Pull results from a completed session
jules remote pull --session <SESSION_ID>

# Or teleport to apply changes directly
jules teleport <SESSION_ID>
```

### Sessions to Check

| Session ID | Verifying | URL |
|------------|-----------|-----|
| 14195565275314613612 | SHA-111: Kitchen->Kytchen rename | [View](https://jules.google.com/session/14195565275314613612) |
| 7738937854612235293 | SHA-113: Stripe/Tier limits | [View](https://jules.google.com/session/7738937854612235293) |
| 18328645047547173906 | SHA-117: E2B Lines API | [View](https://jules.google.com/session/18328645047547173906) |
| 10362386763630500801 | Git tools unification | [View](https://jules.google.com/session/10362386763630500801) |
| 11212036129706054048 | Frontend unicode cleanup | [View](https://jules.google.com/session/11212036129706054048) |

### What to Do with Results

1. **If session completed successfully**: Jules found no issues, verification passed
2. **If session has a patch**: Run `jules teleport <ID>` to apply fixes Jules made
3. **If session failed**: Review the error and fix manually

### Quick Check Command
```bash
# See status of all 5 verification sessions
for id in 14195565275314613612 7738937854612235293 18328645047547173906 10362386763630500801 11212036129706054048; do
  echo "Session $id:"
  jules remote pull --session $id 2>/dev/null | head -5
  echo "---"
done
```

---

## CRITICAL PATH TO V1.0 LAUNCH

### Week 1 Priority Order (P0 - Launch Blockers)

#### Day 1-2: SDK Publishing (SHA-133)
**Agent:** `general-executor`
```
Publish the Python SDK to PyPI:
1. Review kytchen-sdk/ directory structure
2. Update pyproject.toml with correct metadata
3. Create GitHub Action for PyPI publishing
4. Test with TestPyPI first
5. Publish to real PyPI as kytchen-sdk v0.1.0
6. Verify: pip install kytchen-sdk && python -c "import kytchen"
```

#### Day 2-3: OpenAPI Docs (SHA-134)
**Agent:** `general-executor`
```
Enable OpenAPI documentation:
1. Check FastAPI /docs and /redoc endpoints are enabled
2. Export openapi.json to docs/
3. Set up docs hosting (GitHub Pages or Vercel)
4. Add version info to OpenAPI spec
```

#### Day 3-4: Quickstart Guide (SHA-135)
**Agent:** `general-executor`
```
Create docs/quickstart.md:
1. Installation: pip install kytchen-sdk
2. First query example (5 lines of code)
3. MCP setup for Claude Desktop
4. Link to full API reference
```

#### Day 4-5: E2B Testing (SHA-136)
**Agent:** `general-executor`
```
Test E2B sandbox lifecycle end-to-end:
1. Set E2B_API_KEY in environment
2. Create sandbox via POST /v1/kytchens/{id}/lines
3. Execute code via POST /v1/kytchens/{id}/lines/{line_id}/exec
4. Test timeout handling
5. Destroy sandbox via DELETE
6. Write integration tests in tests/test_e2b_integration.py
```

#### Day 5-6: Sentry Integration (SHA-137)
**Agent:** `general-executor`
```
Add Sentry error tracking:
1. pip install sentry-sdk[fastapi]
2. Add to kytchen/api/app.py with DSN from env
3. Add to Next.js frontend (kytchen-web)
4. Test error capture
5. Set up Slack alerts for critical errors
```

#### Day 6-7: Billing Testing (SHA-138) + Enforcement (SHA-139)
**Agent:** `general-executor`
```
Test and enforce Stripe billing:
1. Use Stripe CLI to test webhooks locally
2. Verify plan changes update workspace.plan
3. Add rate limiting middleware to FastAPI
4. Enforce check_lines_limit in create_line endpoint
5. Return proper 403 TierLimitError responses
```

---

## STRATEGIC CONTEXT

### The Core Insight
**GitHub is where humans store and develop code.**
**Kytchen is where LLMs develop code in a way natural to them.**

This is the correct competitive framing. We ARE a GitHub competitor - just for a different user: the LLM.

### What Kytchen IS
- The development environment designed for how LLMs actually work
- Programmatic context exploration (not cramming context into prompts)
- Evidence trail ("Sauce") system for verifiable conclusions
- MCP-native infrastructure layer
- Budget-controlled exploration with hard limits

### Competitive Frame
| Platform | Who It Serves | How It Works |
|----------|---------------|--------------|
| **GitHub** | Human developers | Files, branches, PRs, code review |
| **Kytchen** | LLM developers | Context exploration, sandboxed execution, evidence trails |
| LangChain | LLM orchestration | Chain-based, but context-cramming |
| RAG Systems | Document retrieval | Static retrieval, no exploration |
| E2B | Sandboxed execution | Execution only, no context layer |

### The One Thing
**Ship `pip install kytchen-sdk` this week.** That's the developer entry point. Nothing else matters until that works.

---

## FILE REFERENCE

### Python Backend (Modified This Session)
```
kytchen/
├── api/
│   ├── limits.py          # NEW: Tier enforcement
│   ├── routes/
│   │   ├── kytchens.py    # RENAMED from kitchens.py
│   │   ├── lines.py       # NEW: E2B sandbox endpoints
│   │   └── git.py         # NEW: Git API endpoints
│   └── app.py             # UPDATED: New router registrations
├── cli/
│   ├── git.py             # NEW: Git CLI commands
│   └── main.py            # UPDATED: Git command registration
└── mcp/
    └── local_server.py    # UPDATED: Git tools added
```

### Frontend (Modified This Session)
```
kytchen-web/
├── app/
│   ├── (auth)/layout.tsx        # Fixed em-dash
│   └── dashboard/
│       ├── page.tsx             # Fixed toast typo
│       └── runs/[id]/page.tsx   # Fixed bullet
└── components/
    ├── ui/open-kitchen.tsx      # Fixed unicode arrow
    └── runs/open-kitchen.tsx    # Fixed unicode arrow
```

### SDK to Publish
```
kytchen-sdk/
├── pyproject.toml         # Update metadata
├── src/kytchen/__init__.py
└── README.md              # Update for PyPI
```

---

## GIT COMMITS THIS SESSION

```
bace1d8 fix(web): replace unicode arrows with Lucide icons, fix toast typo
6f05839 feat(cli): add git command group
d052572 feat(api): add E2B Lines and Git API endpoints (SHA-117)
7fa9dfc refactor(api): rename Kitchen to Kytchen (SHA-111) + add tier limits
25fc46d style(web): clean unicode for Master Chef aesthetic
c32410e feat(mcp): add git tools to local server
```

---

## THE MAGIC PROMPT FOR NEXT CLAUDE

```
Read HANDOFF_V1_LAUNCH.md and execute the v1.0 launch plan:

1. CHECK Jules verification sessions - pull/merge any completed results:
   jules remote list --session | grep Shannon-Labs/Kytchen
   If any have patches, run: jules teleport <SESSION_ID>

2. USE linear-project-manager to check status of SHA-133 through SHA-139

3. PRIORITIZE SHA-133 (SDK publishing) - this is THE critical path:
   - Review kytchen-sdk/ directory
   - Update pyproject.toml
   - Set up GitHub Actions for PyPI
   - Publish to PyPI
   - Verify: pip install kytchen-sdk works

4. COMPLETE remaining P0 issues in order:
   - SHA-134: OpenAPI docs
   - SHA-135: Quickstart guide
   - SHA-136: E2B testing
   - SHA-137: Sentry integration
   - SHA-138: Stripe webhook testing
   - SHA-139: Billing enforcement

5. DOGFOOD using mcp__kytchen__* tools for all git operations

6. UPDATE Linear issues as each completes

The product launches when:
- pip install kytchen-sdk works
- /docs endpoint returns OpenAPI spec
- quickstart.md exists and is accurate
- E2B sandbox lifecycle is tested
- Sentry is capturing errors
- Billing enforcement is active

POSITIONING: GitHub is where humans develop code. Kytchen is where LLMs develop code.
We ARE a GitHub competitor - for the LLM user, not the human user.
```

---

## SUCCESS CRITERIA FOR V1.0

| Metric | Target | Current |
|--------|--------|---------|
| SDK on PyPI | Yes | No |
| OpenAPI docs live | Yes | No |
| Quickstart guide | Yes | No |
| E2B tested E2E | Yes | No |
| Error tracking | Yes | No |
| Billing enforced | Yes | Partial |
| Integration tests | 80%+ coverage | Unknown |
| Landing page | Production | Done |
| Master Chef aesthetic | Compliant | Done |

---

**The next Claude should be able to ship v1.0 in 5-7 focused days using this handoff.**
