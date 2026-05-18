from flask import Blueprint

from ..auth import require_auth
from ..services.posts_service import (
    create_comment,
    delete_comment,
    delete_post,
    get_post_detail,
    update_comment,
    update_post,
)
from ..utils.responses import success_response
from ..utils.validators import get_json_body

posts_bp = Blueprint("posts", __name__)
comments_bp = Blueprint("comments", __name__)


@posts_bp.get("/<post_id>")
@require_auth
def detail(post_id):
    return success_response(get_post_detail(post_id))


@posts_bp.patch("/<post_id>")
@require_auth
def patch(post_id):
    return success_response(update_post(post_id, get_json_body()))


@posts_bp.delete("/<post_id>")
@require_auth
def delete(post_id):
    return success_response(delete_post(post_id))


@posts_bp.post("/<post_id>/comments")
@require_auth
def comment(post_id):
    return success_response(create_comment(post_id, get_json_body()), 201)


@comments_bp.patch("/<comment_id>")
@require_auth
def patch_comment(comment_id):
    return success_response(update_comment(comment_id, get_json_body()))


@comments_bp.delete("/<comment_id>")
@require_auth
def delete_comment_route(comment_id):
    return success_response(delete_comment(comment_id))
