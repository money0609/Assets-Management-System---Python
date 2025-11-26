from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.asset import AssetStatus


class AssetBase(BaseModel):
    """Base schema for Asset with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Asset name")
    description: Optional[str] = Field(None, max_length=1000, description="Asset description")
    status: AssetStatus = Field(default=AssetStatus.UNKNOWN, description="Current asset status")
    location: Optional[str] = Field(None, max_length=255, description="Asset location")
    type: Optional[str] = Field(None, max_length=100, description="Type of asset")


class AssetCreate(AssetBase):
    """Schema for creating a new asset."""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[AssetStatus] = None
    location: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=100)


class AssetResponse(AssetBase):
    """Schema for asset response with read-only fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
