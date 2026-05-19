import json
from datetime import datetime, time, timedelta, timezone

from .ai_context_service import get_current_profile_context
from .ai_prompt_service import activity_copy_prompt, post_summary_prompt, recommendations_prompt, tribe_digest_prompt
from .common import current_user_email, current_user_id, db, single_or_404
from .llm_service import invoke_json
from ..utils.errors import APIError
from ..utils.validators import require_fields


def _clean_text(value, max_length=2000):
    if value in (None, ""):
        return ""
    text = str(value).strip()
    if len(text) > max_length:
        raise APIError("VALIDATION_ERROR", f"Input text is too long. Max length is {max_length}", 400)
    return text


def generate_activity_copy(data):
    require_fields(data, ("title",))

    variables = {
        "title": _clean_text(data.get("title"), 120),
        "description": _clean_text(data.get("description") or "精彩校园活动"),
        "location": _clean_text(data.get("location") or "校园内", 120),
        "start_time": _clean_text(data.get("start_time") or data.get("time") or "近期", 120),
        "profile": get_current_profile_context(),
    }

    return invoke_json(
        activity_copy_prompt(),
        variables,
        required_fields=("copy",),
        defaults={"copy": ""},
        temperature=0.4,
    )


def _parse_datetime(value, field_name):
    if not value:
        raise APIError("VALIDATION_ERROR", f"Missing required field: {field_name}", 400)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise APIError("VALIDATION_ERROR", f"{field_name} must be an ISO datetime", 400) from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_optional_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _today_range():
    now = datetime.now(timezone.utc).astimezone()
    start = datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    end = datetime.combine(now.date(), time.max, tzinfo=now.tzinfo)
    return start, end


def _resolve_time_range(data):
    if data.get("start_time") or data.get("end_time"):
        start = _parse_datetime(data.get("start_time"), "start_time")
        end = _parse_datetime(data.get("end_time"), "end_time")
    else:
        time_range = data.get("time_range") or "today"
        if time_range != "today":
            raise APIError("VALIDATION_ERROR", "time_range currently supports only: today", 400)
        start, end = _today_range()

    if end <= start:
        raise APIError("VALIDATION_ERROR", "end_time must be after start_time", 400)
    if end - start > timedelta(days=14):
        raise APIError("VALIDATION_ERROR", "time range cannot exceed 14 days", 400)
    return start, end


def _iso(value):
    return value.isoformat()


def _is_between(value, start, end):
    parsed = _parse_optional_datetime(value)
    return bool(parsed and start <= parsed <= end)


def _text(value, max_length=160):
    text = " ".join(str(value or "").split())
    if len(text) > max_length:
        return f"{text[:max_length].rstrip()}..."
    return text


def _normalize_profile_name(profile, fallback="校园同学"):
    if not profile:
        return fallback
    return profile.get("display_name") or profile.get("email") or fallback


def _ensure_tribe_access(tribe_id):
    user_id = current_user_id()
    membership = db().select(
        "tribe_members",
        {
            "tribe_id": f"eq.{tribe_id}",
            "user_id": f"eq.{user_id}",
            "select": "id,role",
            "limit": "1",
        },
    )
    if not membership:
        raise APIError("FORBIDDEN", "You do not have permission to summarize this tribe", 403)

    tribe = db().select(
        "tribes",
        {"id": f"eq.{tribe_id}", "select": "id,name,category,description", "limit": "1"},
    )
    return single_or_404(tribe, "Tribe not found")


