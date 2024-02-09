from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_dummy():
    print("test dummy")
    response = client.post(
        "/dummy",
        json={
            "title": "test dummy",
            "message": "Dummy test",
            "ruleUrl": "https://www.lifen.fr",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "title": "test dummy",
        "message": "Dummy test",
        "ruleUrl": "https://www.lifen.fr",
    }


def test_mock_grafana():
    print("test jira payload creation")
    response = client.post(
        "/grafana8-mock",
        json={
            "title": "test jira payload creation title",
            "message": "test jira payload creation message",
            "ruleUrl": "https://www.lifen.fr",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "fields": {
            "description": "test jira payload creation message\nhttps://www.lifen.fr",
            "issuetype": {"id": "3"},
            "project": {"key": "test"},
            "summary": "test jira payload creation title",
        }
    }
