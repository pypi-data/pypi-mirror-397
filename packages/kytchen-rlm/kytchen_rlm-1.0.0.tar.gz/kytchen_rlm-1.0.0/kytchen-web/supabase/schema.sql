-- THIS FILE IS FOR REFERENCE ONLY
-- Actual migrations are in /kytchen/supabase/migrations/
-- See: 001_initial_kytchen.sql, 002_audit_logs.sql

-- Workspaces
create table workspaces (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  plan text not null default 'free',
  stripe_customer_id text unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Members (workspace membership)
create table members (
  workspace_id uuid not null references workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'admin', 'member')),
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);

-- API Keys
create table api_keys (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  key_hash text not null unique,
  key_prefix text not null,
  name text,
  created_at timestamptz not null default now(),
  last_used_at timestamptz,
  revoked_at timestamptz
);

-- Datasets (pantry ingredients)
create table datasets (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  name text not null,
  description text,
  storage_bucket text not null default 'pantry',
  storage_path text not null,
  size_bytes bigint not null default 0,
  content_hash text not null,
  mime_type text,
  status text not null default 'uploaded' check (status in ('uploaded', 'processing', 'ready', 'failed')),
  processing_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Runs (analysis tickets)
create table runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  api_key_id uuid references api_keys(id) on delete set null,
  query text not null,
  dataset_ids uuid[] not null default '{}'::uuid[],
  budget jsonb not null default '{}'::jsonb,
  status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'failed', 'canceled')),
  e2b_sandbox_id text,
  answer text,
  success boolean,
  error text,
  metrics jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz
);

-- Evidence (citations)
create table evidence (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  run_id uuid not null references runs(id) on delete cascade,
  tool_name text not null,
  params jsonb not null default '{}'::jsonb,
  snippet text not null,
  line_start int,
  line_end int,
  note text,
  e2b_execution_id text,
  execution_time_ms float,
  created_at timestamptz not null default now()
);

-- Usage tracking
create table usage (
  workspace_id uuid primary key references workspaces(id) on delete cascade,
  month_start timestamptz not null default date_trunc('month', now()),
  storage_bytes bigint not null default 0,
  requests_this_month int not null default 0,
  egress_bytes_this_month bigint not null default 0,
  updated_at timestamptz not null default now()
);

-- Audit logs (append-only)
create table audit_logs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  event_type text not null,
  event_category text not null,
  severity text not null default 'info',
  actor_type text not null,
  actor_id text,
  actor_ip inet,
  user_agent text,
  resource_type text,
  resource_id uuid,
  description text not null,
  metadata jsonb not null default '{}'::jsonb,
  content_hash text not null,
  previous_hash text,
  created_at timestamptz not null default now()
);

-- Billing (Stripe)
create table billing (
  workspace_id uuid primary key references workspaces(id) on delete cascade,
  stripe_customer_id text unique,
  stripe_subscription_id text,
  stripe_price_id text,
  subscription_status text,
  current_period_start timestamptz,
  current_period_end timestamptz,
  cancel_at_period_end boolean default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Sandbox sessions (E2B)
create table sandbox_sessions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  run_id uuid references runs(id) on delete set null,
  e2b_sandbox_id text not null,
  context_id text not null default 'default',
  status text not null default 'active',
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  metadata jsonb not null default '{}'::jsonb
);

-- RLS enabled on all tables (see migrations for policies)
