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


def _patch_user_and_db(monkeypatch, responses, user_id="user-1"):
    fake_db = FakeDb(responses)
    monkeypatch.setattr(ai_service, "current_user_id", lambda: user_id)
    monkeypatch.setattr(ai_service, "current_user_email", lambda: "student@example.edu")
    monkeypatch.setattr(ai_service, "db", lambda: fake_db)
    return fake_db


def _tribe(**overrides):
    return {
        "id": "tribe-1",
        "name": "算法学习部落",
        "description": "一起刷题、分享竞赛经验和工程实践。",
        "category": "科技",
        "tribe_members": [],
        **overrides,
    }


def _event(**overrides):
    return {
        "id": "event-1",
        "title": "算法竞赛训练营",
        "description": "面向编程和算法爱好者的训练活动。",
        "location": "实验楼",
        "start_time": "2026-05-20T08:00:00+00:00",
        "status": "recruiting",
        "tribe_id": "tribe-1",
        "tribes": {"id": "tribe-1", "name": "算法学习部落", "category": "科技"},
        **overrides,
    }


def test_recommendations_requires_login():
    app = create_app()
    client = app.test_client()

    response = client.post("/api/ai/recommendations", json={})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_recommendations_handles_missing_profile(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [],
            [],
            [],
            [_tribe()],
            [_event()],
        ],
    )
    monkeypatch.setattr(ai_service, "recommendations_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "profile_basis": {"used_bio": False, "used_interests": False, "notes": "资料较少。"},
            "recommended_tribes": [],
            "recommended_events": [],
        },
    )

    result = ai_service.generate_recommendations({})

    assert "完善个人简介" in result["profile_basis"]["notes"]
    assert result["recommended_tribes"][0]["tribe_id"] == "tribe-1"
    assert result["recommended_events"][0]["event_id"] == "event-1"


def test_recommendations_returns_empty_without_candidates(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "user-1", "display_name": "同学", "major": "", "bio": ""}],
            [],
            [],
            [],
            [],
        ],
    )

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("LLM should not be called without candidates")

    monkeypatch.setattr(ai_service, "invoke_json", fail_if_called)

    result = ai_service.generate_recommendations({})

    assert result["recommended_tribes"] == []
    assert result["recommended_events"] == []


def test_recommendations_filters_joined_tribes_and_registered_events(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "user-1", "display_name": "同学", "major": "计算机", "bio": "喜欢算法和开源。"}],
            [{"tribe_id": "tribe-joined"}],
            [{"event_id": "event-registered"}],
            [_tribe(id="tribe-joined", name="已加入部落"), _tribe(id="tribe-open")],
            [_event(id="event-registered", title="已报名活动"), _event(id="event-open")],
        ],
    )
    monkeypatch.setattr(ai_service, "recommendations_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "profile_basis": {"used_bio": True, "used_interests": False, "notes": "基于简介推荐。"},
            "recommended_tribes": [
                {"tribe_id": "tribe-joined", "name": "已加入部落", "reason": "不应出现", "match_tags": [], "score": 1},
                {"tribe_id": "tribe-open", "name": "算法学习部落", "reason": "和算法兴趣匹配。", "match_tags": ["算法"], "score": 0.9},
            ],
            "recommended_events": [
                {"event_id": "event-registered", "title": "已报名活动", "reason": "不应出现", "match_tags": [], "score": 1},
                {"event_id": "event-open", "title": "算法竞赛训练营", "reason": "适合算法兴趣。", "match_tags": ["算法"], "score": 0.9},
            ],
        },
    )

    result = ai_service.generate_recommendations({})

    assert [item["tribe_id"] for item in result["recommended_tribes"]] == ["tribe-open"]
    assert [item["event_id"] for item in result["recommended_events"]] == ["event-open"]


def test_recommendations_falls_back_when_llm_output_is_invalid(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "user-1", "display_name": "同学", "major": "计算机", "bio": "喜欢算法和开源。"}],
            [],
            [],
            [_tribe()],
            [_event()],
        ],
    )
    monkeypatch.setattr(ai_service, "recommendations_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(APIError("LLM_OUTPUT_PARSE_ERROR", "bad json", 502)),
    )

    result = ai_service.generate_recommendations({})

    assert result["recommended_tribes"][0]["tribe_id"] == "tribe-1"
    assert result["recommended_events"][0]["event_id"] == "event-1"


def test_recommendations_respects_zero_limits(monkeypatch):
    _patch_user_and_db(
        monkeypatch,
        [
            [{"id": "user-1", "display_name": "同学", "major": "计算机", "bio": "喜欢算法和开源。"}],
            [],
            [],
            [_tribe()],
            [_event()],
        ],
    )
    monkeypatch.setattr(ai_service, "recommendations_prompt", lambda: object())
    monkeypatch.setattr(
        ai_service,
        "invoke_json",
        lambda *_args, **_kwargs: {
            "profile_basis": {"used_bio": True, "used_interests": False, "notes": "基于简介推荐。"},
            "recommended_tribes": [
                {"tribe_id": "tribe-1", "name": "算法学习部落", "reason": "和算法兴趣匹配。", "match_tags": ["算法"], "score": 0.9}
            ],
            "recommended_events": [
                {"event_id": "event-1", "title": "算法竞赛训练营", "reason": "适合算法兴趣。", "match_tags": ["算法"], "score": 0.9}
            ],
        },
    )

    result = ai_service.generate_recommendations({"limit_tribes": 0, "limit_events": 0})

    assert result["recommended_tribes"] == []
    assert result["recommended_events"] == []
