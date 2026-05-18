from .common import current_user_email, current_user_id, db
from ..utils.validators import pick_allowed_fields


PROFILE_FIELDS = ("display_name", "major", "avatar_url", "bio")


def get_or_create_my_profile():
    user_id = current_user_id()
    rows = db().select("profiles", {"id": f"eq.{user_id}", "select": "*", "limit": "1"})
    if rows:
        return rows[0]

    payload = {
        "id": user_id,
        "email": current_user_email(),
        "display_name": current_user_email().split("@")[0] if current_user_email() else "新同学",
    }
    created = db().insert("profiles", payload)
    return created[0] if created else payload


def update_my_profile(data):
    user_id = current_user_id()
    payload = pick_allowed_fields(data, PROFILE_FIELDS)
    if not payload:
        return get_or_create_my_profile()

    rows = db().update("profiles", payload, {"id": f"eq.{user_id}"})
    return rows[0] if rows else get_or_create_my_profile()
