# Kytchen Cost Model & Safety Limits (BYOLLM)

Kytchen is BYOLLM: users bring their own LLM (their keys/subscriptions). Kytchen’s costs are primarily **storage + bandwidth + light compute** for tool execution and evidence/metrics tracking.

## Baseline Infrastructure Costs (ballpark)

- Supabase Pro: `$25/mo` base (includes `8GB` DB, `100GB` storage, `50GB` egress)
- Railway: `~$5–20/mo` for a small API (usage-based CPU/RAM seconds)
- Vercel: Free tier is typically enough for the dashboard early on

## Sanity Scenarios

- 1,000 free users @ 50–100MB each → ~50–100GB storage (fits in Supabase Pro) + modest API compute
- 10,000 free users @ 50–100MB each → 0.5–1TB storage (storage overage starts to matter); rate limits + egress caps become critical

## “Must Implement” Safety Mechanisms

### 1) Hard storage limits (pre-flight)

Reject uploads/writes before any work is done:

```python
if workspace.storage_used + file_size > PLAN_LIMITS[workspace.plan]["storage_bytes"]:
    raise HTTPException(status_code=402, detail="Storage limit reached. Upgrade to continue.")
```

### 2) Rate limiting (per API key)

Enforce at the API edge using Redis/Upstash:

- Free: `5 req/min`
- Pro: `100 req/min`
- Team: `200 req/min`

### 3) Request timeout (per plan)

- Free: `15s`
- Pro: `60s`
- Team: `120s`

### 4) Egress limits (prevent bandwidth abuse)

Track egress per workspace per month and throttle/reject:

- Free: `1GB/mo`
- Pro: `50GB/mo`
- Team: `200GB/mo`

## Plan Limits (environment-configurable)

```python
PLAN_LIMITS = {
    "free": {
        "storage_bytes": 50 * 1024 * 1024,  # 50MB
        "rate_limit_per_min": 5,
        "timeout_seconds": 15,
        "egress_bytes_per_month": 1 * 1024 * 1024 * 1024,  # 1GB
        "history_days": 3,
        "workspaces": 1,
    },
    "pro": {
        "storage_bytes": 10 * 1024 * 1024 * 1024,  # 10GB
        "rate_limit_per_min": 100,
        "timeout_seconds": 60,
        "egress_bytes_per_month": 50 * 1024 * 1024 * 1024,  # 50GB
        "history_days": 90,
        "workspaces": 3,
    },
    "team": {
        "storage_bytes": 50 * 1024 * 1024 * 1024,  # 50GB
        "rate_limit_per_min": 200,
        "timeout_seconds": 120,
        "egress_bytes_per_month": 200 * 1024 * 1024 * 1024,  # 200GB
        "history_days": 365,
        "workspaces": -1,  # unlimited
    },
}
```

## Usage Tracking Schema (for limits)

```sql
CREATE TABLE workspace_usage (
  workspace_id UUID PRIMARY KEY REFERENCES workspaces(id),
  storage_bytes BIGINT DEFAULT 0,
  requests_this_month INT DEFAULT 0,
  egress_bytes_this_month BIGINT DEFAULT 0,
  last_reset_at TIMESTAMPTZ DEFAULT date_trunc('month', now()),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION reset_monthly_usage()
RETURNS void AS $$
  UPDATE workspace_usage
  SET requests_this_month = 0,
      egress_bytes_this_month = 0,
      last_reset_at = now(),
      updated_at = now()
  WHERE last_reset_at < date_trunc('month', now());
$$ LANGUAGE sql;
```

