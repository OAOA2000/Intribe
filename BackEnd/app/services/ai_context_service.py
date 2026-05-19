from .common import current_user_id, db, single_or_404


def get_current_profile_context():
    rows = db().select(
        "profiles",
        {
            "id": f"eq.{current_user_id()}",
            "select": "id,display_name,major,bio",
            "limit": "1",
        },
    )
    if not rows:
        return {"empty": True}

    profile = rows[0]
    return {
        "empty": False,
        "id": profile.get("id"),
        "display_name": profile.get("display_name"),
        "major": profile.get("major"),
        "bio": profile.get("bio"),
    }


def get_tribe_context(tribe_id):
    rows = db().select(
        "tribes",
        {
            "id": f"eq.{tribe_id}",
            "select": "id,name,category,description",
            "limit": "1",
        },
    )
    tribe = single_or_404(rows, "Tribe not found")
    return {
        "id": tribe.get("id"),
        "name": tribe.get("name"),
        "category": tribe.get("category"),
        "description": tribe.get("description"),
    }


def get_event_context(event_id):
    rows = db().select(
        "events",
        {
            "id": f"eq.{event_id}",
            "select": "id,tribe_id,title,description,location,start_time,status",
            "limit": "1",
        },
    )
    event = single_or_404(rows, "Event not found")
    return {
        "id": event.get("id"),
        "tribe_id": event.get("tribe_id"),
        "title": event.get("title"),
        "description": event.get("description"),
        "location": event.get("location"),
        "start_time": event.get("start_time"),
        "status": event.get("status"),
    }
