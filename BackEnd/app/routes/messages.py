from flask import Blueprint

from ..auth import require_auth
from ..services.messages_service import get_unread_count, list_messages, mark_message_read
from ..utils.responses import success_response

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
