import pytest

from app import create_app
from app.services import ai_service
from app.utils.errors import APIError


class FakeDb:
    def __init__(self, responses):
        self.responses = list(responses)

    def select(self, *_args, **_kwargs):
        if not self.responses:
            return []
        return self.responses.pop(0)


def _post(**overrides):
    return {
        "id": "post-1",
        "title": "排练时间征集",
        "content": "这周想约一次乐队排练，大家看看周五晚上是否方便。",
        "author_id": "user-2",
        "created_at": "2026-05-19T08:00:00+00:00",
        "tribe_id": "tribe-1",
        "tribes": {"id": "tribe-1", "name": "吉他社", "owner_id": "owner-1"},
        **overrides,
    }


def _patch_user_and_db(monkeypatch, responses):
    fake_db = FakeDb(responses)
    monkeypatch.setattr(ai_service, "current_user_id", lambda: "user-1")
    monkeypatch.setattr(ai_service, "db", lambda: fake_db)
    return fake_db


def test_post_summary_requires_login():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/ai/post-summary", json={"post_id": "post-1"})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_post_summary_forbids_non_member(monkeypatch):
    _patch_user_and_db(monkeypatch, [[_post()], []])

    with pytest.raises(APIError) as error:
        ai_service.generate_post_summary({"post_id": "post-1"})

    assert error.value.status_code == 403


def test_post_summary_rejects_deleted_or_invisible_post(monkeypatch):
    _patch_user_and_db(monkeypatch, [[]])

    with pytest.raises(APIError) as error:
        ai_service.generate_post_summary({"post_id": "post-1"})

    assert error.value.status_code == 404


def test_post_summary_allows_empty_comments(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [_post()],
            [{"id": "member-1", "role": "member"}],
            [],
            [{"id": "user-1", "display_name": "当前同学"}],
        ],
    )
    monkeypatch.setattr(ai_service, "post_summary_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "post_title": "排练时间征集",
            "summary": "帖子主要在征集本周排练时间。",
            "key_points": ["周五晚上是被提出的候选时间"],
            "discussion_threads": [],
            "open_questions": ["具体时间仍需确认"],
            "action_items": [],
        },
    )

    result = ai_service.generate_post_summary({"post_id": "post-1"})

    assert result["comment_count"] == 0
    assert result["summary"] == "帖子主要在征集本周排练时间。"
    assert result["open_questions"] == ["具体时间仍需确认"]


def test_post_summary_llm_failure_is_readable(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [_post()],
            [{"id": "member-1", "role": "member"}],
            [
                {
                    "id": "comment-1",
                    "parent_id": None,
                    "author_id": "user-1",
                    "content": "我周五晚上可以。",
                    "created_at": "2026-05-19T09:00:00+00:00",
                }
            ],
            [{"id": "user-1", "display_name": "当前同学"}],
        ],
    )
    monkeypatch.setattr(ai_service, "post_summary_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(APIError("LLM_REQUEST_FAILED", "boom", 502)),
    )

    with pytest.raises(APIError) as error:
        ai_service.generate_post_summary({"post_id": "post-1"})

    assert error.value.status_code == 502
    assert "AI 总结暂时生成失败" in error.value.message
