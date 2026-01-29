"""Tests for FastAPI application endpoints"""
import pytest


def test_get_activities(client, reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that all activities are returned
    assert "Basketball" in data
    assert "Tennis Club" in data
    assert "Music Band" in data
    
    # Check activity structure
    basketball = data["Basketball"]
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball
    assert len(basketball["participants"]) > 0


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Basketball/signup",
        params={"email": "new_student@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "new_student@mergington.edu" in data["message"]


def test_signup_duplicate(client, reset_activities):
    """Test that signing up twice raises an error"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response = client.post(
        "/activities/Basketball/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(
        "/activities/Basketball/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonExistentActivity/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity(client, reset_activities):
    """Test unregistering from an activity"""
    email = "unregister@mergington.edu"
    
    # First, sign up
    response = client.post(
        "/activities/Basketball/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Then unregister
    response = client.delete(
        "/activities/Basketball/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]


def test_unregister_not_registered(client, reset_activities):
    """Test unregistering from an activity when not registered"""
    response = client.delete(
        "/activities/Basketball/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregistering from a non-existent activity"""
    response = client.delete(
        "/activities/NonExistentActivity/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_participants_list_updated_after_signup(client, reset_activities):
    """Test that participants list is updated after signup"""
    email = "participant@mergington.edu"
    activity_name = "Tennis Club"
    
    # Get initial participants count
    response = client.get("/activities")
    initial_count = len(response.json()[activity_name]["participants"])
    
    # Sign up
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Check updated participants
    response = client.get("/activities")
    updated_count = len(response.json()[activity_name]["participants"])
    assert updated_count == initial_count + 1
    assert email in response.json()[activity_name]["participants"]


def test_participants_list_updated_after_unregister(client, reset_activities):
    """Test that participants list is updated after unregister"""
    email = "temp_participant@mergington.edu"
    activity_name = "Art Studio"
    
    # Sign up first
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Get count before unregister
    response = client.get("/activities")
    count_before = len(response.json()[activity_name]["participants"])
    
    # Unregister
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Check updated participants
    response = client.get("/activities")
    count_after = len(response.json()[activity_name]["participants"])
    assert count_after == count_before - 1
    assert email not in response.json()[activity_name]["participants"]
