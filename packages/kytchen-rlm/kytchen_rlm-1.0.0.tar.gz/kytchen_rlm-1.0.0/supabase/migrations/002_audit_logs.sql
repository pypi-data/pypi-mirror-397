-- Kytchen Cloud v1.0: Audit logs and billing tables
--
-- Tables:
-- - audit_logs (immutable append-only)
-- - billing (Stripe integration)
-- - sandbox_sessions (E2B tracking)
--
-- Non-negotiables:
-- - audit_logs is APPEND-ONLY (no update/delete policies)
-- - Hash chain for tamper detection

begin;

-- -----------------------------------------------------------------------------
-- Audit Logs (immutable append-only)
-- -----------------------------------------------------------------------------

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,

  -- Event classification
  event_type text not null,  -- 'run.started', 'dataset.uploaded', 'key.rotated', etc.
  event_category text not null,  -- 'data', 'auth', 'admin', 'system'
  severity text not null default 'info',  -- 'info', 'warning', 'error', 'critical'

  -- Actor (who)
  actor_type text not null,  -- 'user', 'api_key', 'system'
  actor_id text,  -- user_id, api_key_id, or 'system'
  actor_ip inet,  -- Source IP (for security events)
  user_agent text,  -- Request user agent

  -- Target (what)
  resource_type text,  -- 'run', 'dataset', 'api_key', 'workspace'
  resource_id uuid,

  -- Details
  description text not null,
  metadata jsonb not null default '{}'::jsonb,  -- Structured event data

  -- Immutability
  content_hash text not null,  -- SHA-256 of event data
  previous_hash text,  -- Hash chain for tamper detection

  -- Timing
  created_at timestamptz not null default now()
);

-- CRITICAL: Enable RLS
alter table public.audit_logs enable row level security;

-- Select only for workspace members
create policy audit_logs_select on public.audit_logs
for select using (public.kytchen_is_workspace_member(workspace_id));

-- Insert only via authenticated users or service role
-- No update or delete policies = append-only
create policy audit_logs_insert on public.audit_logs
for insert with check (
  public.kytchen_is_workspace_member(workspace_id)
  or current_setting('role', true) = 'service_role'
);

-- Indexes for efficient querying
create index if not exists audit_logs_workspace_id_idx on public.audit_logs(workspace_id);
create index if not exists audit_logs_created_at_idx on public.audit_logs(created_at desc);
create index if not exists audit_logs_event_type_idx on public.audit_logs(event_type);
create index if not exists audit_logs_actor_idx on public.audit_logs(actor_type, actor_id);
create index if not exists audit_logs_resource_idx on public.audit_logs(resource_type, resource_id);

-- -----------------------------------------------------------------------------
-- Billing (Stripe integration)
-- -----------------------------------------------------------------------------

create table if not exists public.billing (
  workspace_id uuid primary key references public.workspaces(id) on delete cascade,
  stripe_customer_id text unique,
  stripe_subscription_id text,
  stripe_price_id text,
  subscription_status text,  -- 'active', 'past_due', 'canceled', 'trialing'
  current_period_start timestamptz,
  current_period_end timestamptz,
  cancel_at_period_end boolean default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.billing enable row level security;

create policy billing_select on public.billing
for select using (public.kytchen_is_workspace_member(workspace_id));

create policy billing_update on public.billing
for update using (public.kytchen_is_workspace_member(workspace_id));

create trigger billing_set_updated_at
before update on public.billing
for each row execute function public.kytchen_set_updated_at();

-- -----------------------------------------------------------------------------
-- Sandbox Sessions (E2B tracking)
-- -----------------------------------------------------------------------------

create table if not exists public.sandbox_sessions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid references public.runs(id) on delete set null,
  e2b_sandbox_id text not null,
  context_id text not null default 'default',
  status text not null default 'active',  -- 'active', 'expired', 'terminated'
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  metadata jsonb not null default '{}'::jsonb
);

alter table public.sandbox_sessions enable row level security;

create policy sandbox_sessions_select on public.sandbox_sessions
for select using (public.kytchen_is_workspace_member(workspace_id));

create policy sandbox_sessions_manage on public.sandbox_sessions
for all using (public.kytchen_is_workspace_member(workspace_id));

create index if not exists sandbox_sessions_workspace_id_idx on public.sandbox_sessions(workspace_id);
create index if not exists sandbox_sessions_expires_at_idx on public.sandbox_sessions(expires_at);
create index if not exists sandbox_sessions_e2b_id_idx on public.sandbox_sessions(e2b_sandbox_id);

-- -----------------------------------------------------------------------------
-- Add stripe_customer_id to workspaces (for lookup)
-- -----------------------------------------------------------------------------

alter table public.workspaces add column if not exists stripe_customer_id text unique;

-- -----------------------------------------------------------------------------
-- Add processing_error to datasets
-- -----------------------------------------------------------------------------

alter table public.datasets add column if not exists processing_error text;

-- -----------------------------------------------------------------------------
-- Add metrics to runs
-- -----------------------------------------------------------------------------

alter table public.runs add column if not exists e2b_sandbox_id text;
alter table public.runs add column if not exists metrics jsonb not null default '{}'::jsonb;

-- -----------------------------------------------------------------------------
-- Add execution metadata to evidence
-- -----------------------------------------------------------------------------

alter table public.evidence add column if not exists e2b_execution_id text;
alter table public.evidence add column if not exists execution_time_ms float;

commit;
