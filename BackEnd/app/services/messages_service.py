from .common import current_user_id, db
from ..utils.errors import APIError


def list_messages():
    user_id = current_user_id()
    return db().select(
        "messages",
        {
            "user_id": f"eq.{user_id}",
            "select": "*,tribes(id,name),events(id,title)",
            "order": "created_at.desc",
        },
    )


def mark_message_read(message_id):
    user_id = current_user_id()
    rows = db().update("messages", {"is_read": True}, {"id": f"eq.{message_id}", "user_id": f"eq.{user_id}"})
    if not rows:
        raise APIError("NOT_FOUND", "Message not found", 404)
    return rows[0]
