from flask import g

from ..supabase_client import get_supabase_client
from ..utils.errors import APIError


def current_user_id():
    user_id = getattr(g, "current_user", {}).get("id")
    if not user_id:
        raise APIError("UNAUTHORIZED", "Unauthorized", 401)
    return user_id


def current_user_email():
    return getattr(g, "current_user", {}).get("email")


def db():
    return get_supabase_client()


def single_or_404(rows, message="Resource not found"):
    if not rows:
        raise APIError("NOT_FOUND", message, 404)
    return rows[0]


def sanitize_search(value):
    if not value:
        return None
    return str(value).replace("*", "").replace(",", " ").replace("(", " ").replace(")", " ").strip()


def is_tribe_manager(tribe_id, user_id=None):
    user_id = user_id or current_user_id()
    rows = db().select(
        "tribe_members",
        {
            "tribe_id": f"eq.{tribe_id}",
            "user_id": f"eq.{user_id}",
            "role": "in.(owner,admin)",
            "select": "id,role",
            "limit": "1",
        },
    )
    if rows:
        return True

    tribes = db().select("tribes", {"id": f"eq.{tribe_id}", "owner_id": f"eq.{user_id}", "select": "id", "limit": "1"})
    return bool(tribes)


def require_tribe_manager(tribe_id):
    if not is_tribe_manager(tribe_id):
        raise APIError("FORBIDDEN", "You do not have permission to manage this tribe", 403)
