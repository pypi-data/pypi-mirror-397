-- Kytchen Cloud v1.0: initial schema (Pantry + Prep + Sauce)
--
-- Tables:
-- - workspaces, members, api_keys
-- - datasets (ingredients), runs (tickets), evidence (sauce), usage
--
-- Non-negotiables:
-- - RLS enabled on ALL tables
-- - Policies for authenticated dashboard users (Supabase JWT)
-- - Optional policies for server-issued JWTs that include workspace_id claim

begin;

-- Extensions
create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Helpers
-- -----------------------------------------------------------------------------

create or replace function public.kytchen_jwt_workspace_id()
returns uuid
language sql
stable
as $$
  select nullif(current_setting('request.jwt.claims', true)::jsonb->>'workspace_id', '')::uuid;
$$;

create or replace function public.kytchen_set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- -----------------------------------------------------------------------------
-- Types
-- -----------------------------------------------------------------------------

do $$
begin
  if not exists (select 1 from pg_type where typname = 'workspace_plan') then
    create type public.workspace_plan as enum ('free', 'pro', 'team');
  end if;
  if not exists (select 1 from pg_type where typname = 'member_role') then
    create type public.member_role as enum ('owner', 'admin', 'member');
  end if;
  if not exists (select 1 from pg_type where typname = 'dataset_status') then
    create type public.dataset_status as enum ('uploaded', 'processing', 'ready', 'failed');
  end if;
  if not exists (select 1 from pg_type where typname = 'run_status') then
    create type public.run_status as enum ('queued', 'running', 'completed', 'failed', 'canceled');
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- Workspaces
-- -----------------------------------------------------------------------------

create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  plan public.workspace_plan not null default 'free',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger workspaces_set_updated_at
before update on public.workspaces
for each row execute function public.kytchen_set_updated_at();

-- -----------------------------------------------------------------------------
-- Members
-- -----------------------------------------------------------------------------

create table if not exists public.members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role public.member_role not null default 'member',
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);

create or replace function public.kytchen_is_workspace_member(ws_id uuid)
returns boolean
language sql
stable
as $$
  select exists (
    select 1
    from public.members m
    where m.workspace_id = ws_id
      and m.user_id = auth.uid()
  );
$$;

create or replace function public.kytchen_workspace_access(ws_id uuid)
returns boolean
language sql
stable
as $$
  -- Access via dashboard JWT membership OR server-issued JWT with workspace_id claim.
  select public.kytchen_is_workspace_member(ws_id)
      or public.kytchen_jwt_workspace_id() = ws_id;
$$;

-- -----------------------------------------------------------------------------
-- API Keys
-- -----------------------------------------------------------------------------

create table if not exists public.api_keys (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  key_hash text not null unique,
  key_prefix text not null,
  name text,
  created_at timestamptz not null default now(),
  last_used_at timestamptz,
  revoked_at timestamptz
);

-- -----------------------------------------------------------------------------
-- Datasets (Ingredients)
-- -----------------------------------------------------------------------------

create table if not exists public.datasets (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  name text not null,
  description text,
  storage_bucket text not null default 'pantry',
  storage_path text not null,
  size_bytes bigint not null default 0,
  content_hash text not null,
  mime_type text,
  status public.dataset_status not null default 'uploaded',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists datasets_workspace_id_idx on public.datasets(workspace_id);
create index if not exists datasets_content_hash_idx on public.datasets(content_hash);

create trigger datasets_set_updated_at
before update on public.datasets
for each row execute function public.kytchen_set_updated_at();

-- -----------------------------------------------------------------------------
-- Runs (Tickets)
-- -----------------------------------------------------------------------------

create table if not exists public.runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  api_key_id uuid references public.api_keys(id) on delete set null,
  query text not null,
  dataset_ids uuid[] not null default '{}'::uuid[],
  budget jsonb not null default '{}'::jsonb,
  status public.run_status not null default 'queued',
  tool_session_id text,
  answer text,
  success boolean,
  error text,
  created_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz
);

create index if not exists runs_workspace_id_idx on public.runs(workspace_id);
create index if not exists runs_created_at_idx on public.runs(created_at desc);

-- -----------------------------------------------------------------------------
-- Evidence (Sauce)
-- -----------------------------------------------------------------------------

create table if not exists public.evidence (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  run_id uuid not null references public.runs(id) on delete cascade,
  tool_name text not null,
  params jsonb not null default '{}'::jsonb,
  snippet text not null,
  line_start int,
  line_end int,
  note text,
  created_at timestamptz not null default now()
);

