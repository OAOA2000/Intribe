from flask import Blueprint

from ..auth import require_auth
from ..services.dashboard_service import get_manageable_events, get_summary
from ..utils.responses import success_response

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/summary")
@require_auth
def summary():
    return success_response(get_summary())


@dashboard_bp.get("/events")
@require_auth
def events():
    return success_response(get_manageable_events())
