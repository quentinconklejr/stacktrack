# ⚗️ StackTrack

Peptide and biohacking protocol tracker built with Streamlit + Supabase.
Log your compounds, score daily metrics, and compare results anonymously
against the community average.

---

## Quick start

```bash
mkdir stacktrack && cd stacktrack
```

Then clone or copy this folder, install deps, add your env vars, and run:

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your Supabase keys
streamlit run app.py
```

---

## Folder structure

```
stacktrack/
├── app.py                  # entire Streamlit app (single file)
├── requirements.txt        # Python dependencies
├── .env.example            # env var template — copy to .env
└── .streamlit/
    └── config.toml         # dark theme + primary color
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in all three values:

```env
# Project Settings > API > URL
SUPABASE_URL=https://your-project-ref.supabase.co

# anon/public key — respects Row Level Security
SUPABASE_KEY=your-anon-key-here

# service_role key — bypasses RLS, required for community aggregation
# Project Settings > API > service_role  (keep this secret)
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

Without `SUPABASE_SERVICE_KEY` the Community Insights page still loads
but aggregated views may only reflect the current user's own data.

---

## Supabase schema

Paste this entire block into the Supabase SQL editor and run it.
The `DROP` statements at the top make it safe to re-run at any time.

```sql
-- ============================================================
-- TEARDOWN (reverse dependency order)
-- ============================================================
drop view if exists public.community_averages;
drop view if exists public.community_summary;
drop trigger if exists trg_on_auth_user_created on auth.users;
drop table if exists public.daily_logs  cascade;
drop table if exists public.protocols   cascade;
drop table if exists public.users       cascade;
drop function if exists public.set_updated_at();
drop function if exists public.handle_new_user();

-- ============================================================
-- EXTENSIONS
-- ============================================================
create extension if not exists "uuid-ossp";

-- ============================================================
-- USERS
-- ============================================================
create table public.users (
  id            uuid primary key references auth.users(id) on delete cascade,
  username      text unique,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- ============================================================
-- PROTOCOLS
-- ============================================================
create table public.protocols (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references public.users(id) on delete cascade,
  compound      text not null,
  dose_amount   numeric(10,3) not null,
  dose_unit     text not null default 'mcg',
  frequency     text not null,
  timing        text,
  route         text not null default 'subq',
  source        text,
  notes         text,
  is_active     boolean not null default true,
  started_at    date not null default current_date,
  ended_at      date,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),

  constraint valid_dose      check (dose_amount > 0),
  constraint valid_dates     check (ended_at is null or ended_at >= started_at),
  constraint valid_route     check (route in ('subq','im','oral','nasal','topical','other')),
  constraint valid_dose_unit check (dose_unit in ('mcg','mg','IU','ml','other'))
);

create index idx_protocols_user_id  on public.protocols(user_id);
create index idx_protocols_compound on public.protocols(lower(compound));

-- ============================================================
-- DAILY LOGS
-- ============================================================
create table public.daily_logs (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references public.users(id) on delete cascade,
  protocol_id   uuid references public.protocols(id) on delete set null,
  log_date      date not null default current_date,

  energy        smallint check (energy between 1 and 10),
  sleep         smallint check (sleep between 1 and 10),
  recovery      smallint check (recovery between 1 and 10),
  libido        smallint check (libido between 1 and 10),
  mood          smallint check (mood between 1 and 10),

  weight_kg     numeric(5,2),
  body_temp_c   numeric(4,2),
  side_effects  text[],
  notes         text,

  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),

  unique (user_id, protocol_id, log_date)
);

create index idx_daily_logs_user_id     on public.daily_logs(user_id);
create index idx_daily_logs_protocol_id on public.daily_logs(protocol_id);
create index idx_daily_logs_date        on public.daily_logs(log_date desc);

-- ============================================================
-- COMMUNITY AGGREGATION VIEW
-- Groups by compound + day-of-protocol so users see
-- "how do people feel on day 7 of BPC-157?"
-- Suppressed when < 3 distinct users to preserve anonymity.
-- ============================================================
create view public.community_averages as
select
  lower(p.compound)                          as compound,
  (dl.log_date - p.started_at) + 1          as protocol_day,
  count(distinct dl.user_id)                 as user_count,
  round(avg(dl.energy),   2)                 as avg_energy,
  round(avg(dl.sleep),    2)                 as avg_sleep,
  round(avg(dl.recovery), 2)                 as avg_recovery,
  round(avg(dl.libido),   2)                 as avg_libido,
  round(avg(dl.mood),     2)                 as avg_mood
