create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  major text,
  avatar_url text,
  bio text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tribes (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  category text,
  icon text,
  owner_id uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tribe_members (
  id uuid primary key default gen_random_uuid(),
  tribe_id uuid not null references public.tribes(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner', 'admin', 'member')),
  joined_at timestamptz not null default now(),
  unique (tribe_id, user_id)
);

create table if not exists public.events (
  id uuid primary key default gen_random_uuid(),
  tribe_id uuid not null references public.tribes(id) on delete cascade,
  title text not null,
  description text,
  location text,
  start_time timestamptz,
  status text not null default 'recruiting' check (status in ('recruiting', 'ongoing', 'finished', 'cancelled')),
  cover_icon text,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.event_registrations (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'registered' check (status in ('registered', 'cancelled', 'checked_in')),
  registered_at timestamptz not null default now(),
  unique (event_id, user_id)
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  tribe_id uuid references public.tribes(id) on delete set null,
  event_id uuid references public.events(id) on delete set null,
  title text,
  content text not null,
  type text not null default 'system' check (type in ('system', 'tribe', 'event', 'ai')),
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.tribe_posts (
  id uuid primary key default gen_random_uuid(),
  tribe_id uuid not null references public.tribes(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table if not exists public.tribe_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.tribe_posts(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete cascade,
  parent_id uuid references public.tribe_comments(id) on delete set null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists set_tribes_updated_at on public.tribes;
create trigger set_tribes_updated_at
before update on public.tribes
for each row execute function public.set_updated_at();

drop trigger if exists set_events_updated_at on public.events;
create trigger set_events_updated_at
before update on public.events
for each row execute function public.set_updated_at();

drop trigger if exists set_tribe_posts_updated_at on public.tribe_posts;
create trigger set_tribe_posts_updated_at
before update on public.tribe_posts
for each row execute function public.set_updated_at();

drop trigger if exists set_tribe_comments_updated_at on public.tribe_comments;
create trigger set_tribe_comments_updated_at
before update on public.tribe_comments
for each row execute function public.set_updated_at();

create index if not exists idx_tribe_members_user_id on public.tribe_members(user_id);
create index if not exists idx_tribe_members_tribe_id on public.tribe_members(tribe_id);
create index if not exists idx_events_tribe_id on public.events(tribe_id);
create index if not exists idx_event_registrations_user_id on public.event_registrations(user_id);
create index if not exists idx_messages_user_id on public.messages(user_id);
create index if not exists idx_tribe_posts_tribe_id on public.tribe_posts(tribe_id);
create index if not exists idx_tribe_posts_author_id on public.tribe_posts(author_id);
create index if not exists idx_tribe_comments_post_id on public.tribe_comments(post_id);
create index if not exists idx_tribe_comments_parent_id on public.tribe_comments(parent_id);
create index if not exists idx_tribe_comments_author_id on public.tribe_comments(author_id);
