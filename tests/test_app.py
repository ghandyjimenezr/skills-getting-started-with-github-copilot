import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_expected_structure():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Programming Class" in data
    assert "participants" in data["Programming Class"]


def test_signup_for_activity_success():
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activities_response = client.get("/activities")
    participants = activities_response.json()["Programming Class"]["participants"]
    assert email in participants


def test_signup_for_activity_duplicate_returns_409():
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": "EMMA@MERGINGTON.EDU "},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_cancel_signup_removes_participant():
    email = "remove.me@mergington.edu"

    client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    delete_response = client.delete(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert delete_response.status_code == 200
    assert "Cancelled signup" in delete_response.json()["message"]

    activities_response = client.get("/activities")
    participants = activities_response.json()["Programming Class"]["participants"]
    assert email not in participants


def test_cancel_signup_missing_participant_returns_404():
    response = client.delete(
        "/activities/Programming%20Class/signup",
        params={"email": "ghost@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
