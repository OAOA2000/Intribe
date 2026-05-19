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


def tribe_digest_prompt():
    return build_json_prompt(
        (
            "你负责把一个校园兴趣部落在指定时间段内的消息、帖子、评论和活动整理成“今日部落动态”。"
            "只能依据输入上下文总结，不要编造不存在的帖子、活动、评论。"
            "不要输出敏感信息，不要泄露数据库字段名。"
            "如果上下文没有明显动态，summary 必须明确包含“暂无明显动态”。"
            "语言要简洁、自然，适合学生在消息中心快速浏览。"
        ),
        (
            "部落：{tribe}\n"
            "时间范围：{time_range}\n"
            "可总结上下文 JSON：{context}\n\n"
            "请生成今日部落动态，突出最近被讨论的帖子、重要评论或回复、近期活动和必要待办。"
        ),
        {
            "summary": "string，1 到 3 句中文，不能包含 Markdown",
            "highlights": [
                {
                    "type": "post|comment|event|todo",
                    "title": "string",
                    "description": "string",
                    "target_type": "post|event|message|null",
                    "target_id": "uuid|null",
                }
            ],
            "todos": ["string"],
        },
    )
