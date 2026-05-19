import json
from datetime import datetime, time, timedelta, timezone

from .ai_context_service import get_current_profile_context
from .ai_prompt_service import activity_copy_prompt, tribe_digest_prompt
from .common import current_user_id, db, single_or_404
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
