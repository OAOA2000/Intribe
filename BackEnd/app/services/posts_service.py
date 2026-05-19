from datetime import datetime, timezone

from flask import current_app

from .common import current_user_id, db, is_tribe_manager, single_or_404
from ..supabase_client import get_supabase_client
from ..utils.errors import APIError
from ..utils.validators import pick_allowed_fields, require_fields


POST_FIELDS = ("title", "content")
COMMENT_FIELDS = ("content", "parent_id")


def _service_db():
    return get_supabase_client(use_service_role=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value):
    return str(value or "").strip()


def _normalize_author(profile):
    if not profile:
        return None
    return {
        "id": profile.get("id"),
        "display_name": profile.get("display_name") or profile.get("email") or "校园同学",
        "avatar_url": profile.get("avatar_url"),
        "major": profile.get("major"),
    }


def _attach_authors(rows, author_key="author_id"):
    if not rows:
        return rows

    author_ids = sorted({row.get(author_key) for row in rows if row.get(author_key)})
    if not author_ids:
        return rows

    profiles = _service_db().select(
        "profiles",
        {
            "id": f"in.({','.join(author_ids)})",
            "select": "id,email,display_name,avatar_url,major",
        },
    )
    profiles_by_id = {profile["id"]: profile for profile in profiles}

    for row in rows:
        row["author"] = _normalize_author(profiles_by_id.get(row.get(author_key))) or {
            "id": row.get(author_key),
            "display_name": "校园同学",
            "avatar_url": None,
            "major": None,
        }
    return rows


def _create_message(payload):
    try:
        _service_db().insert("messages", payload)
    except Exception as exc:  # Notifications should not block the comment itself.
        current_app.logger.warning("Failed to create comment notification: %s", exc)


def _notify_comment_recipients(post, comment, parent_comment=None):
    actor_id = comment.get("author_id")
    actor_name = comment.get("author", {}).get("display_name") or "有同学"
    recipients = {}

    post_author_id = post.get("author_id")
    if post_author_id and post_author_id != actor_id:
        recipients[post_author_id] = {
            "title": "帖子收到新评论",
            "content": f"{actor_name} 评论了你的帖子《{post.get('title') or '部落帖子'}》",
        }

    parent_author_id = parent_comment.get("author_id") if parent_comment else None
    if parent_author_id and parent_author_id != actor_id and parent_author_id not in recipients:
        recipients[parent_author_id] = {
            "title": "评论收到新回复",
            "content": f"{actor_name} 回复了你在《{post.get('title') or '部落帖子'}》下的评论",
        }

    for user_id, message in recipients.items():
        _create_message(
            {
                "user_id": user_id,
                "tribe_id": post.get("tribe_id"),
                "post_id": post.get("id"),
                "comment_id": comment.get("id"),
                "title": message["title"],
                "content": message["content"],
                "type": "tribe",
            }
        )


def _load_post(post_id, include_deleted=False):
    params = {"id": f"eq.{post_id}", "select": "*,tribes(id,name,category,icon)", "limit": "1"}
    if not include_deleted:
        params["deleted_at"] = "is.null"
    return single_or_404(db().select("tribe_posts", params), "Post not found")


def _load_comment(comment_id):
    rows = db().select(
        "tribe_comments",
        {"id": f"eq.{comment_id}", "select": "*,tribe_posts(tribe_id)", "limit": "1"},
    )
    return single_or_404(rows, "Comment not found")


def _can_manage_post(post):
    user_id = current_user_id()
    return post.get("author_id") == user_id or is_tribe_manager(post.get("tribe_id"), user_id)


def _can_manage_comment(comment):
    user_id = current_user_id()
    tribe_id = (comment.get("tribe_posts") or {}).get("tribe_id")
    return comment.get("author_id") == user_id or is_tribe_manager(tribe_id, user_id)


def _serialize_comment(comment):
    item = dict(comment)
    item["children"] = []
    return item


def build_comment_tree(comments):
    nodes = {comment["id"]: _serialize_comment(comment) for comment in comments}
    roots = []

    for comment in comments:
        node = nodes[comment["id"]]
        parent_id = comment.get("parent_id")
        parent = nodes.get(parent_id)
        if parent:
            parent["children"].append(node)
        else:
            roots.append(node)

    return roots


def list_tribe_posts(tribe_id):
    rows = db().select(
        "tribe_posts",
        {
            "tribe_id": f"eq.{tribe_id}",
            "deleted_at": "is.null",
            "select": "*,tribes(id,name,category,icon)",
            "order": "created_at.desc",
        },
    )
    _attach_authors(rows)
    if not rows:
        return rows

    post_ids = [post["id"] for post in rows]
    comments = db().select(
        "tribe_comments",
        {
            "post_id": f"in.({','.join(post_ids)})",
            "deleted_at": "is.null",
            "select": "id,post_id,created_at",
            "order": "created_at.desc",
        },
    )
    stats = {post_id: {"comment_count": 0, "last_comment_at": None} for post_id in post_ids}
    for comment in comments:
        post_stat = stats.setdefault(comment["post_id"], {"comment_count": 0, "last_comment_at": None})
        post_stat["comment_count"] += 1
        if not post_stat["last_comment_at"] or comment["created_at"] > post_stat["last_comment_at"]:
            post_stat["last_comment_at"] = comment["created_at"]

    for post in rows:
        post.update(stats.get(post["id"], {"comment_count": 0, "last_comment_at": None}))
    return rows


