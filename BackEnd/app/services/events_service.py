from .common import current_user_id, db, require_tribe_manager, sanitize_search, single_or_404, is_tribe_manager
from ..utils.errors import APIError
from ..utils.validators import pick_allowed_fields, require_fields


EVENT_FIELDS = ("tribe_id", "title", "description", "location", "start_time", "status", "cover_icon")
EVENT_UPDATE_FIELDS = ("title", "description", "location", "start_time", "status", "cover_icon")


def list_events(status=None, tribe_id=None, search=None):
    params = {"select": "*,tribes(id,name,category,icon)", "order": "start_time.asc"}
    if status:
        params["status"] = f"eq.{status}"
    if tribe_id:
        params["tribe_id"] = f"eq.{tribe_id}"

    term = sanitize_search(search)
    if term:
        params["or"] = f"(title.ilike.*{term}*,description.ilike.*{term}*,location.ilike.*{term}*)"

    return db().select("events", params)


def get_event_detail(event_id):
    rows = db().select(
        "events",
        {
            "id": f"eq.{event_id}",
            "select": "*,tribes(id,name,category,icon),event_registrations(id,user_id,status,registered_at)",
            "limit": "1",
        },
    )
    return single_or_404(rows, "Event not found")


def create_event(data):
    require_fields(data, ("tribe_id", "title"))
    require_tribe_manager(data["tribe_id"])

    payload = pick_allowed_fields(data, EVENT_FIELDS)
    payload["created_by"] = current_user_id()
    payload.setdefault("status", "recruiting")

    rows = db().insert("events", payload)
    return single_or_404(rows, "Failed to create event")


def _load_event(event_id):
    rows = db().select("events", {"id": f"eq.{event_id}", "select": "*", "limit": "1"})
    return single_or_404(rows, "Event not found")


def _can_manage_event(event):
    user_id = current_user_id()
    return event.get("created_by") == user_id or is_tribe_manager(event.get("tribe_id"), user_id)


def update_event(event_id, data):
    event = _load_event(event_id)
    if not _can_manage_event(event):
        raise APIError("FORBIDDEN", "You do not have permission to update this event", 403)

    payload = pick_allowed_fields(data, EVENT_UPDATE_FIELDS)
    if not payload:
        return event

    rows = db().update("events", payload, {"id": f"eq.{event_id}"})
    return single_or_404(rows, "Failed to update event")


def delete_event(event_id):
    event = _load_event(event_id)
    if not _can_manage_event(event):
        raise APIError("FORBIDDEN", "You do not have permission to delete this event", 403)

    rows = db().delete("events", {"id": f"eq.{event_id}"})
    return {"deleted": bool(rows), "event_id": event_id}


def register_event(event_id):
    user_id = current_user_id()
    existing = db().select(
        "event_registrations",
        {"event_id": f"eq.{event_id}", "user_id": f"eq.{user_id}", "select": "*", "limit": "1"},
    )
    if existing:
        if existing[0].get("status") == "cancelled":
            rows = db().update("event_registrations", {"status": "registered"}, {"id": f"eq.{existing[0]['id']}"})
            return single_or_404(rows, "Failed to register event")
        return existing[0]

    rows = db().insert(
        "event_registrations",
        {"event_id": event_id, "user_id": user_id, "status": "registered"},
    )
    return single_or_404(rows, "Failed to register event")


def cancel_registration(event_id):
    user_id = current_user_id()
    rows = db().update(
        "event_registrations",
        {"status": "cancelled"},
        {"event_id": f"eq.{event_id}", "user_id": f"eq.{user_id}"},
    )
    return {"cancelled": bool(rows), "event_id": event_id}
