from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_dummy():
    print("test dummy")
    response = client.post(
        "/dummy", json={"title": "test dummy", "message": "Dummy test"}
    )
    assert response.status_code == 200
    assert response.json() == {"title": "test dummy", "message": "Dummy test"}


def test_mock_grafana():
    print("test jira payload creation")
    response = client.post(
        "/grafana8-mock",
        json={
            "title": "test jira payload creation title",
            "message": "test jira payload creation message",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "fields": {
            "description": "test jira payload creation message",
            "issuetype": {"id": "3"},
            "project": {"key": "test"},
            "summary": "test jira payload creation title",
        }
    }
