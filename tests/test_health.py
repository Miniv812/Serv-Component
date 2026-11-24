from freezegun import freeze_time


def test_liveness_endpoint(client):
    response = client.get("/healthz/live")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "alive"
    assert "timestamp" in data


@freeze_time("2026-10-05 12:00:00")
def test_frozen_time_liveness(client):
    response = client.get("/healthz/live")
    assert response.status_code == 200
    assert response.get_json()["timestamp"].startswith("2026-10-05T12:00:00")


def test_readiness_endpoint(client):
    response = client.get("/healthz/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