def _load_digest_rows(tribe_id, user_id, start, end):
    start_iso = _iso(start)
    end_iso = _iso(end)

    messages = db().select(
        "messages",
        {
            "user_id": f"eq.{user_id}",
            "tribe_id": f"eq.{tribe_id}",
            "and": f"(created_at.gte.{start_iso},created_at.lte.{end_iso})",
            "select": "id,title,content,type,is_read,post_id,event_id,created_at",
            "order": "created_at.desc",
            "limit": "50",
        },
    )
    messages = [row for row in messages if _is_between(row.get("created_at"), start, end)][:20]

    posts = db().select(
        "tribe_posts",
        {
            "tribe_id": f"eq.{tribe_id}",
            "deleted_at": "is.null",
            "and": f"(updated_at.gte.{start_iso},updated_at.lte.{end_iso})",
            "select": "id,title,content,created_at,updated_at",
            "order": "updated_at.desc",
            "limit": "50",
        },
    )
    posts = [row for row in posts if _is_between(row.get("updated_at"), start, end)][:20]

    all_posts = db().select(
        "tribe_posts",
        {
            "tribe_id": f"eq.{tribe_id}",
            "deleted_at": "is.null",
            "select": "id,title",
            "limit": "100",
        },
    )
    post_titles = {post["id"]: post.get("title") for post in all_posts}
    post_ids = list(post_titles.keys())
    comments = []
    if post_ids:
        comments = db().select(
            "tribe_comments",
            {
                "post_id": f"in.({','.join(post_ids)})",
                "deleted_at": "is.null",
                "and": f"(created_at.gte.{start_iso},created_at.lte.{end_iso})",
                "select": "id,post_id,parent_id,content,created_at",
                "order": "created_at.desc",
                "limit": "80",
            },
        )
        comments = [row for row in comments if _is_between(row.get("created_at"), start, end)][:30]
        for comment in comments:
            comment["post_title"] = post_titles.get(comment.get("post_id")) or "部落帖子"

    event_window_end = end + timedelta(days=7)
    events = db().select(
        "events",
        {
            "tribe_id": f"eq.{tribe_id}",
            "status": "neq.cancelled",
            "select": "id,title,description,location,start_time,status,updated_at",
            "order": "start_time.asc",
            "limit": "30",
        },
    )
    events = [
        event
        for event in events
        if _event_is_relevant(event, start, end, event_window_end)
    ][:12]

    return {
        "messages": messages,
        "posts": posts,
        "comments": comments,
        "events": events,
    }


def _event_is_relevant(event, start, end, upcoming_end):
    updated_at = _parse_optional_datetime(event.get("updated_at"))
    start_time = _parse_optional_datetime(event.get("start_time"))
    return bool((updated_at and start <= updated_at <= end) or (start_time and start <= start_time <= upcoming_end))


def _compress_digest_context(rows):
    return {
        "messages": [
            {
                "id": item.get("id"),
                "title": _text(item.get("title") or "部落消息", 80),
                "content": _text(item.get("content"), 180),
                "is_unread": not item.get("is_read"),
                "created_at": item.get("created_at"),
                "target": item.get("post_id") or item.get("event_id"),
            }
            for item in rows["messages"][:12]
        ],
        "posts": [
            {
                "id": item.get("id"),
                "title": _text(item.get("title"), 80),
                "preview": _text(item.get("content"), 180),
                "updated_at": item.get("updated_at"),
            }
            for item in rows["posts"][:12]
        ],
        "comments": [
            {
                "id": item.get("id"),
                "post_id": item.get("post_id"),
                "post_title": _text(item.get("post_title"), 80),
                "kind": "reply" if item.get("parent_id") else "comment",
                "content": _text(item.get("content"), 180),
                "created_at": item.get("created_at"),
            }
            for item in rows["comments"][:16]
        ],
        "events": [
            {
                "id": item.get("id"),
                "title": _text(item.get("title"), 80),
                "description": _text(item.get("description"), 140),
                "location": _text(item.get("location"), 80),
                "start_time": item.get("start_time"),
                "status": item.get("status"),
            }
            for item in rows["events"][:10]
        ],
    }


def _has_digest_context(context):
    return any(context[key] for key in ("messages", "posts", "comments", "events"))


def _context_target_ids(context):
    target_ids = set()
    for message in context["messages"]:
        target_ids.add(message.get("id"))
        target_ids.add(message.get("target"))
    for post in context["posts"]:
        target_ids.add(post.get("id"))
    for comment in context["comments"]:
        target_ids.add(comment.get("id"))
        target_ids.add(comment.get("post_id"))
    for event in context["events"]:
        target_ids.add(event.get("id"))
    return {str(target_id) for target_id in target_ids if target_id}


