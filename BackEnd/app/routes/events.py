from flask import Blueprint, request

from ..auth import require_auth
from ..services.events_service import (
    cancel_registration,
    create_event,
    delete_event,
    get_event_detail,
    list_my_registrations,
    list_events,
    register_event,
    update_event,
)
from ..utils.responses import success_response
from ..utils.validators import get_json_body

events_bp = Blueprint("events", __name__)


@events_bp.get("")
@require_auth
def index():
    return success_response(
        list_events(
            status=request.args.get("status"),
            tribe_id=request.args.get("tribe_id"),
            search=request.args.get("search"),
        )
    )


@events_bp.get("/my-registrations")
@require_auth
def my_registrations():
    return success_response(list_my_registrations())


@events_bp.get("/<event_id>")
@require_auth
def detail(event_id):
    return success_response(get_event_detail(event_id))


@events_bp.post("")
@require_auth
def create():
    return success_response(create_event(get_json_body()), 201)


@events_bp.patch("/<event_id>")
@require_auth
def patch(event_id):
    return success_response(update_event(event_id, get_json_body()))


@events_bp.delete("/<event_id>")
@require_auth
def delete(event_id):
    return success_response(delete_event(event_id))


@events_bp.post("/<event_id>/register")
@require_auth
def register(event_id):
    return success_response(register_event(event_id), 201)


@events_bp.delete("/<event_id>/register")
@require_auth
def cancel(event_id):
    return success_response(cancel_registration(event_id))
