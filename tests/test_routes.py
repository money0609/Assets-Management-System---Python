"""
Integration tests for API endpoints.
Tests API routes with real database interactions.
"""
import pytest
from app.models.asset import AssetStatus


def test_create_asset_endpoint(client):
    """Test POST /assets/ endpoint."""
    # Arrange
    asset_data = {
        "name": "Gate Scanner #5",
        "description": "Scanner for gate 5 operations",
        "status": "Available",
        "location": "Terminal A",
        "type": "Gate Equipment"
    }
    
    # Act
    response = client.post("/assets/", json=asset_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gate Scanner #5"
    assert data["description"] == "Scanner for gate 5 operations"
    assert data["status"] == "Available"
    assert data["location"] == "Terminal A"
    assert data["type"] == "Gate Equipment"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_asset_with_default_status(client):
    """Test POST /assets/ without status (should use default)."""
    # Arrange
    asset_data = {
        "name": "Test Asset"
        # status not provided
    }
    
    # Act
    response = client.post("/assets/", json=asset_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Unknown"  # Default status


def test_get_assets_endpoint_empty(client):
    """Test GET /assets/ when no assets exist."""
    # Act
    response = client.get("/assets/")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == []
    assert len(data) == 0


def test_get_assets_endpoint(client):
    """Test GET /assets/ endpoint."""
    # Arrange - create some assets first
    client.post("/assets/", json={"name": "Asset 1", "status": "Available"})
    client.post("/assets/", json={"name": "Asset 2", "status": "In Use"})
    client.post("/assets/", json={"name": "Asset 3", "status": "Needs Repair"})
    
    # Act
    response = client.get("/assets/")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Asset 1"
    assert data[1]["name"] == "Asset 2"
    assert data[2]["name"] == "Asset 3"


def test_get_assets_with_pagination(client):
    """Test GET /assets/ with pagination parameters."""
    # Arrange - create 5 assets
    for i in range(5):
        client.post("/assets/", json={"name": f"Asset {i+1}", "status": "Available"})
    
    # Act - get first 2
    response = client.get("/assets/?skip=0&limit=2")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Act - skip first 2, get next 2
    response = client.get("/assets/?skip=2&limit=2")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_asset_by_id_endpoint(client):
    """Test GET /assets/{id} endpoint."""
    # Arrange
    create_response = client.post("/assets/", json={
        "name": "Test Asset",
        "status": "Available",
        "location": "Terminal B"
    })
    asset_id = create_response.json()["id"]
    
    # Act
    response = client.get(f"/assets/{asset_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == asset_id
    assert data["name"] == "Test Asset"
    assert data["status"] == "Available"
    assert data["location"] == "Terminal B"


def test_get_asset_not_found(client):
    """Test GET /assets/{id} with non-existent ID."""
    # Act
    response = client.get("/assets/999")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
    assert "999" in data["detail"]


def test_update_asset_endpoint(client):
    """Test PUT /assets/{id} endpoint."""
    # Arrange
    create_response = client.post("/assets/", json={
        "name": "Old Name",
        "status": "Available",
        "location": "Terminal A"
    })
    asset_id = create_response.json()["id"]
    update_data = {
        "name": "New Name",
        "status": "In Use",
        "location": "Terminal B"
    }
    
    # Act
    response = client.put(f"/assets/{asset_id}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == asset_id
    assert data["name"] == "New Name"
    assert data["status"] == "In Use"
    assert data["location"] == "Terminal B"


def test_update_asset_partial(client):
    """Test PUT /assets/{id} with partial update."""
    # Arrange
    create_response = client.post("/assets/", json={
        "name": "Original Name",
        "status": "Available",
        "location": "Terminal A",
        "description": "Original description"
    })
    asset_id = create_response.json()["id"]
    update_data = {
        "status": "In Use"
        # Only updating status
    }
    
    # Act
    response = client.put(f"/assets/{asset_id}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Original Name"  # Unchanged
    assert data["status"] == "In Use"  # Changed
    assert data["location"] == "Terminal A"  # Unchanged
    assert data["description"] == "Original description"  # Unchanged


def test_update_asset_not_found(client):
    """Test PUT /assets/{id} with non-existent ID."""
    # Arrange
    update_data = {"name": "New Name"}
    
    # Act
    response = client.put("/assets/999", json=update_data)
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_delete_asset_endpoint(client):
    """Test DELETE /assets/{id} endpoint."""
    # Arrange
    create_response = client.post("/assets/", json={
        "name": "To Delete",
        "status": "Available"
    })
    asset_id = create_response.json()["id"]
    
    # Act
    response = client.delete(f"/assets/{asset_id}")
    
    # Assert
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/assets/{asset_id}")
    assert get_response.status_code == 404


def test_delete_asset_not_found(client):
    """Test DELETE /assets/{id} with non-existent ID."""
    # Act
    response = client.delete("/assets/999")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_create_asset_validation_error(client):
    """Test POST /assets/ with invalid data."""
    # Arrange - missing required field (name)
    asset_data = {
        "status": "Available"
        # name is required but missing
    }
    
    # Act
    response = client.post("/assets/", json=asset_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_create_asset_invalid_status(client):
    """Test POST /assets/ with invalid status value."""
    # Arrange
    asset_data = {
        "name": "Test Asset",
        "status": "InvalidStatus"  # Not in enum
    }
    
    # Act
    response = client.post("/assets/", json=asset_data)
    
    # Assert
    assert response.status_code == 422  # Validation error

