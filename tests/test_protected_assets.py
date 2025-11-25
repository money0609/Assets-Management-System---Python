"""
Tests for protected asset endpoints with authentication.
Tests that protected routes require authentication and work correctly.

IMPORTANT: All test passwords must be <= 72 bytes (bcrypt limit).
Current test passwords are all well under this limit.
"""
import pytest
from app.models.user import UserRole


@pytest.fixture
def admin_token(client, db_session):
    """Create an admin user and return auth token."""
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
    
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def staff_token(client, db_session):
    """Create a staff user and return auth token."""
    from app.core.security import get_password_hash
    from app.models.user import User
    
    staff = User(
        username="staff",
        hashed_password=get_password_hash("staff123"),
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(staff)
    db_session.commit()
    
    response = client.post(
        "/auth/login",
        data={"username": "staff", "password": "staff123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def manager_token(client, db_session):
    """Create a manager user and return auth token."""
    from app.core.security import get_password_hash
    from app.models.user import User
    
    manager = User(
        username="manager",
        hashed_password=get_password_hash("manager123"),
        role=UserRole.MANAGER,
        is_active=True
    )
    db_session.add(manager)
    db_session.commit()
    
    response = client.post(
        "/auth/login",
        data={"username": "manager", "password": "manager123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_asset(client, admin_token):
    """Create a sample asset for testing."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/assets/create",
        json={
            "name": "Test Scanner",
            "description": "Test asset",
            "status": "Available",
            "location": "Terminal A"
        },
        headers=headers
    )
    return response.json()


# ========== GET /assets/{id} Tests ==========

def test_get_asset_with_auth(client, admin_token, sample_asset):
    """Test getting asset by ID with authentication."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/assets/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_asset["id"]
    assert data["name"] == "Test Scanner"


def test_get_asset_without_auth(client, sample_asset):
    """Test getting asset without authentication should fail."""
    response = client.get(f"/assets/{sample_asset['id']}")
    
    assert response.status_code == 401


def test_get_asset_with_invalid_token(client, sample_asset):
    """Test getting asset with invalid token should fail."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(f"/assets/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 401


def test_get_nonexistent_asset_with_auth(client, admin_token):
    """Test getting non-existent asset with auth returns 404."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/assets/999", headers=headers)
    
    assert response.status_code == 404


# ========== POST /assets/create Tests ==========

def test_create_asset_with_auth(client, staff_token):
    """Test creating asset with authentication."""
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = client.post(
        "/assets/create",
        json={
            "name": "New Scanner",
            "description": "A new scanner",
            "status": "Available",
            "location": "Terminal B"
        },
        headers=headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Scanner"
    assert "id" in data
    assert "created_at" in data


def test_create_asset_without_auth(client):
    """Test creating asset without authentication should fail."""
    response = client.post(
        "/assets/create",
        json={
            "name": "New Scanner",
            "status": "Available"
        }
    )
    
    assert response.status_code == 401


def test_create_asset_invalid_data(client, staff_token):
    """Test creating asset with invalid data."""
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = client.post(
        "/assets/create",
        json={
            # Missing required field "name"
            "status": "Available"
        },
        headers=headers
    )
    
    assert response.status_code == 422  # Validation error


# ========== PUT /assets/update/{id} Tests ==========

def test_update_asset_as_manager(client, manager_token, sample_asset):
    """Test updating asset as manager (should work)."""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={
            "name": "Updated Scanner",
            "status": "In Use"
        },
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Scanner"
    assert data["status"] == "In Use"


def test_update_asset_as_admin(client, admin_token, sample_asset):
    """Test updating asset as admin (should work)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"status": "Needs Repair"},
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "Needs Repair"


def test_update_asset_as_staff_fails(client, staff_token, sample_asset):
    """Test that staff cannot update assets."""
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated"},
        headers=headers
    )
    
    assert response.status_code == 403
    assert "denied" in response.json()["detail"].lower() or "role" in response.json()["detail"].lower()


def test_update_asset_without_auth(client, sample_asset):
    """Test updating asset without authentication should fail."""
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated"}
    )
    
    assert response.status_code == 401


def test_update_nonexistent_asset(client, manager_token):
    """Test updating non-existent asset returns 404."""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = client.put(
        "/assets/update/999",
        json={"name": "Updated"},
        headers=headers
    )
    
    assert response.status_code == 404


# ========== DELETE /assets/delete/{id} Tests ==========

def test_delete_asset_as_admin(client, admin_token, sample_asset):
    """Test deleting asset as admin (should work)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(
        f"/assets/delete/{sample_asset['id']}",
        headers=headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/assets/{sample_asset['id']}", headers=headers)
    assert get_response.status_code == 404


def test_delete_asset_as_manager_fails(client, manager_token, sample_asset):
    """Test that manager cannot delete assets."""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = client.delete(
        f"/assets/delete/{sample_asset['id']}",
        headers=headers
    )
    
    assert response.status_code == 403
    assert "denied" in response.json()["detail"].lower() or "role" in response.json()["detail"].lower()


def test_delete_asset_as_staff_fails(client, staff_token, sample_asset):
    """Test that staff cannot delete assets."""
    headers = {"Authorization": f"Bearer {staff_token}"}
    response = client.delete(
        f"/assets/delete/{sample_asset['id']}",
        headers=headers
    )
    
    assert response.status_code == 403


def test_delete_asset_without_auth(client, sample_asset):
    """Test deleting asset without authentication should fail."""
    response = client.delete(f"/assets/delete/{sample_asset['id']}")
    
    assert response.status_code == 401


def test_delete_nonexistent_asset(client, admin_token):
    """Test deleting non-existent asset returns 404."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/assets/delete/999", headers=headers)
    
    assert response.status_code == 404


# ========== GET /assets/ Tests (Public) ==========

def test_get_assets_list_public(client, sample_asset):
    """Test that asset list is public (no auth required)."""
    response = client.get("/assets/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(a["id"] == sample_asset["id"] for a in data)


def test_get_assets_list_with_auth(client, admin_token, sample_asset):
    """Test that asset list works with auth too."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/assets/", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


# ========== Role-Based Access Control Tests ==========

def test_role_hierarchy(client, db_session):
    """Test that role hierarchy works correctly."""
    # Create users with different roles
    from app.core.security import get_password_hash
    from app.models.user import User
    
    viewer = User(
        username="viewer",
        hashed_password=get_password_hash("viewer123"),
        role=UserRole.VIEWER,
        is_active=True
    )
    staff = User(
        username="staff",
        hashed_password=get_password_hash("staff123"),
        role=UserRole.STAFF,
        is_active=True
    )
    manager = User(
        username="manager",
        hashed_password=get_password_hash("manager123"),
        role=UserRole.MANAGER,
        is_active=True
    )
    admin = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    for user in [viewer, staff, manager, admin]:
        db_session.add(user)
    db_session.commit()
    
    # Create an asset
    admin_login = client.post("/auth/login", data={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    asset_response = client.post(
        "/assets/create",
        json={"name": "Test Asset", "status": "Available"},
        headers=admin_headers
    )
    asset_id = asset_response.json()["id"]
    
    # Test each role's permissions
    roles_permissions = [
        ("viewer", UserRole.VIEWER, False, False, False, False),  # Can't create, update, delete
        ("staff", UserRole.STAFF, True, False, False, False),    # Can create only
        ("manager", UserRole.MANAGER, True, True, False, False), # Can create and update
        ("admin", UserRole.ADMIN, True, True, True, True),        # Can do everything
    ]
    
    for username, role, can_create, can_update, can_delete, _ in roles_permissions:
        login_resp = client.post("/auth/login", data={"username": username, "password": f"{username}123"})
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test create
        create_resp = client.post(
            "/assets/create",
            json={"name": f"Asset by {username}", "status": "Available"},
            headers=headers
        )
        if can_create:
            assert create_resp.status_code == 201, f"{role.value} should be able to create"
        else:
            assert create_resp.status_code == 403, f"{role.value} should not be able to create (403 Forbidden - authenticated but lacks permission)"
        
        # Test update
        update_resp = client.put(
            f"/assets/update/{asset_id}",
            json={"name": "Updated"},
            headers=headers
        )
        if can_update:
            assert update_resp.status_code == 200, f"{role.value} should be able to update"
        else:
            assert update_resp.status_code in [401, 403], f"{role.value} should not be able to update"
        
        # Test delete
        delete_resp = client.delete(f"/assets/delete/{asset_id}", headers=headers)
        if can_delete:
            assert delete_resp.status_code == 204, f"{role.value} should be able to delete"
        else:
            assert delete_resp.status_code in [401, 403], f"{role.value} should not be able to delete"

