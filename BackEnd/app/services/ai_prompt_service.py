from .ai_output_parser import json_format_instructions
from ..utils.errors import APIError


BASE_SYSTEM_PROMPT = (
    "你是校园兴趣部落与活动协作平台的 AI 助手。"
    "回答必须简洁、安全、适合高校学生社区场景。"
    "不要编造平台中不存在的数据；如果上下文为空或不足，返回空状态字段。"
)


def _escape_template_literals(value):
    return value.replace("{", "{{").replace("}", "}}")


def build_json_prompt(system_message, user_template, output_schema):
    try:
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError as exc:
        raise APIError("LLM_DEPENDENCY_MISSING", "LangChain Core dependency is not installed", 500) from exc

    system = _escape_template_literals(
        "\n".join(
            [
                BASE_SYSTEM_PROMPT,
                system_message.strip(),
                json_format_instructions(output_schema),
            ]
        )
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


def post_summary_prompt():
    return build_json_prompt(
        (
            "你负责总结校园兴趣部落帖子详情页中的正文和评论讨论。"
            "只能基于输入的帖子和评论内容总结，不要编造不存在的观点、人物、结论或行动项。"
            "需要区分“已达成共识”和“仍在讨论的问题”；如果没有评论，也要基于帖子正文给出简洁总结。"
            "对争议内容保持中立，不要替任何一方下判断。"
            "输出语言必须为中文，风格简洁，适合校园社区阅读。"
            "不要输出 Markdown，不要泄露数据库字段名。"
        ),
        (
            "帖子标题：{post_title}\n"
            "帖子作者：{post_author}\n"
            "发布时间：{post_created_at}\n"
            "帖子正文：{post_content}\n"
            "评论数量：{comment_count}\n"
            "压缩后的评论上下文：{comments_context}\n\n"
            "请生成结构化讨论总结。"
        ),
        {
            "post_title": "string，帖子标题",
            "summary": "string，1 到 3 句中文，概括帖子正文和讨论",
            "key_points": ["string，关键观点或已形成的共识"],
            "discussion_threads": [
                {
                    "topic": "string，讨论主题",
                    "summary": "string，中立总结该主题下的讨论",
                }
            ],
            "open_questions": ["string，仍未解决或仍在讨论的问题"],
            "action_items": ["string，明确出现的后续行动或建议，没有则为空数组"],
        },
    )


def recommendations_prompt():
    return build_json_prompt(
        (
            "你负责根据当前用户资料，从平台提供的候选兴趣部落和活动中选择推荐项。"
            "只能从输入的候选 tribes/events 中选择，必须使用候选项里的 id，不允许编造数据库中不存在的部落或活动。"
            "推荐理由必须具体说明用户资料与候选项名称、描述、分类、地点或时间的关联，不要泛泛而谈。"
            "如果用户个人简介为空，需要在 profile_basis.notes 中提示用户完善资料，同时可以基于专业、热门或近期内容做弱推荐。"
            "输出必须为中文，score 范围必须是 0 到 1。"
        ),
        (
            "用户资料 JSON：{profile}\n"
            "候选部落 JSON：{tribes}\n"
            "候选活动 JSON：{events}\n"
            "推荐数量：部落最多 {limit_tribes} 个，活动最多 {limit_events} 个。\n\n"
            "请生成结构化个性推荐。"
        ),
        {
            "profile_basis": {
                "used_bio": "boolean",
                "used_interests": "boolean",
                "notes": "string，中文，说明本次推荐依据或资料不足提示",
            },
            "recommended_tribes": [
                {
                    "tribe_id": "uuid，必须来自候选部落 id",
                    "name": "string，候选部落名称",
                    "reason": "string，具体中文理由",
                    "match_tags": ["string"],
                    "score": "number，0 到 1",
                }
            ],
            "recommended_events": [
                {
                    "event_id": "uuid，必须来自候选活动 id",
                    "title": "string，候选活动标题",
                    "reason": "string，具体中文理由",
                    "match_tags": ["string"],
                    "score": "number，0 到 1",
                }
            ],
        },
    )
