from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AssetStatus(str, enum.Enum):
    """Enumeration for asset status values."""
    AVAILABLE = "Available"
    IN_USE = "In Use"
    NEEDS_REPAIR = "Needs Repair"
    UNKNOWN = "Unknown"


class Asset(Base):
    """SQLAlchemy model for Asset table."""
    
    __tablename__ = "Assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000))
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.UNKNOWN)
    location = Column(String(255))
    asset_type = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', status='{self.status}')>"