create index if not exists evidence_run_id_idx on public.evidence(run_id);
create index if not exists evidence_workspace_id_idx on public.evidence(workspace_id);

-- -----------------------------------------------------------------------------
-- Usage (Limits)
-- -----------------------------------------------------------------------------

create table if not exists public.usage (
  workspace_id uuid primary key references public.workspaces(id) on delete cascade,
  month_start timestamptz not null default date_trunc('month', now()),
  storage_bytes bigint not null default 0,
  requests_this_month int not null default 0,
  egress_bytes_this_month bigint not null default 0,
  updated_at timestamptz not null default now()
);

create trigger usage_set_updated_at
before update on public.usage
for each row execute function public.kytchen_set_updated_at();

-- -----------------------------------------------------------------------------
-- RLS (Isolation)
-- -----------------------------------------------------------------------------

alter table public.workspaces enable row level security;
alter table public.members enable row level security;
alter table public.api_keys enable row level security;
alter table public.datasets enable row level security;
alter table public.runs enable row level security;
alter table public.evidence enable row level security;
alter table public.usage enable row level security;

-- Workspaces
drop policy if exists workspaces_select on public.workspaces;
create policy workspaces_select
on public.workspaces
for select
using (public.kytchen_workspace_access(id));

drop policy if exists workspaces_insert on public.workspaces;
create policy workspaces_insert
on public.workspaces
for insert
with check (auth.uid() is not null);

drop policy if exists workspaces_update on public.workspaces;
create policy workspaces_update
on public.workspaces
for update
using (public.kytchen_is_workspace_member(id))
with check (public.kytchen_is_workspace_member(id));

-- Members
drop policy if exists members_select on public.members;
create policy members_select
on public.members
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists members_insert on public.members;
create policy members_insert
on public.members
for insert
with check (public.kytchen_is_workspace_member(workspace_id));

drop policy if exists members_update on public.members;
create policy members_update
on public.members
for update
using (public.kytchen_is_workspace_member(workspace_id))
with check (public.kytchen_is_workspace_member(workspace_id));

drop policy if exists members_delete on public.members;
create policy members_delete
on public.members
for delete
using (public.kytchen_is_workspace_member(workspace_id));

-- API Keys
drop policy if exists api_keys_select on public.api_keys;
create policy api_keys_select
on public.api_keys
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists api_keys_insert on public.api_keys;
create policy api_keys_insert
on public.api_keys
for insert
with check (public.kytchen_is_workspace_member(workspace_id));

drop policy if exists api_keys_update on public.api_keys;
create policy api_keys_update
on public.api_keys
for update
using (public.kytchen_is_workspace_member(workspace_id))
with check (public.kytchen_is_workspace_member(workspace_id));

drop policy if exists api_keys_delete on public.api_keys;
create policy api_keys_delete
on public.api_keys
for delete
using (public.kytchen_is_workspace_member(workspace_id));

-- Datasets
drop policy if exists datasets_select on public.datasets;
create policy datasets_select
on public.datasets
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists datasets_insert on public.datasets;
create policy datasets_insert
on public.datasets
for insert
with check (public.kytchen_workspace_access(workspace_id));

drop policy if exists datasets_update on public.datasets;
create policy datasets_update
on public.datasets
for update
using (public.kytchen_workspace_access(workspace_id))
with check (public.kytchen_workspace_access(workspace_id));

drop policy if exists datasets_delete on public.datasets;
create policy datasets_delete
on public.datasets
for delete
using (public.kytchen_workspace_access(workspace_id));

-- Runs
drop policy if exists runs_select on public.runs;
create policy runs_select
on public.runs
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists runs_insert on public.runs;
create policy runs_insert
on public.runs
for insert
with check (public.kytchen_workspace_access(workspace_id));

drop policy if exists runs_update on public.runs;
create policy runs_update
on public.runs
for update
using (public.kytchen_workspace_access(workspace_id))
with check (public.kytchen_workspace_access(workspace_id));

-- Evidence
drop policy if exists evidence_select on public.evidence;
create policy evidence_select
on public.evidence
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists evidence_insert on public.evidence;
create policy evidence_insert
on public.evidence
for insert
with check (public.kytchen_workspace_access(workspace_id));

-- Usage
drop policy if exists usage_select on public.usage;
create policy usage_select
on public.usage
for select
using (public.kytchen_workspace_access(workspace_id));

drop policy if exists usage_update on public.usage;
create policy usage_update
on public.usage
for update
using (public.kytchen_workspace_access(workspace_id))
with check (public.kytchen_workspace_access(workspace_id));

commit;