def create_tribe_post(tribe_id, data):
    require_fields(data, ("title", "content"))
    payload = pick_allowed_fields(data, POST_FIELDS)
    payload["title"] = _clean_text(payload.get("title"))
    payload["content"] = _clean_text(payload.get("content"))
    require_fields(payload, ("title", "content"))
    payload["tribe_id"] = tribe_id
    payload["author_id"] = current_user_id()

    rows = db().insert("tribe_posts", payload)
    post = single_or_404(rows, "Failed to create post")
    _attach_authors([post])
    return post


def get_post_detail(post_id):
    post = _load_post(post_id)
    _attach_authors([post])
    user_id = current_user_id()
    user_can_manage_tribe = is_tribe_manager(post.get("tribe_id"), user_id)
    post["can_edit"] = post.get("author_id") == user_id
    post["can_delete"] = post["can_edit"] or user_can_manage_tribe
    comments = db().select(
        "tribe_comments",
        {
            "post_id": f"eq.{post_id}",
            "deleted_at": "is.null",
            "select": "*",
            "order": "created_at.asc",
        },
    )
    _attach_authors(comments)
    for comment in comments:
        comment["can_edit"] = comment.get("author_id") == user_id and not comment.get("deleted_at")
        comment["can_delete"] = (
            (comment.get("author_id") == user_id or user_can_manage_tribe) and not comment.get("deleted_at")
        )
    post["comments"] = build_comment_tree(comments)
    post["comment_count"] = len([comment for comment in comments if not comment.get("deleted_at")])
    return post


def update_post(post_id, data):
    post = _load_post(post_id)
    if post.get("author_id") != current_user_id():
        raise APIError("FORBIDDEN", "You do not have permission to update this post", 403)

    payload = pick_allowed_fields(data, POST_FIELDS)
    if "title" in payload:
        payload["title"] = _clean_text(payload.get("title"))
    if "content" in payload:
        payload["content"] = _clean_text(payload.get("content"))
    if not payload:
        return post
    require_fields({**post, **payload}, ("title", "content"))

    rows = db().update("tribe_posts", payload, {"id": f"eq.{post_id}"})
    updated = single_or_404(rows, "Failed to update post")
    _attach_authors([updated])
    return updated


def delete_post(post_id):
    post = _load_post(post_id)
    if not _can_manage_post(post):
        raise APIError("FORBIDDEN", "You do not have permission to delete this post", 403)

    db().update("tribe_posts", {"deleted_at": _now_iso()}, {"id": f"eq.{post_id}"})
    return {"deleted": True, "post_id": post_id}


def create_comment(post_id, data):
    post = _load_post(post_id)
    require_fields(data, ("content",))

    payload = pick_allowed_fields(data, COMMENT_FIELDS)
    payload["content"] = _clean_text(payload.get("content"))
    require_fields(payload, ("content",))
    payload["post_id"] = post_id
    payload["author_id"] = current_user_id()

    parent_id = payload.get("parent_id")
    parent_comment = None
    if parent_id:
        parent_rows = db().select(
            "tribe_comments",
            {"id": f"eq.{parent_id}", "post_id": f"eq.{post_id}", "select": "id,author_id", "limit": "1"},
        )
        parent_comment = single_or_404(parent_rows, "Parent comment not found")
    else:
        payload.pop("parent_id", None)

    rows = db().insert("tribe_comments", payload)
    comment = single_or_404(rows, "Failed to create comment")
    comment["tribe_id"] = post.get("tribe_id")
    _attach_authors([comment])
    _notify_comment_recipients(post, comment, parent_comment)
    return comment


def update_comment(comment_id, data):
    comment = _load_comment(comment_id)
    if comment.get("deleted_at"):
        raise APIError("COMMENT_DELETED", "Deleted comments cannot be updated", 400)
    if comment.get("author_id") != current_user_id():
        raise APIError("FORBIDDEN", "You do not have permission to update this comment", 403)

    payload = pick_allowed_fields(data, ("content",))
    if "content" in payload:
        payload["content"] = _clean_text(payload.get("content"))
    require_fields(payload, ("content",))

    rows = db().update("tribe_comments", payload, {"id": f"eq.{comment_id}"})
    updated = single_or_404(rows, "Failed to update comment")
    _attach_authors([updated])
    return updated


def delete_comment(comment_id):
    comment = _load_comment(comment_id)
    if not _can_manage_comment(comment):
        raise APIError("FORBIDDEN", "You do not have permission to delete this comment", 403)

    rows = db().update("tribe_comments", {"deleted_at": _now_iso()}, {"id": f"eq.{comment_id}"})
    return {"deleted": bool(rows), "comment_id": comment_id}
