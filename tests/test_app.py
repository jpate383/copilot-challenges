"""Tests for the FastAPI application endpoints"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_activity_structure(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client, sample_email):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert sample_email in data["message"]

    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client, sample_email):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_persists(self, client, sample_email):
        """Test that signup persists in activity participants"""
        client.post(
            "/activities/Drama Club/signup",
            params={"email": sample_email}
        )
        
        response = client.get("/activities")
        assert sample_email in response.json()["Drama Club"]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_existing_participant(self, client):
        """Test removing an existing participant"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_participant(self, client):
        """Test removing a participant that doesn't exist"""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "definitely.not.signed.up@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity(self, client, sample_email):
        """Test removing from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_persists(self, client):
        """Test that removal persists"""
        email = "michael@mergington.edu"
        
        client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
