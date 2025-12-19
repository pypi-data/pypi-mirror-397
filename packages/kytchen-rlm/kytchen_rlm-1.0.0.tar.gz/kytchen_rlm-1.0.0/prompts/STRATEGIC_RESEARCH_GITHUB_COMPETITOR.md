# Strategic Research: Kytchen vs GitHub Actions for Agentic Workloads

## Context for Claude

You are a strategic advisor helping Kytchen (a commercial AI agent orchestration platform) capitalize on GitHub's pricing changes and position as a GitHub Actions alternative for **agentic workloads**.

**GitHub just announced** (effective 2026):
- $0.002/min charge for self-hosted runners (NEW fee that didn't exist)
- "Actions usage has grown significantly, across both CI/CD and **agentic workloads**"
- 96% of customers see lower/no change = **4% power users get hit harder**

**Kytchen's current positioning**: "Heroku for AI Agents" - BYOLLM context orchestration with audit trails ("Sauce").

---

## Research Tasks

### 1. GitHub Vulnerability Analysis

Search the web for:
- Developer reactions to GitHub Actions pricing changes (Twitter/X, HN, Reddit)
- GitHub Actions limitations for AI/agent workloads
- Companies that have publicly complained about GitHub Actions costs
- What "agentic workloads" actually means in GitHub's context
- GitHub Copilot Workspace / GitHub's AI agent strategy

**Questions to answer:**
- Who are the 4% getting price increases? What do they have in common?
- What's the actual $/month difference for a heavy Actions user?
- Are there patterns in what people hate about Actions for AI work?

### 2. Competitive Landscape

Research these competitors and their pricing:
- **GitHub Actions** - per-minute compute
- **CircleCI** - credits system
- **GitLab CI** - compute minutes
- **Buildkite** - per-agent pricing
- **Dagger** - container-based CI
- **Railway** - usage-based
- **Render** - usage-based
- **Modal** - serverless GPU/compute
- **E2B** - sandbox pricing (we use this)

**Questions to answer:**
- How does each price? Per-minute? Per-job? Per-storage?
- Which model is most predictable for users?
- Which model has the best margins for the provider?
- What's the "Goldilocks" pricing that's fair but profitable?

### 3. Kytchen's Cost Structure

Our actual costs come from:
- **Vercel** (frontend hosting) - what tier do we need?
- **Supabase** (database + auth) - what tier do we need?
- **E2B** (sandboxes) - $0.05/min for sandbox time
- **Bandwidth** - egress costs

**Questions to answer:**
- What does it cost US to run one "ticket" (query)?
- What margin do we need? (SaaS standard is 70-80% gross margin)
- Storage-based pricing: what $/GB/month is competitive AND profitable?

### 4. Minimum Viable Commercial Product

What can we **NOT** launch without?
- [ ] Auth (Supabase handles this)
- [ ] Billing/payments (Stripe)
- [ ] Usage metering
- [ ] API rate limiting
- [ ] Multi-tenant isolation
- [ ] ???

What can we **SKIP** for v1?
- Teams/orgs? (just personal accounts first?)
- SSO/SAML?
- Self-host option? (user says NO - we need the moat)
- ???

### 5. Positioning Against GitHub

GitHub's weakness:
- Per-minute pricing is unpredictable for AI workloads
- No native "context management" for agents
- No audit trail / evidence system
- Copilot is closed - you can't BYOLLM

Kytchen's pitch:
- **Storage-based pricing** = predictable monthly bill
- **BYOLLM** = use any model, control your AI costs separately
- **Sauce (evidence trail)** = audit everything for compliance
- **Context orchestration** = don't burn tokens stuffing prompts

**Questions to answer:**
- What's the one-liner that makes a GitHub Actions user switch?
- What's the "aha moment" in a demo?
- Who's the ICP? (DevOps? AI Engineers? Compliance teams?)

### 6. Pricing Model Proposal

Create 3 pricing tiers with:
- **Free tier** (enough to try, not enough to freeload)
- **Pro tier** (individual power users)
- **Team tier** (companies)

Consider:
- Storage (Pantry) - $/GB/month
- Compute (Tickets) - included minutes or $/minute overage?
- Seats - per-user or unlimited?

Compare to:
- GitHub: $4/user/month (Pro), $21/user/month (Team)
- Vercel: $20/user/month (Pro)
- Supabase: $25/month (Pro)

---

## Deliverables

1. **Market Opportunity Summary** (1 page)
   - Size of the "agentic workloads" market
   - GitHub's vulnerability
   - Window of opportunity (before/after their Jan 2026 changes)

2. **Competitive Matrix** (table)
   - Feature comparison: Kytchen vs GitHub Actions vs alternatives
   - Pricing comparison

3. **Recommended Pricing** (with justification)
   - Three tiers
   - What's included
   - Why this beats GitHub for our ICP

4. **Go-to-Market Wedge** (1 page)
   - Who do we sell to first?
   - What's the message?
   - What content/demos do we need?

5. **MVP Feature Checklist**
   - Must-have for launch
   - Nice-to-have (v1.1)
   - Skip entirely

---

## Resources

- GitHub pricing announcement: https://github.blog/news-insights/company-news/evolving-github-actions-pricing/
- GitHub Actions pricing calculator: https://github.com/pricing/calculator
- E2B pricing: https://e2b.dev/pricing
- Supabase pricing: https://supabase.com/pricing
- Vercel pricing: https://vercel.com/pricing

---

## Output Format

Write your findings as a strategic memo. Be opinionated. Make recommendations, don't just list options. The founder is overwhelmed - they need clear "do this" guidance, not "here are 10 options."

---

*This research will inform Kytchen's commercial launch strategy and pricing.*
