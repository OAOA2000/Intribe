import pytest

from app import create_app
from app.services import ai_service
from app.services.ai_output_parser import json_format_instructions
from app.services.ai_prompt_service import _escape_template_literals
from app.utils.errors import APIError


class FakeDb:
    def __init__(self, responses):
        self.responses = list(responses)

    def select(self, *_args, **_kwargs):
        if not self.responses:
            return []
        return self.responses.pop(0)


def _patch_user_and_db(monkeypatch, responses):
    fake_db = FakeDb(responses)
    monkeypatch.setattr(ai_service, "current_user_id", lambda: "user-1")
    monkeypatch.setattr(ai_service, "db", lambda: fake_db)


def test_tribe_digest_requires_login():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/ai/tribe-digest", json={"tribe_id": "tribe-1", "time_range": "today"})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_tribe_digest_forbids_non_member(monkeypatch):
    _patch_user_and_db(monkeypatch, [[]])

    with pytest.raises(APIError) as error:
        ai_service.generate_tribe_digest({"tribe_id": "tribe-1", "time_range": "today"})

    assert error.value.status_code == 403


def test_tribe_digest_returns_empty_state_without_llm(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "member-1", "role": "member"}],
            [{"id": "tribe-1", "name": "摄影部落", "category": "艺术"}],
            [],
            [],
            [],
            [],
        ],
    )

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("LLM should not be called for empty digest context")

    monkeypatch.setattr(ai_service, "invoke_json", fail_if_called)

    result = ai_service.generate_tribe_digest({"tribe_id": "tribe-1", "time_range": "today"})

    assert "暂无明显动态" in result["summary"]
    assert result["highlights"] == []
    assert result["todos"] == []


def test_tribe_digest_llm_failure_is_readable(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "member-1", "role": "member"}],
            [{"id": "tribe-1", "name": "摄影部落", "category": "艺术"}],
            [
                {
                    "id": "message-1",
                    "title": "帖子收到新评论",
                    "content": "有同学评论了你的帖子",
                    "is_read": False,
                    "created_at": "2026-05-19T08:00:00+00:00",
                }
            ],
            [],
            [],
            [],
        ],
    )
    monkeypatch.setattr(ai_service, "tribe_digest_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(APIError("LLM_REQUEST_FAILED", "boom", 502)),
    )

    with pytest.raises(APIError) as error:
        ai_service.generate_tribe_digest(
            {
                "tribe_id": "tribe-1",
                "start_time": "2026-05-19T00:00:00+00:00",
                "end_time": "2026-05-19T23:59:59+00:00",
            }
        )

    assert error.value.status_code == 502
    assert "AI 总结暂时生成失败" in error.value.message


def test_tribe_digest_schema_braces_are_escaped_for_langchain_template():
    schema_text = json_format_instructions(
        {
            "summary": "string",
            "highlights": [{"type": "post|comment|event|todo", "title": "string"}],
            "todos": ["string"],
        }
    )

    escaped = _escape_template_literals(schema_text)

    assert '{{"summary"' in escaped
    assert '[{{"type"' in escaped
    assert '"string"]}}' in escaped
