import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 4,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_data_and_disables_caching(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 4,
            "participants": ["existing@example.com"],
        }
    }
    assert response.headers["cache-control"] == "no-store"


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert app_module.activities["Chess Club"]["participants"] == [
        "existing@example.com",
        email,
    ]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert app_module.activities["Chess Club"]["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert app_module.activities["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert app_module.activities["Chess Club"]["participants"] == ["existing@example.com"]