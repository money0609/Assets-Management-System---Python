"""
End-to-end tests for complete user workflows.
Tests the entire application flow from start to finish.
"""
import pytest


def test_complete_asset_lifecycle(client):
    """Test complete workflow: Create → Read → Update → Delete."""
    
    # 1. CREATE: Create a new asset
    create_response = client.post("/assets/", json={
        "name": "Gate Scanner #5",
        "description": "Scanner for gate 5 operations",
        "status": "Available",
        "location": "Terminal A",
        "asset_type": "Gate Equipment"
    })
    assert create_response.status_code == 201
    asset_data = create_response.json()
    asset_id = asset_data["id"]
    
    # Verify created asset
    assert asset_data["name"] == "Gate Scanner #5"
    assert asset_data["status"] == "Available"
    assert asset_data["location"] == "Terminal A"
    assert asset_data["asset_type"] == "Gate Equipment"
    assert "created_at" in asset_data
    assert "updated_at" in asset_data
    
    # 2. READ: Get the asset we just created
    get_response = client.get(f"/assets/{asset_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["id"] == asset_id
    assert retrieved_data["name"] == "Gate Scanner #5"
    assert retrieved_data["status"] == "Available"
    
    # 3. READ ALL: Verify it appears in the list
    list_response = client.get("/assets/")
    assert list_response.status_code == 200
    assets = list_response.json()
    assert len(assets) == 1
    assert assets[0]["id"] == asset_id
    assert assets[0]["name"] == "Gate Scanner #5"
    
    # 4. UPDATE: Change the asset status and location
    update_response = client.put(f"/assets/{asset_id}", json={
        "status": "In Use",
        "location": "Terminal B"
    })
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["status"] == "In Use"
    assert updated_data["location"] == "Terminal B"
    assert updated_data["name"] == "Gate Scanner #5"  # Name unchanged
    assert updated_data["description"] == "Scanner for gate 5 operations"  # Description unchanged
    
    # 5. VERIFY UPDATE: Get the asset again to confirm update
    get_updated_response = client.get(f"/assets/{asset_id}")
    assert get_updated_response.status_code == 200
    verify_data = get_updated_response.json()
    assert verify_data["status"] == "In Use"
    assert verify_data["location"] == "Terminal B"
    
    # 6. DELETE: Remove the asset
    delete_response = client.delete(f"/assets/{asset_id}")
    assert delete_response.status_code == 204
    
    # 7. VERIFY DELETION: Confirm it's deleted
    get_deleted_response = client.get(f"/assets/{asset_id}")
    assert get_deleted_response.status_code == 404
    
    # 8. VERIFY LIST: Confirm it's removed from the list
    final_list_response = client.get("/assets/")
    assert final_list_response.status_code == 200
    final_assets = final_list_response.json()
    assert len(final_assets) == 0


def test_asset_workflow_with_multiple_assets(client):
    """Test working with multiple assets simultaneously."""
    
    # Create multiple assets
    asset1_response = client.post("/assets/", json={
        "name": "Maintenance Cart #1",
        "status": "Available",
        "location": "Terminal A",
        "asset_type": "Maintenance Tool"
    })
    asset2_response = client.post("/assets/", json={
        "name": "Baggage Conveyor",
        "status": "In Use",
        "location": "Terminal B",
        "asset_type": "Gate Equipment"
    })
    asset3_response = client.post("/assets/", json={
        "name": "Broken Scanner",
        "status": "Needs Repair",
        "location": "Terminal C",
        "asset_type": "Gate Equipment"
    })
    
    asset1 = asset1_response.json()
    asset2 = asset2_response.json()
    asset3 = asset3_response.json()
    
    # Get all assets
    response = client.get("/assets/")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) == 3
    
    # Verify all assets are present
    asset_ids = [a["id"] for a in assets]
    assert asset1["id"] in asset_ids
    assert asset2["id"] in asset_ids
    assert asset3["id"] in asset_ids
    
    # Update one asset
    update_response = client.put(f"/assets/{asset2['id']}", json={
        "status": "Available"
    })
    assert update_response.status_code == 200
    updated_asset2 = update_response.json()
    assert updated_asset2["status"] == "Available"
    
    # Verify other assets unchanged
    get_asset1 = client.get(f"/assets/{asset1['id']}").json()
    get_asset3 = client.get(f"/assets/{asset3['id']}").json()
    assert get_asset1["status"] == "Available"  # Unchanged
    assert get_asset3["status"] == "Needs Repair"  # Unchanged
    
    # Delete one asset
    delete_response = client.delete(f"/assets/{asset2['id']}")
    assert delete_response.status_code == 204
    
    # Verify remaining assets
    final_response = client.get("/assets/")
    final_assets = final_response.json()
    assert len(final_assets) == 2
    remaining_ids = [a["id"] for a in final_assets]
    assert asset1["id"] in remaining_ids
    assert asset3["id"] in remaining_ids
    assert asset2["id"] not in remaining_ids


def test_asset_status_workflow(client):
    """Test asset status transitions."""
    
    # Create asset as Available
    create_response = client.post("/assets/", json={
        "name": "Test Asset",
        "status": "Available"
    })
    asset_id = create_response.json()["id"]
    
    # Transition: Available → In Use
    update1 = client.put(f"/assets/{asset_id}", json={"status": "In Use"})
    assert update1.json()["status"] == "In Use"
    
    # Transition: In Use → Needs Repair
    update2 = client.put(f"/assets/{asset_id}", json={"status": "Needs Repair"})
    assert update2.json()["status"] == "Needs Repair"
    
    # Transition: Needs Repair → Available (after repair)
    update3 = client.put(f"/assets/{asset_id}", json={"status": "Available"})
    assert update3.json()["status"] == "Available"
    
    # Verify final state
    final = client.get(f"/assets/{asset_id}").json()
    assert final["status"] == "Available"


def test_pagination_workflow(client):
    """Test pagination through multiple assets."""
    
    # Create 10 assets
    for i in range(10):
        client.post("/assets/", json={
            "name": f"Asset {i+1}",
            "status": "Available"
        })
    
    # Get first page (5 items)
    page1 = client.get("/assets/?skip=0&limit=5").json()
    assert len(page1) == 5
    assert page1[0]["name"] == "Asset 1"
    assert page1[4]["name"] == "Asset 5"
    
    # Get second page (5 items)
    page2 = client.get("/assets/?skip=5&limit=5").json()
    assert len(page2) == 5
    assert page2[0]["name"] == "Asset 6"
    assert page2[4]["name"] == "Asset 10"
    
    # Get third page (should be empty)
    page3 = client.get("/assets/?skip=10&limit=5").json()
    assert len(page3) == 0


def test_error_handling_workflow(client):
    """Test error handling in various scenarios."""
    
    # Try to get non-existent asset
    get_response = client.get("/assets/999")
    assert get_response.status_code == 404
    
    # Try to update non-existent asset
    update_response = client.put("/assets/999", json={"name": "New Name"})
    assert update_response.status_code == 404
    
    # Try to delete non-existent asset
    delete_response = client.delete("/assets/999")
    assert delete_response.status_code == 404
    
    # Create an asset first
    create_response = client.post("/assets/", json={
        "name": "Test Asset",
        "status": "Available"
    })
    asset_id = create_response.json()["id"]
    
    # Now operations should work
    get_valid = client.get(f"/assets/{asset_id}")
    assert get_valid.status_code == 200
    
    update_valid = client.put(f"/assets/{asset_id}", json={"status": "In Use"})
    assert update_valid.status_code == 200
    
    delete_valid = client.delete(f"/assets/{asset_id}")
    assert delete_valid.status_code == 204

