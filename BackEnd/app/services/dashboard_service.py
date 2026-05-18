from datetime import datetime, timezone

from .common import current_user_id, db


def _manageable_memberships():
    return db().select(
        "tribe_members",
        {
            "user_id": f"eq.{current_user_id()}",
            "role": "in.(owner,admin)",
            "select": "tribe_id,role",
        },
    )


def _manageable_tribe_ids():
    return [item["tribe_id"] for item in _manageable_memberships()]


def get_manageable_events():
    tribe_ids = _manageable_tribe_ids()
    if not tribe_ids:
        return []

    return db().select(
        "events",
        {
            "tribe_id": f"in.({','.join(tribe_ids)})",
            "select": "*,tribes(id,name,category,icon),event_registrations(id,status)",
            "order": "start_time.asc",
        },
    )


def get_summary():
    user_id = current_user_id()
    tribe_ids = _manageable_tribe_ids()
    events = get_manageable_events()
    event_ids = [event["id"] for event in events]

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_registrations = []
    if event_ids:
        today_registrations = db().select(
            "event_registrations",
            {
                "event_id": f"in.({','.join(event_ids)})",
                "registered_at": f"gte.{today_start}",
                "status": "eq.registered",
                "select": "id",
            },
        )

    unread_messages = db().select(
        "messages",
        {"user_id": f"eq.{user_id}", "is_read": "eq.false", "select": "id"},
    )

    total_members = []
    if tribe_ids:
        total_members = db().select(
            "tribe_members",
            {"tribe_id": f"in.({','.join(tribe_ids)})", "select": "id"},
        )

    active_events = [event for event in events if event.get("status") in ("recruiting", "ongoing")]
    activity_rate = 0 if not events else round(len(active_events) / len(events), 2)

    return {
        "today_registrations": len(today_registrations),
        "new_messages": len(unread_messages),
        "activity_rate": activity_rate,
        "total_members": len(total_members),
    }
