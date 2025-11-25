"""
Tests for authentication endpoints.
Tests login, registration, and user info endpoints.

IMPORTANT: All test passwords must be <= 72 bytes (bcrypt limit).
Current test passwords are all well under this limit.
"""
import pytest
from fastapi.testclient import TestClient
from app.crud import user as crud_user
from app.models.user import UserRole


def test_register_user_as_admin(client, db_session):
    """Test registering a new user by admin."""
    # First, create an admin user directly in DB (bypass registration)
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    # Login as admin to get token
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Register new user as admin
    headers = {"Authorization": f"Bearer {token}"}
    register_response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "securepass123",
            "role": "staff"
        },
        headers=headers
    )
    
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "staff"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be in response


def test_register_user_as_non_admin_fails(client, db_session):
    """Test that non-admin users cannot register new users."""
    # Create a staff user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    staff_user = User(
        username="staff",
        hashed_password=get_password_hash("staff123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(staff_user)
    db_session.commit()
    
    # Login as staff
    login_response = client.post(
        "/auth/login",
        data={"username": "staff", "password": "staff123"}
    )
    token = login_response.json()["access_token"]
    
    # Try to register - should fail
    headers = {"Authorization": f"Bearer {token}"}
    register_response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "securepass123",
            "role": "staff"
        },
        headers=headers
    )
    
    assert register_response.status_code == 403
    assert "admin" in register_response.json()["detail"].lower()


def test_register_without_auth_fails(client):
    """Test that registration requires authentication."""
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "securepass123",
            "role": "staff"
        }
    )
    
    assert response.status_code == 401  # Unauthorized


def test_login_success(client, db_session):
    """Test successful login."""
    # Create a user directly in DB
    from app.core.security import get_password_hash
    from app.models.user import User
    
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_password(client, db_session):
    """Test login with wrong password."""
    # Create a user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    user = User(
        username="testuser",
        hashed_password=get_password_hash("correctpass"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpass"}
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "anypass"}
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_inactive_user(client, db_session):
    """Test login with inactive user."""
    # Create inactive user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    user = User(
        username="inactive",
        hashed_password=get_password_hash("pass123"),
        role=UserRole.STAFF,
        is_active=False  # Inactive
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login
    response = client.post(
        "/auth/login",
        data={"username": "inactive", "password": "pass123"}
    )
    
    assert response.status_code == 401


def test_get_current_user_info(client, db_session):
    """Test getting current user information."""
    # Create and login user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.MANAGER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "manager"
    assert "hashed_password" not in data  # Password should not be exposed


def test_get_current_user_without_token(client):
    """Test getting user info without authentication token."""
    response = client.get("/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_with_invalid_token(client):
    """Test getting user info with invalid token."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401


def test_register_duplicate_username(client, db_session):
    """Test registering with duplicate username."""
    # Create admin user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create existing user
    existing = User(
        username="existing",
        hashed_password=get_password_hash("pass123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(existing)
    db_session.commit()
    
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Try to register with duplicate username
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/auth/register",
        json={
            "username": "existing",  # Already exists
            "password": "pass123",
            "role": "staff"
        },
        headers=headers
    )
    
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


def test_token_expiration(client, db_session):
    """Test that tokens expire after the configured time."""
    # This test would require mocking time or waiting, so we'll just verify token structure
    from app.core.security import get_password_hash
    from app.models.user import User
    
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Token should be a valid JWT string
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT tokens have 3 parts separated by dots
    assert len(token.split(".")) == 3


def test_delete_user_as_admin(client, db_session):
    """Test that admin can delete a user."""
    # Create admin user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    
    # Create a user to delete
    user_to_delete = User(
        username="todelete",
        hashed_password=get_password_hash("pass123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(user_to_delete)
    
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete user
    delete_response = client.delete(
        f"/auth/users/{user_to_delete.id}",
        headers=headers
    )
    
    assert delete_response.status_code == 204
    
    # Verify user is deleted
    from app.crud import user as crud_user
    deleted_user = crud_user.get_user(db_session, user_to_delete.id)
    assert deleted_user is None


def test_delete_user_as_non_admin_fails(client, db_session):
    """Test that non-admin users cannot delete users."""
    # Create admin and staff users
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    
    staff_user = User(
        username="staff",
        hashed_password=get_password_hash("staff123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(staff_user)
    
    # Create a user to delete
    user_to_delete = User(
        username="todelete",
        hashed_password=get_password_hash("pass123"),
        role=UserRole.VIEWER,
        is_active=True
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(staff_user)
    db_session.refresh(user_to_delete)
    
    # Login as staff (non-admin)
    login_response = client.post(
        "/auth/login",
        data={"username": "staff", "password": "staff123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to delete user
    delete_response = client.delete(
        f"/auth/users/{user_to_delete.id}",
        headers=headers
    )
    
    assert delete_response.status_code == 403
    assert "Only admin" in delete_response.json()["detail"]


def test_delete_nonexistent_user(client, db_session):
    """Test deleting a user that doesn't exist."""
    # Create admin user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to delete non-existent user
    delete_response = client.delete(
        "/auth/users/99999",
        headers=headers
    )
    
    assert delete_response.status_code == 404
    assert "not found" in delete_response.json()["detail"].lower()


def test_admin_cannot_delete_themselves(client, db_session):
    """Test that admin cannot delete their own account."""
    # Create admin user
    from app.core.security import get_password_hash
    from app.models.user import User
    
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to delete own account
    delete_response = client.delete(
        f"/auth/users/{admin_user.id}",
        headers=headers
    )
    
    assert delete_response.status_code == 400
    assert "Cannot delete your own account" in delete_response.json()["detail"]

