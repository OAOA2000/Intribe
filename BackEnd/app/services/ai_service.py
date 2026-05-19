from .ai_context_service import get_current_profile_context
from .ai_prompt_service import activity_copy_prompt
from .llm_service import invoke_json
from ..utils.errors import APIError
from ..utils.validators import require_fields


def _clean_text(value, max_length=2000):
    if value in (None, ""):
        return ""
    text = str(value).strip()
    if len(text) > max_length:
        raise APIError("VALIDATION_ERROR", f"Input text is too long. Max length is {max_length}", 400)
    return text


def generate_activity_copy(data):
    require_fields(data, ("title",))

    variables = {
        "title": _clean_text(data.get("title"), 120),
        "description": _clean_text(data.get("description") or "精彩校园活动"),
        "location": _clean_text(data.get("location") or "校园内", 120),
        "start_time": _clean_text(data.get("start_time") or data.get("time") or "近期", 120),
        "profile": get_current_profile_context(),
    }

    return invoke_json(
        activity_copy_prompt(),
        variables,
        required_fields=("copy",),
        defaults={"copy": ""},
        temperature=0.4,
    )
