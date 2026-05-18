from .errors import APIError


def get_json_body():
    from flask import request

    body = request.get_json(silent=True)
    if body is None:
        return {}
    if not isinstance(body, dict):
        raise APIError("INVALID_REQUEST", "Request body must be a JSON object", 400)
    return body


def pick_allowed_fields(data, allowed_fields):
    return {key: value for key, value in data.items() if key in allowed_fields}


def require_fields(data, required_fields):
    missing = [field for field in required_fields if data.get(field) in (None, "")]
    if missing:
        raise APIError("VALIDATION_ERROR", f"Missing required fields: {', '.join(missing)}", 400)
