from flask import Blueprint

from ..auth import require_auth
from ..services.ai_service import generate_activity_copy, generate_post_summary, generate_tribe_digest
from ..utils.responses import success_response
from ..utils.validators import get_json_body

ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/activity-copy")
@require_auth
def activity_copy():
    return success_response(generate_activity_copy(get_json_body()))


@ai_bp.post("/tribe-digest")
@require_auth
def tribe_digest():
    return success_response(generate_tribe_digest(get_json_body()))


@ai_bp.post("/post-summary")
@require_auth
def post_summary():
    return success_response(generate_post_summary(get_json_body()))