from public.daily_logs  dl
join public.protocols   p  on p.id = dl.protocol_id
where
  dl.energy   is not null or
  dl.sleep    is not null or
  dl.recovery is not null or
  dl.libido   is not null or
  dl.mood     is not null
group by lower(p.compound), protocol_day
having count(distinct dl.user_id) >= 3;

-- ============================================================
-- COMMUNITY SUMMARY VIEW (overall per-compound averages)
-- ============================================================
create view public.community_summary as
select
  lower(p.compound)              as compound,
  count(distinct dl.user_id)     as total_users,
  count(*)                       as total_log_entries,
  round(avg(dl.energy),   2)     as avg_energy,
  round(avg(dl.sleep),    2)     as avg_sleep,
  round(avg(dl.recovery), 2)     as avg_recovery,
  round(avg(dl.libido),   2)     as avg_libido,
  round(avg(dl.mood),     2)     as avg_mood
from public.daily_logs  dl
join public.protocols   p  on p.id = dl.protocol_id
group by lower(p.compound)
having count(distinct dl.user_id) >= 3;

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger trg_users_updated_at
  before update on public.users
  for each row execute function public.set_updated_at();

create trigger trg_protocols_updated_at
  before update on public.protocols
  for each row execute function public.set_updated_at();

create trigger trg_daily_logs_updated_at
  before update on public.daily_logs
  for each row execute function public.set_updated_at();

-- ============================================================
-- AUTO-CREATE USER PROFILE ON SIGN-UP
-- ============================================================
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.users (id)
  values (new.id)
  on conflict (id) do nothing;
  return new;
end;
$$;

create trigger trg_on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================
alter table public.users       enable row level security;
alter table public.protocols   enable row level security;
alter table public.daily_logs  enable row level security;

create policy "users_select_own" on public.users
  for select using (auth.uid() = id);
create policy "users_update_own" on public.users
  for update using (auth.uid() = id);

create policy "protocols_select_own" on public.protocols
  for select using (auth.uid() = user_id);
create policy "protocols_insert_own" on public.protocols
  for insert with check (auth.uid() = user_id);
create policy "protocols_update_own" on public.protocols
  for update using (auth.uid() = user_id);
create policy "protocols_delete_own" on public.protocols
  for delete using (auth.uid() = user_id);

create policy "logs_select_own" on public.daily_logs
  for select using (auth.uid() = user_id);
create policy "logs_insert_own" on public.daily_logs
  for insert with check (auth.uid() = user_id);
create policy "logs_update_own" on public.daily_logs
  for update using (auth.uid() = user_id);
create policy "logs_delete_own" on public.daily_logs
  for delete using (auth.uid() = user_id);

-- Community views: any authenticated user can read aggregated data
grant select on public.community_averages to authenticated;
grant select on public.community_summary  to authenticated;
```

---

## App pages

| Page | What it does |
|---|---|
| **Dashboard** | Streak counter, active protocol cards with day counter, recent log table. Shows onboarding for new accounts. |
| **Log Today** | Pick a protocol, rate energy / sleep / recovery / libido / mood 1–10, add notes. Upserts so re-submitting the same day updates the existing entry. |
| **My Protocols** | Three tabs — *Active* (cards + stop button + past protocols expander), *Trends* (spline charts per metric + combined overlay), *Add New* (protocol form). |
| **Community Insights** | Trending this week (medal cards), all-compounds score table with heatmap gradient, grouped bar chart comparing your averages vs community. |

---

## Sidebar features

- **Streak pill** — consecutive days logged. Flame count scales: 1 flame up to day 6, 2 from day 7, 3 from day 21.
- **Programmatic navigation** — the onboarding CTA and any internal link can set `st.session_state["nav_page"]` to jump to a page without URL hacks.

---

## How community aggregation works

The `community_averages` and `community_summary` views run at the Postgres level. A compound only appears once **3 or more distinct users** have logged data for it — this is a k-anonymity floor so no single user's scores are identifiable.

Supabase views run with security invoker by default, meaning the underlying RLS still applies when queried with the anon key. Setting `SUPABASE_SERVICE_KEY` makes the app use the service-role client for community queries, bypassing RLS so all users' aggregated (never individual) data is visible.

---

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit 1.32+ |
| Charts | Plotly (dark theme, spline smoothing) |
| Backend / DB | Supabase (Postgres + Auth + RLS) |
| Python client | supabase-py 2.x |
| Auth | Supabase email/password, session tokens stored in `st.session_state` |
