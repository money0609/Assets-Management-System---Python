from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    """Base schema for User."""
    username: str = Field(..., min_length=3, max_length=25)
    first_name: str = Field(..., min_length=2, max_length=25)
    last_name: str = Field(..., min_length=1, max_length=25)
    role: UserRole = Field(default=UserRole.VIEWER)
    is_active: bool = Field(default=True)

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=4, max_length=72, description="Password must be 4-72 characters (bcrypt limit)")

class UserUpdate(BaseModel):
    """Schema for updating user (all fields optional)."""
    first_name: Optional[str] = Field(None, min_length=2, max_length=25)
    last_name: Optional[str] = Field(None, min_length=1, max_length=25)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for login request."""
    username: str
    password: str

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None