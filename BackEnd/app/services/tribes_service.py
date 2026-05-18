from .common import current_user_id, db, sanitize_search, single_or_404
from ..supabase_client import get_supabase_client
from ..utils.errors import APIError
from ..utils.validators import pick_allowed_fields, require_fields


TRIBE_FIELDS = ("name", "description", "category", "icon")


def _service_db():
    return get_supabase_client(use_service_role=True)


def _add_counts_to_tribes(tribes):
    if not tribes:
        return tribes

    tribe_ids = [tribe["id"] for tribe in tribes]
    id_filter = f"in.({','.join(tribe_ids)})"

    members_by_tribe = {tribe_id: set() for tribe_id in tribe_ids}
    events_by_tribe = {tribe_id: 0 for tribe_id in tribe_ids}

    for tribe in tribes:
        if tribe.get("owner_id"):
            members_by_tribe[tribe["id"]].add(tribe["owner_id"])

    memberships = _service_db().select(
        "tribe_members",
        {"tribe_id": id_filter, "select": "tribe_id,user_id"},
    )
    for membership in memberships:
        members_by_tribe.setdefault(membership["tribe_id"], set()).add(membership["user_id"])

    event_rows = _service_db().select(
        "events",
        {"tribe_id": id_filter, "select": "tribe_id,id"},
    )
    for event in event_rows:
        events_by_tribe[event["tribe_id"]] = events_by_tribe.get(event["tribe_id"], 0) + 1

    for tribe in tribes:
        tribe["member_count"] = len(members_by_tribe.get(tribe["id"], set()))
        tribe["event_count"] = events_by_tribe.get(tribe["id"], 0)

    return tribes


def list_tribes(category=None, search=None):
    params = {"select": "*,tribe_members(id,user_id,role),events(id,status)", "order": "created_at.desc"}
    if category:
        params["category"] = f"eq.{category}"

    term = sanitize_search(search)
    if term:
        params["or"] = f"(name.ilike.*{term}*,description.ilike.*{term}*,category.ilike.*{term}*)"

    return _add_counts_to_tribes(db().select("tribes", params))


def get_my_tribes():
    user_id = current_user_id()
    memberships = db().select(
        "tribe_members",
        {
            "user_id": f"eq.{user_id}",
            "select": "id,role,joined_at,tribes(*)",
            "order": "joined_at.desc",
        },
    )
    tribes = [item["tribes"] for item in memberships if item.get("tribes")]
    _add_counts_to_tribes(tribes)
    return memberships


def get_tribe_detail(tribe_id):
    rows = db().select(
        "tribes",
        {
            "id": f"eq.{tribe_id}",
            "select": "*,tribe_members(id,user_id,role,joined_at),events(*)",
            "limit": "1",
        },
    )
    return single_or_404(_add_counts_to_tribes(rows), "Tribe not found")


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
