"""
Unit tests for CRUD operations.
Tests individual CRUD functions in isolation.
"""
import pytest
from app.models.asset import Asset, AssetStatus
from app.crud.asset import (
    create_asset,
    get_asset,
    get_assets,
    update_asset,
    delete_asset
)
from app.schemas.asset import AssetCreate, AssetUpdate


def test_create_asset(db_session):
    """Test creating a new asset."""
    # Arrange
    asset_data = AssetCreate(
        name="Test Scanner",
        description="A test scanner for gate operations",
        status=AssetStatus.AVAILABLE,
        location="Terminal A",
        type="Gate Equipment"
    )
    
    # Act
    created_asset = create_asset(db_session, asset_data)
    
    # Assert
    assert created_asset.id is not None
    assert created_asset.name == "Test Scanner"
    assert created_asset.description == "A test scanner for gate operations"
    assert created_asset.status == AssetStatus.AVAILABLE
    assert created_asset.location == "Terminal A"
    assert created_asset.type == "Gate Equipment"
    assert created_asset.created_at is not None
    assert created_asset.updated_at is not None


def test_create_asset_with_default_status(db_session):
    """Test creating asset without specifying status (should default to UNKNOWN)."""
    # Arrange
    asset_data = AssetCreate(
        name="Test Asset",
        description="Test description"
        # status not specified
    )
    
    # Act
    created_asset = create_asset(db_session, asset_data)
    
    # Assert
    assert created_asset.status == AssetStatus.UNKNOWN


def test_get_asset(db_session):
    """Test getting an asset by ID."""
    # Arrange - create an asset first
    asset_data = AssetCreate(
        name="Test Asset",
        description="Test description",
        status=AssetStatus.AVAILABLE
    )
    created = create_asset(db_session, asset_data)
    
    # Act
    retrieved = get_asset(db_session, created.id)
    
    # Assert
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Test Asset"
    assert retrieved.status == AssetStatus.AVAILABLE


def test_get_asset_not_found(db_session):
    """Test getting a non-existent asset returns None."""
    # Act
    result = get_asset(db_session, 999)
    
    # Assert
    assert result is None


def test_get_assets_empty(db_session):
    """Test getting assets when database is empty."""
    # Act
    assets = get_assets(db_session)
    
    # Assert
    assert assets == []
    assert len(assets) == 0


def test_get_assets_with_pagination(db_session):
    """Test getting a list of assets with pagination."""
    # Arrange - create multiple assets
    create_asset(db_session, AssetCreate(name="Asset 1", status=AssetStatus.AVAILABLE))
    create_asset(db_session, AssetCreate(name="Asset 2", status=AssetStatus.IN_USE))
    create_asset(db_session, AssetCreate(name="Asset 3", status=AssetStatus.NEEDS_REPAIR))
    
    # Act - get first 2
    assets = get_assets(db_session, skip=0, limit=2)
    
    # Assert
    assert len(assets) == 2
    
    # Act - skip first, get next 2
    assets_skip = get_assets(db_session, skip=1, limit=2)
    
    # Assert
    assert len(assets_skip) == 2
    assert assets_skip[0].name != assets[0].name


def test_get_assets_all(db_session):
    """Test getting all assets."""
    # Arrange - create multiple assets
    create_asset(db_session, AssetCreate(name="Asset 1", status=AssetStatus.AVAILABLE))
    create_asset(db_session, AssetCreate(name="Asset 2", status=AssetStatus.IN_USE))
    create_asset(db_session, AssetCreate(name="Asset 3", status=AssetStatus.NEEDS_REPAIR))
    
    # Act
    assets = get_assets(db_session, skip=0, limit=100)
    
    # Assert
    assert len(assets) == 3
    assert assets[0].name == "Asset 1"
    assert assets[1].name == "Asset 2"
    assert assets[2].name == "Asset 3"


def test_update_asset(db_session):
    """Test updating an existing asset."""
    # Arrange
    created = create_asset(
        db_session,
        AssetCreate(name="Old Name", status=AssetStatus.AVAILABLE, location="Terminal A")
    )
    update_data = AssetUpdate(
        name="New Name",
        status=AssetStatus.IN_USE,
        location="Terminal B"
    )
    
    # Act
    updated = update_asset(db_session, created.id, update_data)
    
    # Assert
    assert updated is not None
    assert updated.id == created.id
    assert updated.name == "New Name"
    assert updated.status == AssetStatus.IN_USE
    assert updated.location == "Terminal B"


def test_update_asset_partial(db_session):
    """Test partial update (only some fields)."""
    # Arrange
    created = create_asset(
        db_session,
        AssetCreate(
            name="Original Name",
            status=AssetStatus.AVAILABLE,
            location="Terminal A",
            description="Original description"
        )
    )
    update_data = AssetUpdate(
        status=AssetStatus.IN_USE
        # Only updating status, other fields should remain unchanged
    )
    
    # Act
    updated = update_asset(db_session, created.id, update_data)
    
    # Assert
    assert updated is not None
    assert updated.name == "Original Name"  # Unchanged
    assert updated.status == AssetStatus.IN_USE  # Changed
    assert updated.location == "Terminal A"  # Unchanged
    assert updated.description == "Original description"  # Unchanged


def test_update_asset_not_found(db_session):
    """Test updating a non-existent asset returns None."""
    # Arrange
    update_data = AssetUpdate(name="New Name")
    
    # Act
    result = update_asset(db_session, 999, update_data)
    
    # Assert
    assert result is None


def test_delete_asset(db_session):
    """Test deleting an asset."""
    # Arrange
    created = create_asset(
        db_session,
        AssetCreate(name="To Delete", status=AssetStatus.AVAILABLE)
    )
    asset_id = created.id
    
    # Act
    deleted = delete_asset(db_session, asset_id)
    
    # Assert
    assert deleted is True
    assert get_asset(db_session, asset_id) is None


def test_delete_asset_not_found(db_session):
    """Test deleting a non-existent asset returns False."""
    # Act
    deleted = delete_asset(db_session, 999)
    
    # Assert
    assert deleted is False

