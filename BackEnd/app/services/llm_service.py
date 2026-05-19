from flask import current_app

from ..utils.errors import APIError
from .ai_output_parser import parse_json_object


def _require_llm_config():
    api_key = current_app.config.get("LLM_API_KEY")
    model_name = current_app.config.get("LLM_MODEL_NAME")
    if not api_key or not model_name:
        raise APIError("LLM_NOT_CONFIGURED", "LLM API key or model name is not configured", 500)


def _chat_model(temperature=0.2):
    _require_llm_config()

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise APIError("LLM_DEPENDENCY_MISSING", "LangChain OpenAI dependencies are not installed", 500) from exc

    kwargs = {
        "api_key": current_app.config["LLM_API_KEY"],
        "model": current_app.config["LLM_MODEL_NAME"],
        "temperature": temperature,
        "timeout": current_app.config["LLM_TIMEOUT_SECONDS"],
    }

    base_url = current_app.config.get("LLM_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    return ChatOpenAI(**kwargs)


def invoke_json(prompt_template, variables, required_fields=None, defaults=None, temperature=0.2):
    try:
        prompt_value = prompt_template.invoke(variables)
        response = _chat_model(temperature=temperature).invoke(prompt_value)
    except APIError:
        raise
    except Exception as exc:
        current_app.logger.warning("LLM request failed: %s", exc)
        raise APIError("LLM_REQUEST_FAILED", "LLM request failed. Please try again later.", 502) from exc

    content = getattr(response, "content", response)
    return parse_json_object(content, required_fields=required_fields, defaults=defaults)
