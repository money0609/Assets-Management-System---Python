from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


def get_asset(db: Session, asset_id: int) -> Optional[Asset]:
    """Get a single asset by ID."""
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_assets(db: Session, skip: int = 0, limit: int = 100) -> List[Asset]:
    """Get a list of assets with pagination."""
    return db.query(Asset).offset(skip).limit(limit).all()


def create_asset(db: Session, asset: AssetCreate) -> Asset:
    """Create a new asset."""
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def update_asset(db: Session, asset_id: int, asset_update: AssetUpdate) -> Optional[Asset]:
    """Update an existing asset."""
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        return None
    
    # Get only the fields that were provided (exclude unset)
    update_data = asset_update.model_dump(exclude_unset=True)
    
    # Update each field that was provided
    for field, value in update_data.items():
        setattr(db_asset, field, value)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset


def delete_asset(db: Session, asset_id: int) -> bool:
    """Delete an asset by ID. Returns True if deleted, False if not found."""
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        return False
    
    db.delete(db_asset)
    db.commit()
    return True

