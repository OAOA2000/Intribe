do $$
declare
  admin_user_id uuid := '0ca47dea-f602-40e5-a724-922466895ec1';
  member_user_id uuid := 'd540665d-3a25-4856-a99b-c4cf32e1d02a';
  guitar_tribe_id uuid;
  dance_tribe_id uuid;
  guitar_post_id uuid;
  dance_admin_post_id uuid;
  dance_member_post_id uuid;
  comment_id uuid;
  reply_id uuid;
begin
  select id into guitar_tribe_id from public.tribes where name = '吉他社' limit 1;
  select id into dance_tribe_id from public.tribes where name = '舞蹈社' limit 1;

  if guitar_tribe_id is null then
    raise exception 'Tribe not found: 吉他社';
  end if;

  if dance_tribe_id is null then
    raise exception 'Tribe not found: 舞蹈社';
  end if;

  insert into public.profiles (id, email, display_name, major, bio)
  values
    (admin_user_id, '1253627036@qq.com', '1253627036', '校园活动组织者', '喜欢把兴趣活动组织成大家都愿意参与的现场。'),
    (member_user_id, '1403264497@qq.com', '1403264497', '软件工程', '正在探索音乐、舞蹈和校园社群协作。')
  on conflict (id) do update
  set
    email = excluded.email,
    display_name = excluded.display_name,
    major = excluded.major,
    bio = excluded.bio;

  insert into public.tribe_members (tribe_id, user_id, role)
  values
    (guitar_tribe_id, admin_user_id, 'admin'),
    (guitar_tribe_id, member_user_id, 'member'),
    (dance_tribe_id, admin_user_id, 'admin'),
    (dance_tribe_id, member_user_id, 'member')
  on conflict (tribe_id, user_id) do update
  set role = excluded.role;

  select id into guitar_post_id
  from public.tribe_posts
  where tribe_id = guitar_tribe_id
    and title = '本周五晚自习后，一起做一次开放弹唱练习'
    and author_id = admin_user_id
    and deleted_at is null
  limit 1;

  if guitar_post_id is null then
    insert into public.tribe_posts (tribe_id, author_id, title, content, created_at)
    values (
      guitar_tribe_id,
      admin_user_id,
      '本周五晚自习后，一起做一次开放弹唱练习',
      '最近有不少同学说想练弹唱，但一个人练容易卡在节奏和换和弦上。本周五 19:30 我们在学生活动中心 203 做一次开放练习：前半小时一起热手和复习 C、G、Am、F，后半段自由组队练一首完整歌曲。新手可以带谱来问，已经会弹的同学也可以帮忙听节奏和扫弦。',
      now() - interval '2 days'
    )
    returning id into guitar_post_id;
  end if;

  select id into comment_id
  from public.tribe_comments
  where post_id = guitar_post_id
    and author_id = member_user_id
    and content = '我想参加！目前 F 和弦切换还不太稳，可以现场请大家帮我看一下手型吗？'
    and deleted_at is null
  limit 1;

  if comment_id is null then
    insert into public.tribe_comments (post_id, author_id, content, created_at)
    values (
      guitar_post_id,
      member_user_id,
      '我想参加！目前 F 和弦切换还不太稳，可以现场请大家帮我看一下手型吗？',
      now() - interval '1 day 21 hours'
    )
    returning id into comment_id;
  end if;

  if not exists (
    select 1 from public.tribe_comments
    where post_id = guitar_post_id
      and parent_id = comment_id
      and author_id = admin_user_id
      and content = '可以，F 和弦我们会专门留十分钟做分解练习。你也可以先试试小横按版本，现场再慢慢过渡。'
      and deleted_at is null
  ) then
    insert into public.tribe_comments (post_id, author_id, parent_id, content, created_at)
    values (
      guitar_post_id,
      admin_user_id,
      comment_id,
      '可以，F 和弦我们会专门留十分钟做分解练习。你也可以先试试小横按版本，现场再慢慢过渡。',
      now() - interval '1 day 20 hours'
    );
  end if;

  if not exists (
    select 1 from public.tribe_comments
    where post_id = guitar_post_id
      and author_id = admin_user_id
      and content = '另外这次会准备几份常用和弦速查表，大家不用担心跟不上。'
      and deleted_at is null
  ) then
    insert into public.tribe_comments (post_id, author_id, content, created_at)
    values (
      guitar_post_id,
      admin_user_id,
      '另外这次会准备几份常用和弦速查表，大家不用担心跟不上。',
      now() - interval '1 day 19 hours'
    );
  end if;

  select id into dance_admin_post_id
  from public.tribe_posts
  where tribe_id = dance_tribe_id
    and title = '校园开放日舞台招募：想组一个 3 分钟展示节目'
    and author_id = admin_user_id
    and deleted_at is null
  limit 1;

  if dance_admin_post_id is null then
    insert into public.tribe_posts (tribe_id, author_id, title, content, created_at)
    values (
      dance_tribe_id,
      admin_user_id,
      '校园开放日舞台招募：想组一个 3 分钟展示节目',
      '下个月校园开放日会有一个小舞台，我们计划准备一支 3 分钟左右的展示节目。风格暂定为爵士和街舞融合，重点不是难度，而是整齐度和感染力。欢迎有舞台经验的同学来做主舞，也欢迎第一次上台的同学加入队形部分。这个帖子用来收集大家的时间、擅长风格和选曲建议。',
      now() - interval '3 days'
    )
    returning id into dance_admin_post_id;
  end if;

  select id into comment_id
  from public.tribe_comments
  where post_id = dance_admin_post_id
    and author_id = member_user_id
    and content = '我可以参加队形部分，周二和周四晚上都有空。选曲能不能偏明快一点，适合开放日气氛？'
    and deleted_at is null
  limit 1;

  if comment_id is null then
    insert into public.tribe_comments (post_id, author_id, content, created_at)
    values (
      dance_admin_post_id,
      member_user_id,
      '我可以参加队形部分，周二和周四晚上都有空。选曲能不能偏明快一点，适合开放日气氛？',
      now() - interval '2 days 22 hours'
    )
    returning id into comment_id;
  end if;

  select id into reply_id
  from public.tribe_comments
  where post_id = dance_admin_post_id
    and parent_id = comment_id
    and author_id = admin_user_id
    and content = '可以，我们优先选节奏清楚、段落变化明显的歌。周四晚先试两版编排，你可以来帮忙判断哪版更适合新手加入。'
    and deleted_at is null
  limit 1;

  if reply_id is null then
    insert into public.tribe_comments (post_id, author_id, parent_id, content, created_at)
    values (
      dance_admin_post_id,
      admin_user_id,
      comment_id,
      '可以，我们优先选节奏清楚、段落变化明显的歌。周四晚先试两版编排，你可以来帮忙判断哪版更适合新手加入。',
      now() - interval '2 days 21 hours'
    )
    returning id into reply_id;
  end if;

  if not exists (
    select 1 from public.tribe_comments
    where post_id = dance_admin_post_id
      and parent_id = reply_id
      and author_id = member_user_id
      and content = '没问题，我也可以负责记录大家的可用时间，后面整理成排练表。'
      and deleted_at is null
  ) then
    insert into public.tribe_comments (post_id, author_id, parent_id, content, created_at)
    values (
      dance_admin_post_id,
      member_user_id,
      reply_id,
      '没问题，我也可以负责记录大家的可用时间，后面整理成排练表。',
      now() - interval '2 days 20 hours'
    );
  end if;

  select id into dance_member_post_id
  from public.tribe_posts
  where tribe_id = dance_tribe_id
    and title = '想开一个零基础律动小练习，有人一起吗？'
    and author_id = member_user_id
    and deleted_at is null
  limit 1;

  if dance_member_post_id is null then
    insert into public.tribe_posts (tribe_id, author_id, title, content, created_at)
    values (
      dance_tribe_id,
      member_user_id,
      '想开一个零基础律动小练习，有人一起吗？',
      '我发现很多同学想来舞蹈社，但担心自己没有基础。其实可以先从最简单的拍点、重心转移和手臂控制开始。我想每周找一个晚上做 40 分钟的小练习，不追求成品舞，主要是让大家敢动起来。如果有同学也想从零开始，可以在评论里说一下想练的时间段。',
      now() - interval '1 day 6 hours'
    )
    returning id into dance_member_post_id;
  end if;

  select id into comment_id
  from public.tribe_comments
  where post_id = dance_member_post_id
    and author_id = admin_user_id
    and content = '这个方向很好，社团可以支持你做成固定新手练习。建议第一次就选 3 个动作循环，降低门槛。'
    and deleted_at is null
  limit 1;

  if comment_id is null then
    insert into public.tribe_comments (post_id, author_id, content, created_at)
    values (
      dance_member_post_id,
      admin_user_id,
      '这个方向很好，社团可以支持你做成固定新手练习。建议第一次就选 3 个动作循环，降低门槛。',
      now() - interval '1 day 4 hours'
    )
    returning id into comment_id;
  end if;

  if not exists (
    select 1 from public.tribe_comments
    where post_id = dance_member_post_id
      and parent_id = comment_id
      and author_id = member_user_id
      and content = '收到！我先把第一期设计成拍点练习、肩胸分离和简单步伐组合，结束后再问大家想继续练什么。'
      and deleted_at is null
  ) then
    insert into public.tribe_comments (post_id, author_id, parent_id, content, created_at)
    values (
      dance_member_post_id,
      member_user_id,
      comment_id,
      '收到！我先把第一期设计成拍点练习、肩胸分离和简单步伐组合，结束后再问大家想继续练什么。',
      now() - interval '1 day 3 hours'
    );
  end if;

  if not exists (
    select 1 from public.tribe_comments
    where post_id = dance_member_post_id
      and author_id = member_user_id
      and content = '如果大家方便的话，我倾向周三 20:00 在形体房先试一次。'
      and deleted_at is null
  ) then
    insert into public.tribe_comments (post_id, author_id, content, created_at)
    values (
      dance_member_post_id,
      member_user_id,
      '如果大家方便的话，我倾向周三 20:00 在形体房先试一次。',
      now() - interval '1 day 2 hours'
    );
  end if;
end $$;
