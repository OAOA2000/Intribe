alter table public.profiles enable row level security;
alter table public.tribes enable row level security;
alter table public.tribe_members enable row level security;
alter table public.events enable row level security;
alter table public.event_registrations enable row level security;
alter table public.messages enable row level security;
alter table public.tribe_posts enable row level security;
alter table public.tribe_comments enable row level security;

create or replace function public.is_tribe_manager(target_tribe_id uuid, target_user_id uuid default auth.uid())
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1
    from public.tribe_members tm
    where tm.tribe_id = target_tribe_id
      and tm.user_id = target_user_id
      and tm.role in ('owner', 'admin')
  )
  or exists (
    select 1
    from public.tribes t
    where t.id = target_tribe_id
      and t.owner_id = target_user_id
  );
$$;

create or replace function public.is_event_manager(target_event_id uuid, target_user_id uuid default auth.uid())
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1
    from public.events e
    where e.id = target_event_id
      and (e.created_by = target_user_id or public.is_tribe_manager(e.tribe_id, target_user_id))
  );
$$;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
on public.profiles for select
using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
on public.profiles for insert
with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
on public.profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

drop policy if exists "tribes_select_authenticated" on public.tribes;
create policy "tribes_select_authenticated"
on public.tribes for select
to authenticated
using (true);

drop policy if exists "tribes_insert_authenticated_owner" on public.tribes;
create policy "tribes_insert_authenticated_owner"
on public.tribes for insert
to authenticated
with check (owner_id = auth.uid());

drop policy if exists "tribes_update_managers" on public.tribes;
create policy "tribes_update_managers"
on public.tribes for update
to authenticated
using (public.is_tribe_manager(id))
with check (public.is_tribe_manager(id));

drop policy if exists "tribe_members_select_self_or_manager" on public.tribe_members;
create policy "tribe_members_select_self_or_manager"
on public.tribe_members for select
to authenticated
using (user_id = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "tribe_members_insert_self_or_manager" on public.tribe_members;
create policy "tribe_members_insert_self_or_manager"
on public.tribe_members for insert
to authenticated
with check (user_id = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "tribe_members_update_manager" on public.tribe_members;
create policy "tribe_members_update_manager"
on public.tribe_members for update
to authenticated
using (public.is_tribe_manager(tribe_id))
with check (public.is_tribe_manager(tribe_id));

drop policy if exists "tribe_members_delete_self_or_manager" on public.tribe_members;
create policy "tribe_members_delete_self_or_manager"
on public.tribe_members for delete
to authenticated
using (user_id = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "events_select_authenticated" on public.events;
create policy "events_select_authenticated"
on public.events for select
to authenticated
using (true);

drop policy if exists "events_insert_tribe_manager" on public.events;
create policy "events_insert_tribe_manager"
on public.events for insert
to authenticated
with check (created_by = auth.uid() and public.is_tribe_manager(tribe_id));

drop policy if exists "events_update_manager" on public.events;
create policy "events_update_manager"
on public.events for update
to authenticated
using (created_by = auth.uid() or public.is_tribe_manager(tribe_id))
with check (created_by = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "events_delete_manager" on public.events;
create policy "events_delete_manager"
on public.events for delete
to authenticated
using (created_by = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "event_registrations_select_self_or_event_manager" on public.event_registrations;
create policy "event_registrations_select_self_or_event_manager"
on public.event_registrations for select
to authenticated
using (user_id = auth.uid() or public.is_event_manager(event_id));

drop policy if exists "event_registrations_insert_self" on public.event_registrations;
create policy "event_registrations_insert_self"
on public.event_registrations for insert
to authenticated
with check (user_id = auth.uid());

drop policy if exists "event_registrations_update_self_or_event_manager" on public.event_registrations;
create policy "event_registrations_update_self_or_event_manager"
on public.event_registrations for update
to authenticated
using (user_id = auth.uid() or public.is_event_manager(event_id))
with check (user_id = auth.uid() or public.is_event_manager(event_id));

drop policy if exists "messages_select_own" on public.messages;
create policy "messages_select_own"
on public.messages for select
to authenticated
using (user_id = auth.uid());

drop policy if exists "messages_update_own" on public.messages;
create policy "messages_update_own"
on public.messages for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "tribe_posts_select_authenticated" on public.tribe_posts;
create policy "tribe_posts_select_authenticated"
on public.tribe_posts for select
to authenticated
using (deleted_at is null);

drop policy if exists "tribe_posts_insert_authenticated_author" on public.tribe_posts;
create policy "tribe_posts_insert_authenticated_author"
on public.tribe_posts for insert
to authenticated
with check (author_id = auth.uid());

drop policy if exists "tribe_posts_update_author_or_manager" on public.tribe_posts;
create policy "tribe_posts_update_author_or_manager"
on public.tribe_posts for update
to authenticated
using (author_id = auth.uid() or public.is_tribe_manager(tribe_id))
with check (author_id = auth.uid() or public.is_tribe_manager(tribe_id));

drop policy if exists "tribe_comments_select_authenticated" on public.tribe_comments;
create policy "tribe_comments_select_authenticated"
on public.tribe_comments for select
to authenticated
using (
  exists (
    select 1
    from public.tribe_posts p
    where p.id = post_id
      and p.deleted_at is null
  )
);

drop policy if exists "tribe_comments_insert_authenticated_author" on public.tribe_comments;
create policy "tribe_comments_insert_authenticated_author"
on public.tribe_comments for insert
to authenticated
with check (
  author_id = auth.uid()
  and exists (
    select 1
    from public.tribe_posts p
    where p.id = post_id
      and p.deleted_at is null
  )
);

drop policy if exists "tribe_comments_update_author_or_manager" on public.tribe_comments;
create policy "tribe_comments_update_author_or_manager"
on public.tribe_comments for update
to authenticated
using (
  author_id = auth.uid()
  or exists (
    select 1
    from public.tribe_posts p
    where p.id = post_id
      and public.is_tribe_manager(p.tribe_id)
  )
)
with check (
  author_id = auth.uid()
  or exists (
    select 1
    from public.tribe_posts p
    where p.id = post_id
      and public.is_tribe_manager(p.tribe_id)
  )
);
