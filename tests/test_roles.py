"""
Tests for role-based access control.
Tests that different user roles have correct permissions.
"""
import pytest
from app.models.user import UserRole


@pytest.fixture
def create_user_with_role(client, db_session):
    """Helper to create a user with a specific role."""
    def _create_user(username, role, password="test123"):
        from app.core.security import get_password_hash
        from app.models.user import User
        
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role=role,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Login and get token
        login_resp = client.post("/auth/login", data={"username": username, "password": password})
        token = login_resp.json()["access_token"]
        return token, user
    
    return _create_user


@pytest.fixture
def sample_asset(client, db_session):
    """Create a sample asset for role testing."""
    from app.core.security import get_password_hash
    from app.models.user import User
    
    # Create admin to create asset
    admin = User(
        username="admin_creator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Login as admin
    login_resp = client.post("/auth/login", data={"username": "admin_creator", "password": "admin123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create asset
    resp = client.post(
        "/assets/create",
        json={"name": "Test Asset", "status": "Available"},
        headers=headers
    )
    return resp.json()


# ========== Viewer Role Tests ==========

def test_viewer_cannot_create_asset(client, create_user_with_role):
    """Test that viewer role cannot create assets."""
    token, _ = create_user_with_role("viewer", UserRole.VIEWER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/assets/create",
        json={"name": "New Asset", "status": "Available"},
        headers=headers
    )
    
    assert response.status_code == 403  # Forbidden - authenticated but lacks permission
    assert "Access denied" in response.json()["detail"] or "required roles" in response.json()["detail"].lower()


def test_viewer_cannot_update_asset(client, create_user_with_role, sample_asset):
    """Test that viewer role cannot update assets."""
    token, _ = create_user_with_role("viewer", UserRole.VIEWER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated"},
        headers=headers
    )
    
    assert response.status_code == 403  # Forbidden - authenticated but lacks permission
    assert "Access denied" in response.json()["detail"] or "required roles" in response.json()["detail"].lower()


def test_viewer_cannot_delete_asset(client, create_user_with_role, sample_asset):
    """Test that viewer role cannot delete assets."""
    token, _ = create_user_with_role("viewer", UserRole.VIEWER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/assets/delete/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 403  # Forbidden - authenticated but lacks permission
    assert "Access denied" in response.json()["detail"] or "required roles" in response.json()["detail"].lower()


# ========== Staff Role Tests ==========

def test_staff_can_create_asset(client, create_user_with_role):
    """Test that staff role can create assets."""
    token, _ = create_user_with_role("staff", UserRole.STAFF)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/assets/create",
        json={"name": "Staff Created Asset", "status": "Available"},
        headers=headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Staff Created Asset"


def test_staff_cannot_update_asset(client, create_user_with_role, sample_asset):
    """Test that staff role cannot update assets."""
    token, _ = create_user_with_role("staff", UserRole.STAFF)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated by Staff"},
        headers=headers
    )
    
    assert response.status_code == 403
    assert "denied" in response.json()["detail"].lower() or "role" in response.json()["detail"].lower()


def test_staff_cannot_delete_asset(client, create_user_with_role, sample_asset):
    """Test that staff role cannot delete assets."""
    token, _ = create_user_with_role("staff", UserRole.STAFF)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/assets/delete/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 403


# ========== Manager Role Tests ==========

def test_manager_can_create_asset(client, create_user_with_role):
    """Test that manager role can create assets."""
    token, _ = create_user_with_role("manager", UserRole.MANAGER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/assets/create",
        json={"name": "Manager Created Asset", "status": "Available"},
        headers=headers
    )
    
    assert response.status_code == 201


def test_manager_can_update_asset(client, create_user_with_role, sample_asset):
    """Test that manager role can update assets."""
    token, _ = create_user_with_role("manager", UserRole.MANAGER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated by Manager", "status": "In Use"},
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated by Manager"


def test_manager_cannot_delete_asset(client, create_user_with_role, sample_asset):
    """Test that manager role cannot delete assets."""
    token, _ = create_user_with_role("manager", UserRole.MANAGER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/assets/delete/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 403


# ========== Admin Role Tests ==========

def test_admin_can_create_asset(client, create_user_with_role):
    """Test that admin role can create assets."""
    token, _ = create_user_with_role("admin", UserRole.ADMIN)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/assets/create",
        json={"name": "Admin Created Asset", "status": "Available"},
        headers=headers
    )
    
    assert response.status_code == 201


def test_admin_can_update_asset(client, create_user_with_role, sample_asset):
    """Test that admin role can update assets."""
    token, _ = create_user_with_role("admin", UserRole.ADMIN)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put(
        f"/assets/update/{sample_asset['id']}",
        json={"name": "Updated by Admin"},
        headers=headers
    )
    
    assert response.status_code == 200


def test_admin_can_delete_asset(client, create_user_with_role, sample_asset):
    """Test that admin role can delete assets."""
    token, _ = create_user_with_role("admin", UserRole.ADMIN)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/assets/delete/{sample_asset['id']}", headers=headers)
    
    assert response.status_code == 204


# ========== Permission Summary Test ==========

def test_role_permissions_summary(client, db_session):
    """Test all role permissions in one comprehensive test."""
    from app.core.security import get_password_hash
    from app.models.user import User
    
    # Create users with all roles
    roles = [
        ("viewer", UserRole.VIEWER),
        ("staff", UserRole.STAFF),
        ("manager", UserRole.MANAGER),
        ("admin", UserRole.ADMIN)
    ]
    
    tokens = {}
    for username, role in roles:
        user = User(
            username=username,
            hashed_password=get_password_hash("test123"),
            role=role,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        login_resp = client.post("/auth/login", data={"username": username, "password": "test123"})
        tokens[role] = login_resp.json()["access_token"]
    
    # Create an asset for testing
    admin_headers = {"Authorization": f"Bearer {tokens[UserRole.ADMIN]}"}
    asset_resp = client.post(
        "/assets/create",
        json={"name": "Permission Test Asset", "status": "Available"},
        headers=admin_headers
    )
    asset_id = asset_resp.json()["id"]
    
    # Expected permissions: (can_create, can_update, can_delete)
    expected_permissions = {
        UserRole.VIEWER: (False, False, False),
        UserRole.STAFF: (True, False, False),
        UserRole.MANAGER: (True, True, False),
        UserRole.ADMIN: (True, True, True),
    }
    
    for role, (can_create, can_update, can_delete) in expected_permissions.items():
        headers = {"Authorization": f"Bearer {tokens[role]}"}
        
        # Test create
        create_resp = client.post(
            "/assets/create",
            json={"name": f"Asset by {role.value}", "status": "Available"},
            headers=headers
        )
        if can_create:
            assert create_resp.status_code == 201, f"{role.value} should create"
        else:
            assert create_resp.status_code in [401, 403], f"{role.value} should not create"
        
        # Test update
        update_resp = client.put(
            f"/assets/update/{asset_id}",
            json={"name": "Updated"},
            headers=headers
        )
        if can_update:
            assert update_resp.status_code == 200, f"{role.value} should update"
        else:
            assert update_resp.status_code in [401, 403], f"{role.value} should not update"
        
        # Test delete (recreate asset if deleted)
        if asset_resp.status_code != 201:  # Asset was deleted, recreate
            asset_resp = client.post(
                "/assets/create",
                json={"name": "Permission Test Asset", "status": "Available"},
                headers=admin_headers
            )
            asset_id = asset_resp.json()["id"]
        
        delete_resp = client.delete(f"/assets/delete/{asset_id}", headers=headers)
        if can_delete:
            assert delete_resp.status_code == 204, f"{role.value} should delete"
        else:
            assert delete_resp.status_code in [401, 403], f"{role.value} should not delete"

