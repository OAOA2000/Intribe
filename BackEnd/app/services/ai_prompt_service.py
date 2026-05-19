from .ai_output_parser import json_format_instructions
from ..utils.errors import APIError


BASE_SYSTEM_PROMPT = (
    "你是校园兴趣部落与活动协作平台的 AI 助手。"
    "回答必须简洁、安全、适合高校学生社区场景。"
    "不要编造平台中不存在的数据；如果上下文为空或不足，返回空状态字段。"
)


def build_json_prompt(system_message, user_template, output_schema):
    try:
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError as exc:
        raise APIError("LLM_DEPENDENCY_MISSING", "LangChain Core dependency is not installed", 500) from exc

    system = "\n".join(
        [
            BASE_SYSTEM_PROMPT,
            system_message.strip(),
            json_format_instructions(output_schema),
        ]
    )
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", user_template),
        ]
    )


def activity_copy_prompt():
    return build_json_prompt(
        "根据用户提供的活动草稿生成可发布的活动文案。",
        (
            "活动标题：{title}\n"
            "活动描述：{description}\n"
            "活动地点：{location}\n"
            "活动时间：{start_time}\n"
            "当前用户资料：{profile}\n\n"
            "请输出适合活动报名页的一段中文文案。"
        ),
        {"copy": "string，80 到 180 个中文字符，不能包含 Markdown"},
    )
