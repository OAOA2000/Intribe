import json
import re

from ..utils.errors import APIError


_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def json_format_instructions(schema):
    """Return compact JSON-only instructions for prompts."""
    return (
        "只返回一个合法 JSON object，不要使用 Markdown，不要添加解释文字。"
        f" JSON 字段约束：{json.dumps(schema, ensure_ascii=False)}"
    )


def _strip_code_fence(text):
    return _CODE_FENCE_RE.sub("", text.strip()).strip()


def parse_json_object(text, required_fields=None, defaults=None):
    if not text or not str(text).strip():
        raise APIError("LLM_EMPTY_OUTPUT", "LLM returned an empty response", 502)

    raw = _strip_code_fence(str(text))
    decoder = json.JSONDecoder()
    start = raw.find("{")
    if start < 0:
        raise APIError("LLM_OUTPUT_PARSE_ERROR", "LLM output is not a JSON object", 502)

    try:
        parsed, _end = decoder.raw_decode(raw[start:])
    except json.JSONDecodeError as exc:
        raise APIError("LLM_OUTPUT_PARSE_ERROR", "LLM output is not valid JSON", 502) from exc

    if not isinstance(parsed, dict):
        raise APIError("LLM_OUTPUT_PARSE_ERROR", "LLM output must be a JSON object", 502)

    result = {**(defaults or {}), **parsed}
    missing = [field for field in (required_fields or ()) if result.get(field) in (None, "")]
    if missing:
        raise APIError("LLM_OUTPUT_PARSE_ERROR", f"LLM output missing fields: {', '.join(missing)}", 502)

    return result
