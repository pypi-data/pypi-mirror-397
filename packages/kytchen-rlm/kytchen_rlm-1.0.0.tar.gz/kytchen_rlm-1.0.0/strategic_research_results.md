# Strategic Memo: How Kytchen Can Capitalize on GitHub Actions’ 2026 Pricing Shift

**To:** Kytchen Leadership  
**From:** Strategic Advisor  
**Date:** December 16, 2025  
**Subject:** Using the “self-hosted runner tax” moment to win agentic workloads

## Executive Take

GitHub is explicitly repositioning Actions as an execution layer for “agentic workloads” and is updating pricing to match. This creates a short window (now → March 2026) where the most vocal, highest-usage segment is motivated to evaluate alternatives. Kytchen can win by **not competing on CI**—compete on **agent runtime**: durable state (Pantry), traceability (Sauce), and predictable billing (bundles + hard caps).

## 1) What GitHub Changed (and Why It Matters)

**Announced changes**
- **Jan 1, 2026:** GitHub-hosted runner rates decrease (up to ~39%, by machine type).
- **Mar 1, 2026:** New **$0.002/min GitHub Actions cloud platform charge** applies to **self-hosted runner usage in private repos**.
- **No change:** Actions usage in **public repos remains free**; **GitHub Enterprise Server is not impacted**.

**GitHub’s own framing**
- Actions is scaling massively (GitHub cites ~71M jobs/day on the new architecture) and is being positioned to “power … agentic workload.”

**Why this is a wedge**
- The platform charge is small per minute but becomes meaningful at scale—and it stacks on top of customers’ existing infra spend for self-hosted runners.
- More importantly: the pricing move forces a conversation about what belongs in CI/CD vs what belongs in an “agent runtime.”

**Quick math (platform charge only)**
- 100k self-hosted minutes/month → **$200/month**
- 1M minutes/month → **$2,000/month**
- 10M minutes/month → **$20,000/month**

These are exactly the orgs that have (a) heavy automation footprints, (b) private-repo requirements, and (c) meaningful interest in autonomous/long-running agents.

## 2) Who’s Motivated to Switch (ICP)

The “best” customers are not the median user—GitHub itself says most users see decreases and median increases are small. The winners for Kytchen are teams that:
- Run **high-volume self-hosted runners in private repos** (platform charge becomes a line item CFOs notice).
- Run **long/iterative workloads** (agent loops, repo-wide refactors, large test generation, deep research/synthesis, data processing).
- Need **durable state and provenance** (compliance, regulated industries, security teams, enterprise DevEx).
- Already feel pain with Actions’ CI-first constraints (timeouts, brittle caching, lack of first-class state, noisy logs not “evidence”).

## 3) What Developers Are Actually Upset About (Sentiment Summary)

The loudest negative reactions aren’t “$0.002/min is huge,” they’re:
- “We already pay for the machines; charging per-minute for self-hosted feels like a tax.”
- “Per-minute pricing is hard to forecast for agent workloads that are spiky and long-running.”
- “If we have to re-architect anyway, we should reduce lock-in (GitLab/Buildkite/Forgejo came up repeatedly).”

That is precisely the narrative Kytchen can own: **agents need state + auditability + predictable billing**—CI systems don’t optimize for that.

## 4) Competitive Landscape (Pricing Models That Shape Expectations)

**GitHub Actions**
- Per-minute rates for GitHub-hosted runners; **self-hosted platform charge $0.002/min (Mar 2026)**.

**CircleCI**
- **Credits** system + seats; includes explicit allowances even for “self-hosted runners” (not free to use the platform at scale).

**GitLab CI (GitLab.com)**
- “Compute minutes” quotas with **cost factors** by runner type/size; predictable if you live within quota, but still a “minutes” mental model.

**Buildkite**
- **Per-concurrent-agent** pricing (plus per active user); arguably the most predictable for heavy CI fleets.

**Infra-style platforms (Railway, Render, Modal, E2B)**
- Usage-based compute (per-second/per-minute), predictable only if you implement budgeting and caps.

**Implication for Kytchen**
The market is being trained toward metering. Your differentiation is not “no metering,” it’s: **metering that matches agent value** (state + evidence + long-running orchestration), with **hard caps** so bills never surprise.

