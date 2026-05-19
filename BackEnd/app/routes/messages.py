from flask import Blueprint

from ..auth import require_auth
from ..services.messages_service import (
    delete_message,
    delete_messages,
    get_unread_count,
    list_messages,
    mark_all_messages_read,
    mark_message_read,
)
from ..utils.responses import success_response
from ..utils.validators import get_json_body

messages_bp = Blueprint("messages", __name__)


@messages_bp.get("")
@require_auth
def index():
    return success_response(list_messages())


@messages_bp.get("/unread-count")
@require_auth
def unread_count():
    return success_response(get_unread_count())


@messages_bp.patch("/<message_id>/read")
@require_auth
def read(message_id):
    return success_response(mark_message_read(message_id))


@messages_bp.patch("/read-all")
@require_auth
def read_all():
    return success_response(mark_all_messages_read())


@messages_bp.delete("/<message_id>")
@require_auth
def delete(message_id):
    return success_response(delete_message(message_id))


@messages_bp.post("/bulk-delete")
@require_auth
def bulk_delete():
    return success_response(delete_messages(get_json_body().get("message_ids")))
