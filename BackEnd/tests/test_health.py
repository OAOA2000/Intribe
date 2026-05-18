from app import create_app


def test_health_returns_ok():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"
    assert payload["error"] is None