## 5) Recommended Positioning (One-Liner + Demo “Aha”)

**One-liner**
“Kytchen is the agent runtime you wish GitHub Actions was: durable state (Pantry), auditable evidence (Sauce), and predictable pricing for long-running work.”

**Demo “aha” (must be visceral)**
Show an agent that:
1) runs for hours,  
2) persists state every step to Pantry,  
3) produces a Sauce bundle you can audit,  
4) resumes after interruption without losing context.

Position this as: “CI tools are for builds. Agent tools are for outcomes.”

## 6) Pricing Proposal (3 Tiers, Predictable by Design)

Principles:
- **Anchor on Pantry (storage + retention)** as the moat and budget-control surface.
- Bundle **agent-hours** (not raw minutes) to keep invoices legible.
- Enforce **hard caps** and **auto-stop** to prevent surprise bills.
- Keep BYOLLM: customers manage model spend separately.

Unit economics sanity check (based on public E2B pricing; validate with your actual invoice):
- 2 vCPU costs ~$0.000028/s → **~$0.10/hr**; memory costs **$0.0000045/GiB/s** (4GiB → **~$0.06/hr**). Roughly **$0.17/agent-hour** for a small sandbox.
- 8 vCPU costs ~$0.000112/s → **~$0.40/hr**; 8GiB memory → **~$0.13/hr**. Roughly **$0.53/agent-hour** for a bigger box.

This suggests overage priced at **$0.75–$1.50/agent-hour** can support 70%+ gross margin while still feeling legible vs “minutes + surprise.”

### Commis (Free)
- **$0/month**
- 1GB Pantry, basic Sauce retention
- 60 minutes/month standard runtime
- 1 concurrent ticket, strict caps (no overage without card)

### Chef (Pro)
- **$29/month**
- 25GB Pantry
- 50 agent-hours/month standard runtime
- 3 concurrent tickets
- 30-day Sauce retention
- Overage: simple per-agent-hour rate + configurable hard cap

### Brigade (Team)
- **$149/month** (includes 3 seats)
- 200GB Pantry
- 250 agent-hours/month standard runtime
- 10 concurrent tickets
- Shared secrets + access controls
- Retention add-on (e.g., 1-year Sauce) for compliance buyers

### Enterprise
- Custom: SSO/SAML, SLAs, dedicated isolation, audit exports, retention policies, procurement-friendly terms

## 7) Go-to-Market Wedge (Tactical Playbook)

**Wedge message:** “Stop paying the self-hosted runner tax for agent workloads.”

Ship (in order):
1) **Actions-cost calculator landing page**: upload last month’s Actions usage report → estimate Mar 2026 platform charge → recommend a Kytchen plan.
2) **No-migration integration**: a GitHub Action that dispatches a Kytchen Ticket and posts status/results back to the PR. Keep CI in Actions, move agent execution to Kytchen.
3) **Content series**: “Why agents shouldn’t run on CI/CD” + “Agent runtime vs CI runner” (use GitHub’s own “agentic workload” language).
4) **Targeted outbound**: orgs using ARC / runner scale sets / large runner fleets; offer an audit + migration workshop with a concrete bill forecast.

## 8) MVP Checklist (Must-Have vs Later)

**Must-have to charge money**
- Stripe billing (subscriptions + overage), invoices, tax/VAT basics
- Runtime + storage + retention **metering** that is visible and exportable
- Hard caps + auto-stop / kill tickets when budget is exceeded
- Supabase RLS isolation (Pantry + Sauce must be tenant-proof)
- API keys + revocation + minimal dashboard (tickets, pantry, usage)
- Retention controls (Sauce/Pantry) as a first-class setting

**Nice-to-have (v1.1)**
- Teams/orgs, project roles, shared secrets UX
- SSO/SAML
- Nicer Sauce visualizations + evidence export bundles

**Skip (v2+)**
- Self-hosted Kytchen (weakens SaaS moat)

## Sources

- GitHub Changelog: https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/
- GitHub Executive Insights: https://resources.github.com/actions/2026-pricing-changes-for-github-actions
- Actions runner pricing reference: https://docs.github.com/billing/reference/actions-runner-pricing
- HN discussion: https://news.ycombinator.com/item?id=46291414
