from functools import wraps

import requests
from flask import current_app, g, request

from .utils.config_check import require_supabase_config
from .utils.errors import APIError


def _extract_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise APIError("UNAUTHORIZED", "Unauthorized", 401)

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise APIError("UNAUTHORIZED", "Unauthorized", 401)
    return token


def get_current_user_from_supabase(token):
    supabase_url = current_app.config["SUPABASE_URL"].rstrip("/")
    anon_key = current_app.config["SUPABASE_ANON_KEY"]

    require_supabase_config(supabase_url, anon_key)

    try:
        response = requests.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=current_app.config["REQUEST_TIMEOUT_SECONDS"],
        )
    except requests.RequestException as exc:
        current_app.logger.warning("Failed to reach Supabase Auth: %s", exc)
        raise APIError(
            "SUPABASE_AUTH_UNAVAILABLE",
            "Could not reach Supabase Auth. Check SUPABASE_URL, network access, and project status.",
            502,
        ) from exc

    if response.status_code != 200:
        raise APIError("UNAUTHORIZED", "Unauthorized", 401)

    user = response.json()
    if not user.get("id"):
        raise APIError("UNAUTHORIZED", "Unauthorized", 401)
    return user


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        token = _extract_bearer_token()
        g.access_token = token
        g.current_user = get_current_user_from_supabase(token)
        return view(*args, **kwargs)

    return wrapped