def _empty_digest():
    return {
        "summary": "暂无明显动态，可以晚点再来看看部落里的新讨论。",
        "highlights": [],
        "todos": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _normalize_digest_output(result, allowed_target_ids=None):
    highlights = result.get("highlights")
    todos = result.get("todos")
    if not isinstance(highlights, list):
        highlights = []
    if not isinstance(todos, list):
        todos = []

    normalized = {
        "summary": str(result.get("summary") or "暂无明显动态。").strip(),
        "highlights": [],
        "todos": [str(todo).strip() for todo in todos if str(todo or "").strip()][:6],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    allowed_types = {"post", "comment", "event", "todo"}
    allowed_targets = {"post", "event", "message", None}
    for item in highlights[:8]:
        if not isinstance(item, dict):
            continue
        target_type = item.get("target_type")
        if target_type == "null":
            target_type = None
        target_id = item.get("target_id") or None
        if target_id and allowed_target_ids is not None and str(target_id) not in allowed_target_ids:
            target_id = None
            target_type = None
        normalized["highlights"].append(
            {
                "type": item.get("type") if item.get("type") in allowed_types else "todo",
                "title": _text(item.get("title") or "部落动态", 80),
                "description": _text(item.get("description"), 180),
                "target_type": target_type if target_type in allowed_targets else None,
                "target_id": target_id,
            }
        )
    return normalized


def generate_tribe_digest(data):
    require_fields(data, ("tribe_id",))
    tribe_id = str(data.get("tribe_id")).strip()
    start, end = _resolve_time_range(data)
    user_id = current_user_id()
    tribe = _ensure_tribe_access(tribe_id)
    rows = _load_digest_rows(tribe_id, user_id, start, end)
    context = _compress_digest_context(rows)

    if not _has_digest_context(context):
        return _empty_digest()

    try:
        result = invoke_json(
            tribe_digest_prompt(),
            {
                "tribe": _text(tribe.get("name") or "兴趣部落", 80),
                "time_range": f"{_iso(start)} 至 {_iso(end)}",
                "context": json.dumps(context, ensure_ascii=False),
            },
            required_fields=("summary",),
            defaults={"summary": "", "highlights": [], "todos": []},
            temperature=0.3,
        )
    except APIError as exc:
        if exc.code.startswith("LLM_"):
            raise APIError(exc.code, "AI 总结暂时生成失败，请稍后重试。", exc.status_code) from exc
        raise

    return _normalize_digest_output(result, allowed_target_ids=_context_target_ids(context))


def _load_visible_post_for_summary(post_id):
    rows = db().select(
        "tribe_posts",
        {
            "id": f"eq.{post_id}",
            "deleted_at": "is.null",
            "select": "id,title,content,author_id,created_at,tribe_id,tribes(id,name,owner_id)",
            "limit": "1",
        },
    )
    return single_or_404(rows, "Post not found")


def _ensure_post_summary_access(post):
    user_id = current_user_id()
    tribe = post.get("tribes") or {}
    if tribe.get("owner_id") == user_id:
        return

    membership = db().select(
        "tribe_members",
        {
            "tribe_id": f"eq.{post.get('tribe_id')}",
            "user_id": f"eq.{user_id}",
            "select": "id,role",
            "limit": "1",
        },
    )
    if not membership:
        raise APIError("FORBIDDEN", "You do not have permission to summarize this post", 403)


def _load_post_summary_comments(post_id):
    return db().select(
        "tribe_comments",
        {
            "post_id": f"eq.{post_id}",
            "deleted_at": "is.null",
            "select": "id,parent_id,author_id,content,created_at",
            "order": "created_at.asc",
            "limit": "160",
        },
    )


def _load_visible_profiles(author_ids):
    if not author_ids:
        return {}
    rows = db().select(
        "profiles",
        {
            "id": f"in.({','.join(author_ids)})",
            "select": "id,email,display_name",
            "limit": "200",
        },
    )
    return {row["id"]: row for row in rows if row.get("id")}


def _comment_depth(comment_id, comments_by_id):
    depth = 0
    current = comments_by_id.get(comment_id)
    seen = set()
    while current and current.get("parent_id") and current.get("parent_id") not in seen:
        seen.add(current["parent_id"])
        parent = comments_by_id.get(current["parent_id"])
        if not parent:
            break
        depth += 1
        current = parent
    return min(depth, 4)


def _compress_post_comments(comments, profiles_by_id, max_total_chars=12000):
    if not comments:
        return "暂无评论。"

    comments_by_id = {comment["id"]: comment for comment in comments}
    lines = []
    total = 0
    for index, comment in enumerate(comments[:120], start=1):
        author = _normalize_profile_name(profiles_by_id.get(comment.get("author_id")))
        kind = "回复" if comment.get("parent_id") else "评论"
        indent = "  " * _comment_depth(comment.get("id"), comments_by_id)
        content = _text(comment.get("content"), 360)
        line = f"{indent}{index}. {author}（{kind}，{comment.get('created_at') or '时间未知'}）：{content}"
        if total + len(line) > max_total_chars:
            lines.append("...（后续评论已因长度限制省略）")
            break
        lines.append(line)
        total += len(line)
    return "\n".join(lines)


def _normalize_string_list(value, limit=8, max_length=140):
    if not isinstance(value, list):
        return []
    return [_text(item, max_length) for item in value if str(item or "").strip()][:limit]


def _parse_limit(value, default=5, maximum=10):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise APIError("VALIDATION_ERROR", "Recommendation limits must be integers", 400) from exc
    if parsed < 0:
        raise APIError("VALIDATION_ERROR", "Recommendation limits cannot be negative", 400)
    return min(parsed, maximum)


def _load_current_profile_for_recommendations(user_id):
    rows = db().select(
        "profiles",
        {
            "id": f"eq.{user_id}",
            "select": "id,email,display_name,major,bio",
            "limit": "1",
        },
    )
    if rows:
        return rows[0]
    return {
        "id": user_id,
        "email": current_user_email(),
        "display_name": "",
        "major": "",
        "bio": "",
    }


def _load_joined_tribe_ids(user_id):
    rows = db().select(
        "tribe_members",
        {
            "user_id": f"eq.{user_id}",
            "select": "tribe_id",
            "limit": "500",
        },
    )
    return {row.get("tribe_id") for row in rows if row.get("tribe_id")}


def _load_registered_event_ids(user_id):
    rows = db().select(
        "event_registrations",
        {
            "user_id": f"eq.{user_id}",
            "status": "neq.cancelled",
            "select": "event_id",
            "limit": "500",
        },
    )
    return {row.get("event_id") for row in rows if row.get("event_id")}


def _load_recommendation_tribes(joined_tribe_ids):
    rows = db().select(
        "tribes",
        {
            "select": "id,name,description,category,tribe_members(id,user_id)",
            "order": "created_at.desc",
            "limit": "80",
        },
    )
    candidates = []
    for row in rows:
        if row.get("id") in joined_tribe_ids:
            continue
        members = row.get("tribe_members") if isinstance(row.get("tribe_members"), list) else []
        candidates.append(
            {
                "id": row.get("id"),
                "name": _text(row.get("name"), 80),
                "description": _text(row.get("description"), 240),
                "category": _text(row.get("category"), 40),
                "member_count": len(members),
            }
        )
    return [item for item in candidates if item.get("id")]


def _load_recommendation_events(registered_event_ids):
    rows = db().select(
        "events",
        {
            "status": "neq.cancelled",
            "select": "id,title,description,location,start_time,status,tribe_id,tribes(id,name,category)",
            "order": "start_time.asc",
            "limit": "100",
        },
    )
    candidates = []
    for row in rows:
        if row.get("id") in registered_event_ids:
            continue
        tribe = row.get("tribes") if isinstance(row.get("tribes"), dict) else {}
        candidates.append(
            {
                "id": row.get("id"),
                "title": _text(row.get("title"), 100),
                "description": _text(row.get("description"), 260),
                "location": _text(row.get("location"), 80),
                "start_time": row.get("start_time"),
                "status": row.get("status"),
                "tribe_id": row.get("tribe_id"),
                "tribe_name": _text(tribe.get("name"), 80),
                "tribe_category": _text(tribe.get("category"), 40),
            }
        )
    return [item for item in candidates if item.get("id")]


def _profile_keyword_text(profile):
    return " ".join(
        str(profile.get(field) or "").strip()
        for field in ("display_name", "major", "bio")
        if str(profile.get(field) or "").strip()
    )


def _extract_match_tags(profile, item, fields):
    tags = []
    profile_text = _profile_keyword_text(profile)
    profile_parts = [part for part in profile_text.replace("，", " ").replace(",", " ").split() if len(part) >= 2]
    item_text = " ".join(str(item.get(field) or "") for field in fields)
    category = item.get("category") or item.get("tribe_category")
    if category:
        tags.append(str(category))
    major = profile.get("major")
    if major and (major in item_text or any(word in item_text for word in str(major).split())):
        tags.append(str(major))
    for part in profile_parts:
        if part in item_text and part not in tags:
            tags.append(part)
    return tags[:4]


def _heuristic_score(profile, item, fields):
    score = 0.35
    profile_text = _profile_keyword_text(profile)
    item_text = " ".join(str(item.get(field) or "") for field in fields)
    if profile.get("bio"):
        score += 0.1
    if profile.get("major") and profile.get("major") in item_text:
        score += 0.25
    for word in profile_text.replace("，", " ").replace(",", " ").split():
        if len(word) >= 2 and word in item_text:
            score += 0.08
    if item.get("status") in ("recruiting", "ongoing"):
        score += 0.08
    if item.get("member_count"):
        score += min(float(item["member_count"]) / 100, 0.08)
    return round(max(0, min(score, 0.95)), 2)


def _fallback_recommendations(profile, tribes, events, limit_tribes, limit_events):
    has_bio = bool(str(profile.get("bio") or "").strip())
    tribe_ranked = sorted(
        tribes,
        key=lambda item: _heuristic_score(profile, item, ("name", "description", "category")),
        reverse=True,
    )
    event_ranked = sorted(
        events,
        key=lambda item: _heuristic_score(
            profile,
            item,
            ("title", "description", "location", "status", "tribe_name", "tribe_category"),
        ),
        reverse=True,
    )
    basis_note = (
        "已结合你的个人简介、专业和平台可见内容生成推荐。"
        if has_bio
        else "你的个人简介暂未填写，完善个人简介可提升推荐质量；本次主要基于专业、部落分类和近期活动进行弱推荐。"
    )
    return {
        "profile_basis": {
            "used_bio": has_bio,
            "used_interests": False,
            "notes": basis_note,
        },
        "recommended_tribes": [
            {
                "tribe_id": item["id"],
                "name": item.get("name") or "兴趣部落",
                "reason": (
                    f"该部落的「{item.get('category') or item.get('name') or '兴趣方向'}」方向与你的资料信息有潜在关联。"
                    if has_bio or profile.get("major")
                    else f"该部落属于「{item.get('category') or '校园兴趣'}」方向，可作为完善资料前的探索选择。"
                ),
                "match_tags": _extract_match_tags(profile, item, ("name", "description", "category")),
                "score": _heuristic_score(profile, item, ("name", "description", "category")),
            }
            for item in tribe_ranked[:limit_tribes]
        ],
        "recommended_events": [
            {
                "event_id": item["id"],
                "title": item.get("title") or "校园活动",
                "reason": (
                    f"活动内容与「{item.get('tribe_category') or item.get('title') or '你的兴趣'}」相关，且当前状态适合关注。"
                    if has_bio or profile.get("major")
                    else "该活动来自你可见的近期活动列表，可先了解并通过完善简介提升后续匹配度。"
                ),
                "match_tags": _extract_match_tags(
                    profile,
                    item,
                    ("title", "description", "location", "status", "tribe_name", "tribe_category"),
                ),
                "score": _heuristic_score(
                    profile,
                    item,
                    ("title", "description", "location", "status", "tribe_name", "tribe_category"),
                ),
            }
            for item in event_ranked[:limit_events]
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _clamp_score(value):
    try:
        return round(max(0, min(float(value), 1)), 2)
    except (TypeError, ValueError):
        return 0.5


def _normalize_recommendations_output(result, profile, tribes, events, limit_tribes, limit_events):
    fallback = _fallback_recommendations(profile, tribes, events, limit_tribes, limit_events)
    tribe_by_id = {item["id"]: item for item in tribes}
    event_by_id = {item["id"]: item for item in events}
    has_bio = bool(str(profile.get("bio") or "").strip())

    basis = result.get("profile_basis") if isinstance(result.get("profile_basis"), dict) else {}
    normalized = {
        "profile_basis": {
            "used_bio": bool(basis.get("used_bio")) and has_bio,
            "used_interests": bool(basis.get("used_interests")),
            "notes": _text(basis.get("notes") or fallback["profile_basis"]["notes"], 220),
        },
        "recommended_tribes": [],
        "recommended_events": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if limit_tribes > 0:
        for item in result.get("recommended_tribes") if isinstance(result.get("recommended_tribes"), list) else []:
            if not isinstance(item, dict):
                continue
            tribe = tribe_by_id.get(item.get("tribe_id"))
            if not tribe:
                continue
            normalized["recommended_tribes"].append(
                {
                    "tribe_id": tribe["id"],
                    "name": tribe.get("name") or _text(item.get("name"), 80),
                    "reason": _text(item.get("reason") or "该部落与你的资料信息相关。", 220),
                    "match_tags": _normalize_string_list(item.get("match_tags"), limit=5, max_length=40),
                    "score": _clamp_score(item.get("score")),
                }
            )
            if len(normalized["recommended_tribes"]) >= limit_tribes:
                break

    if limit_events > 0:
        for item in result.get("recommended_events") if isinstance(result.get("recommended_events"), list) else []:
            if not isinstance(item, dict):
                continue
            event = event_by_id.get(item.get("event_id"))
            if not event:
                continue
            normalized["recommended_events"].append(
                {
                    "event_id": event["id"],
                    "title": event.get("title") or _text(item.get("title"), 100),
                    "reason": _text(item.get("reason") or "该活动与你的资料信息相关。", 220),
                    "match_tags": _normalize_string_list(item.get("match_tags"), limit=5, max_length=40),
                    "score": _clamp_score(item.get("score")),
                }
            )
            if len(normalized["recommended_events"]) >= limit_events:
                break

    if len(normalized["recommended_tribes"]) < limit_tribes:
        seen = {item["tribe_id"] for item in normalized["recommended_tribes"]}
        normalized["recommended_tribes"].extend(
            item for item in fallback["recommended_tribes"] if item["tribe_id"] not in seen
        )
        normalized["recommended_tribes"] = normalized["recommended_tribes"][:limit_tribes]

    if len(normalized["recommended_events"]) < limit_events:
        seen = {item["event_id"] for item in normalized["recommended_events"]}
        normalized["recommended_events"].extend(
            item for item in fallback["recommended_events"] if item["event_id"] not in seen
        )
        normalized["recommended_events"] = normalized["recommended_events"][:limit_events]

    if not has_bio and "完善个人简介" not in normalized["profile_basis"]["notes"]:
        normalized["profile_basis"]["notes"] = f"{normalized['profile_basis']['notes']} 完善个人简介可提升推荐质量。"
    return normalized


def generate_recommendations(data):
    data = data or {}
    limit_tribes = _parse_limit(data.get("limit_tribes"), default=5)
    limit_events = _parse_limit(data.get("limit_events"), default=5)
    user_id = current_user_id()

    profile = _load_current_profile_for_recommendations(user_id)
    joined_tribe_ids = _load_joined_tribe_ids(user_id)
    registered_event_ids = _load_registered_event_ids(user_id)
    tribes = _load_recommendation_tribes(joined_tribe_ids)
    events = _load_recommendation_events(registered_event_ids)

    if not tribes and not events:
        return {
            **_fallback_recommendations(profile, [], [], limit_tribes, limit_events),
            "recommended_tribes": [],
            "recommended_events": [],
        }

    try:
        result = invoke_json(
            recommendations_prompt(),
            {
                "profile": json.dumps(
                    {
                        "nickname": profile.get("display_name") or "",
                        "email": profile.get("email") or "",
                        "major": profile.get("major") or "",
                        "bio": profile.get("bio") or "",
                    },
                    ensure_ascii=False,
                ),
                "tribes": json.dumps(tribes, ensure_ascii=False),
                "events": json.dumps(events, ensure_ascii=False),
                "limit_tribes": limit_tribes,
                "limit_events": limit_events,
            },
            required_fields=("profile_basis", "recommended_tribes", "recommended_events"),
            defaults={"profile_basis": {}, "recommended_tribes": [], "recommended_events": []},
            temperature=0.2,
        )
    except APIError as exc:
        if exc.code.startswith("LLM_"):
            return _fallback_recommendations(profile, tribes, events, limit_tribes, limit_events)
        raise

    return _normalize_recommendations_output(result, profile, tribes, events, limit_tribes, limit_events)


def _normalize_post_summary_output(result, post, comment_count):
    threads = []
    raw_threads = result.get("discussion_threads") if isinstance(result.get("discussion_threads"), list) else []
    for item in raw_threads[:6]:
        if not isinstance(item, dict):
            continue
        topic = _text(item.get("topic") or "讨论主题", 80)
        summary = _text(item.get("summary"), 220)
        if summary:
            threads.append({"topic": topic, "summary": summary})

    return {
        "post_title": _text(result.get("post_title") or post.get("title"), 120),
        "summary": _text(result.get("summary") or "暂无可总结内容。", 500),
        "key_points": _normalize_string_list(result.get("key_points"), limit=8),
        "discussion_threads": threads,
        "open_questions": _normalize_string_list(result.get("open_questions"), limit=6),
        "action_items": _normalize_string_list(result.get("action_items"), limit=6),
        "comment_count": comment_count,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_post_summary(data):
    require_fields(data, ("post_id",))
    post_id = str(data.get("post_id")).strip()
    post = _load_visible_post_for_summary(post_id)
    _ensure_post_summary_access(post)

    comments = _load_post_summary_comments(post_id)
    author_ids = sorted(
        {
            author_id
            for author_id in [post.get("author_id"), *[comment.get("author_id") for comment in comments]]
            if author_id
        }
    )
    profiles_by_id = _load_visible_profiles(author_ids)
    post_author = _normalize_profile_name(profiles_by_id.get(post.get("author_id")))
    comments_context = _compress_post_comments(comments, profiles_by_id)

    try:
        result = invoke_json(
            post_summary_prompt(),
            {
                "post_title": _text(post.get("title"), 120),
                "post_author": post_author,
                "post_created_at": post.get("created_at") or "",
                "post_content": _text(post.get("content"), 5000),
                "comment_count": len(comments),
                "comments_context": comments_context,
            },
            required_fields=("post_title", "summary"),
            defaults={
                "post_title": post.get("title") or "",
                "summary": "",
                "key_points": [],
                "discussion_threads": [],
                "open_questions": [],
                "action_items": [],
            },
            temperature=0.2,
        )
    except APIError as exc:
        if exc.code.startswith("LLM_"):
            raise APIError(exc.code, "AI 总结暂时生成失败，请稍后重试。", exc.status_code) from exc
        raise

    return _normalize_post_summary_output(result, post, len(comments))
