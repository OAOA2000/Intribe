from flask import Blueprint, request

from ..auth import require_auth
from ..services.tribes_service import (
    create_tribe,
    get_my_tribes,
    get_tribe_detail,
    join_tribe,
    leave_tribe,
    list_tribes,
)
from ..services.posts_service import create_tribe_post, list_tribe_posts
from ..utils.responses import success_response
from ..utils.validators import get_json_body

tribes_bp = Blueprint("tribes", __name__)


@tribes_bp.get("")
@require_auth
def index():
    return success_response(list_tribes(category=request.args.get("category"), search=request.args.get("search")))


@tribes_bp.get("/my")
@require_auth
def my_tribes():
    return success_response(get_my_tribes())


@tribes_bp.get("/<tribe_id>")
@require_auth
def detail(tribe_id):
    return success_response(get_tribe_detail(tribe_id))


@tribes_bp.get("/<tribe_id>/posts")
@require_auth
def posts(tribe_id):
    return success_response(list_tribe_posts(tribe_id))


@tribes_bp.post("")
@require_auth
def create():
    return success_response(create_tribe(get_json_body()), 201)


@tribes_bp.post("/<tribe_id>/posts")
@require_auth
def create_post(tribe_id):
    return success_response(create_tribe_post(tribe_id, get_json_body()), 201)


@tribes_bp.post("/<tribe_id>/join")
@require_auth
def join(tribe_id):
    return success_response(join_tribe(tribe_id), 201)


@tribes_bp.delete("/<tribe_id>/leave")
@require_auth
def leave(tribe_id):
    return success_response(leave_tribe(tribe_id))
