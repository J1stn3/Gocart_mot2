"""
Request and response models for authentication endpoints.
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v


class LoginRequest(BaseModel):
    """User login request model."""
    username: str = Field(..., min_length=3)
    password: str = Field(...)


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(...)


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response model."""
    user_id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class AuthResponse(BaseModel):
    """Authentication response model."""
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    error_code: Optional[str] = None


class LogoutRequest(BaseModel):
    """Logout request model."""
    refresh_token: Optional[str] = None
