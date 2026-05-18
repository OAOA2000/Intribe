from flask import Blueprint

from ..auth import require_auth
from ..services.profiles_service import get_or_create_my_profile, update_my_profile
from ..utils.responses import success_response
from ..utils.validators import get_json_body

profiles_bp = Blueprint("profiles", __name__)


@profiles_bp.get("/me")
@require_auth
def get_me():
    return success_response(get_or_create_my_profile())


@profiles_bp.patch("/me")
@require_auth
def patch_me():
    return success_response(update_my_profile(get_json_body()))
