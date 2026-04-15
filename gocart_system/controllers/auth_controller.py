"""
Authentication API endpoints controller.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, status
from typing import Dict, Optional
from ..requests.auth_requests import (
    RegisterRequest, LoginRequest, TokenResponse, AuthResponse,
    RefreshTokenRequest, UserResponse, LogoutRequest
)
from ..services.auth_service import AuthenticationService
from ..services.auth_logger import auth_logger
from ..services.auth_middleware import verify_jwt_token, verify_rbac_role
from ..services.jwt_service import JWTService, JWTConfig
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
auth_service = AuthenticationService()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, user_data: RegisterRequest):
    """
    Register a new user.
    
    Args:
        request: FastAPI request object
        user_data: Registration data
    
    Returns:
        Registration response with user info
    """
    ip_address = request.client.host if request.client else None
    
    success, user, message = auth_service.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role="user"
    )
    
    auth_logger.log_registration(
        username=user_data.username,
        email=user_data.email,
        success=success,
        ip_address=ip_address,
        details=message
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return AuthResponse(
        success=True,
        message=message,
        data={
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }
    )


@router.post("/login", response_model=Dict, status_code=status.HTTP_200_OK)
async def login(request: Request, login_data: LoginRequest):
    """
    Login user and return tokens.
    
    Args:
        request: FastAPI request object
        login_data: Login credentials
    
    Returns:
        Access and refresh tokens
    """
    ip_address = request.client.host if request.client else None
    
    success, tokens, message = auth_service.login(
        username=login_data.username,
        password=login_data.password
    )
    
    auth_logger.log_login_attempt(
        username=login_data.username,
        success=success,
        ip_address=ip_address,
        details=message
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "data": {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    }


@router.post("/refresh", response_model=Dict, status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, token_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Args:
        request: FastAPI request object
        token_data: Refresh token data
    
    Returns:
        New access token
    """
    ip_address = request.client.host if request.client else None
    
    success, new_token, message = auth_service.refresh_access_token(
        token_data.refresh_token
    )
    
    # Extract user info from token to log
    is_valid, payload, _ = JWTService.verify_token(token_data.refresh_token)
    if is_valid:
        auth_logger.log_token_refresh(
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            success=success,
            ip_address=ip_address,
            details=message
        )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "data": {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    }


@router.post("/logout", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    logout_data: LogoutRequest,
    user: dict = Depends(verify_jwt_token)
):
    """
    Logout user by invalidating refresh token.
    
    Args:
        request: FastAPI request object
        logout_data: Logout data (optional refresh token)
        user: Current authenticated user
    
    Returns:
        Logout confirmation
    """
    ip_address = request.client.host if request.client else None
    refresh_token = logout_data.refresh_token
    
    if not refresh_token:
        # Token to invalidate should be provided by client
        return AuthResponse(
            success=True,
            message="Logout successful. Please discard your tokens."
        )
    
    success, message = auth_service.logout(refresh_token)
    
    auth_logger.log_logout(
        user_id=user.get("user_id"),
        username=user.get("username"),
        ip_address=ip_address,
        details=message
    )
    
    return AuthResponse(
        success=success,
        message=message
    )


@router.get("/me", response_model=Dict, status_code=status.HTTP_200_OK)
async def get_current_user(
    request: Request,
    user: dict = Depends(verify_jwt_token)
):
    """
    Get current authenticated user info.
    
    Args:
        request: FastAPI request object
        user: Current authenticated user from token
    
    Returns:
        Current user information
    """
    user_obj = auth_service.get_user_by_id(user.get("user_id"))
    
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "message": "User info retrieved successfully",
        "data": user_obj.to_dict()
    }


@router.get("/admin/users", response_model=Dict, status_code=status.HTTP_200_OK)
async def get_all_users(
    request: Request,
    admin_user: dict = Depends(verify_rbac_role("admin"))
):
    """
    Get all users (admin only).
    
    Args:
        request: FastAPI request object
        admin_user: Admin user (verified by RBAC)
    
    Returns:
        List of all users
    """
    try:
        import sqlite3
        import os
        from datetime import datetime
        
        db_path = os.getenv("DB_PATH", "gocart.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, role, is_active, created_at, last_login
            FROM users ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        users = [
            {
                "user_id": r[0],
                "username": r[1],
                "email": r[2],
                "role": r[3],
                "is_active": r[4],
                "created_at": r[5],
                "last_login": r[6],
            }
            for r in results
        ]
        
        return {
            "success": True,
            "message": f"Retrieved {len(users)} users",
            "data": users
        }
    
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )
