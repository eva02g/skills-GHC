from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


def test_get_activities_returns_activity_catalog(reset_activities):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_rejects_duplicate_registration(reset_activities):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_when_activity_is_full(reset_activities):
    activity = activities["Basketball Team"]
    activity["participants"] = [f"student{i}@mergington.edu" for i in range(activity["max_participants"])]

    response = client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_remove_participant_success(reset_activities):
    response = client.delete("/activities/Chess Club/remove?email=michael@mergington.edu")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
