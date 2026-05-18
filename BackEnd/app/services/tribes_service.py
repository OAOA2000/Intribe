from .common import current_user_id, db, sanitize_search, single_or_404
from ..utils.errors import APIError
from ..utils.validators import pick_allowed_fields, require_fields


TRIBE_FIELDS = ("name", "description", "category", "icon")


def list_tribes(category=None, search=None):
    params = {"select": "*,tribe_members(id,user_id,role),events(id,status)", "order": "created_at.desc"}
    if category:
        params["category"] = f"eq.{category}"

    term = sanitize_search(search)
    if term:
        params["or"] = f"(name.ilike.*{term}*,description.ilike.*{term}*,category.ilike.*{term}*)"

    return db().select("tribes", params)


def get_my_tribes():
    user_id = current_user_id()
    return db().select(
        "tribe_members",
        {
            "user_id": f"eq.{user_id}",
            "select": "id,role,joined_at,tribes(*)",
            "order": "joined_at.desc",
        },
    )


def get_tribe_detail(tribe_id):
    rows = db().select(
        "tribes",
        {
            "id": f"eq.{tribe_id}",
            "select": "*,tribe_members(id,user_id,role,joined_at),events(*)",
            "limit": "1",
        },
    )
    return single_or_404(rows, "Tribe not found")


def create_tribe(data):
    require_fields(data, ("name",))
    user_id = current_user_id()
    payload = pick_allowed_fields(data, TRIBE_FIELDS)
    payload["owner_id"] = user_id

    created = db().insert("tribes", payload)
    tribe = single_or_404(created, "Failed to create tribe")

    db().insert(
        "tribe_members",
        {
            "tribe_id": tribe["id"],
            "user_id": user_id,
            "role": "owner",
        },
    )
    return get_tribe_detail(tribe["id"])


def join_tribe(tribe_id):
    user_id = current_user_id()
    existing = db().select(
        "tribe_members",
        {"tribe_id": f"eq.{tribe_id}", "user_id": f"eq.{user_id}", "select": "*", "limit": "1"},
    )
    if existing:
        return existing[0]

    rows = db().insert("tribe_members", {"tribe_id": tribe_id, "user_id": user_id, "role": "member"})
    return single_or_404(rows, "Failed to join tribe")


def leave_tribe(tribe_id):
    user_id = current_user_id()
    memberships = db().select(
        "tribe_members",
        {"tribe_id": f"eq.{tribe_id}", "user_id": f"eq.{user_id}", "select": "id,role", "limit": "1"},
    )
    membership = single_or_404(memberships, "Membership not found")
    if membership.get("role") == "owner":
        raise APIError("OWNER_CANNOT_LEAVE", "Transfer ownership before leaving the tribe", 400)

    deleted = db().delete("tribe_members", {"id": f"eq.{membership['id']}"})
    return {"left": bool(deleted), "tribe_id": tribe_id}
