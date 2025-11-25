from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.crud import asset as crud
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.core.limiter import limiter

router = APIRouter(prefix="/assets", tags=["assets"])


# Public route - anyone can view list of assets
@router.get("/", response_model=List[AssetResponse])
@limiter.limit("100/minute")
def get_assets(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get a list of assets with pagination (public)."""
    assets = crud.get_assets(db, skip=skip, limit=limit)
    print('***********assets: ', assets)
    return assets


# Protected route - requires authentication to view single asset
@router.get("/{asset_id}", response_model=AssetResponse)
@limiter.limit("100/minute")
def get_asset(
    request: Request,
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a single asset by ID (requires authentication)."""
    asset = crud.get_asset(db, asset_id=asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    return asset


# Protected route - requires staff, manager, or admin role to create (viewers cannot create)
@router.post("/create", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_asset(
    request: Request,
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]))
):
    """Create a new asset (requires staff, manager, or admin role - viewers cannot create)."""
    return crud.create_asset(db=db, asset=asset)


# Protected route - requires manager or admin role to update
@router.put("/update/{asset_id}", response_model=AssetResponse)
@limiter.limit("30/minute")
def update_asset(
    request: Request,
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN]))
):
    """Update an existing asset (requires manager or admin role)."""
    asset = crud.update_asset(db, asset_id=asset_id, asset_update=asset_update)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    return asset


# Protected route - requires admin role only to delete
@router.delete("/delete/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_asset(
    request: Request,
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete an asset (requires admin role)."""
    deleted = crud.delete_asset(db, asset_id=asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    return None
