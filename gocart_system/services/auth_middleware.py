"""
JWT middleware and RBAC decorators for API security.
"""
from fastapi import Request, HTTPException, status, Depends
from typing import Optional, Callable, List
from functools import wraps
from .jwt_service import JWTService
from .auth_logger import auth_logger
import logging

logger = logging.getLogger(__name__)


class RBACVerifier:
    """Role-Based Access Control verifier."""
    
    ROLE_HIERARCHY = {
        "admin": ["admin", "staff", "user"],
        "staff": ["staff", "user"],
        "user": ["user"],
    }
    
    @staticmethod
    def verify_role(required_roles: List[str], user_role: str) -> bool:
        """
        Verify if user role has access.
        
        Args:
            required_roles: List of required roles
            user_role: User's actual role
        
        Returns:
            True if user has required role
        """
        allowed_roles = RBACVerifier.ROLE_HIERARCHY.get(user_role, [])
        return user_role in required_roles or any(r in allowed_roles for r in required_roles)


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication on endpoints.
    
    Usage:
        @require_auth
        def my_endpoint(request: Request):
            pass
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = JWTService.extract_token_from_header(auth_header)
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        is_valid, payload, error = JWTService.verify_token(token)
        
        if not is_valid:
            auth_logger.log_unauthorized_access(
                endpoint=request.url.path,
                reason=error or "Invalid token",
                ip_address=request.client.host if request.client else None,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error or "Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        request.state.user = payload
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_roles(required_roles: List[str]) -> Callable:
    """
    Decorator to require specific roles on endpoints.
    
    Usage:
        @require_roles(["admin", "staff"])
        def admin_endpoint(request: Request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # First check authentication
            auth_header = request.headers.get("Authorization")
            token = JWTService.extract_token_from_header(auth_header)
            
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            is_valid, payload, error = JWTService.verify_token(token)
            
            if not is_valid:
                auth_logger.log_unauthorized_access(
                    endpoint=request.url.path,
                    reason=error or "Invalid token",
                    ip_address=request.client.host if request.client else None,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error or "Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check role
            user_role = payload.get("role", "user")
            if not RBACVerifier.verify_role(required_roles, user_role):
                auth_logger.log_unauthorized_access(
                    endpoint=request.url.path,
                    reason=f"Insufficient permissions. Required roles: {required_roles}, User role: {user_role}",
                    ip_address=request.client.host if request.client else None,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles}",
                )
            
            request.state.user = payload
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


async def verify_jwt_token(request: Request) -> dict:
    """
    Dependency function for FastAPI to verify JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(verify_jwt_token)):
            pass
    
    Args:
        request: FastAPI request object
    
    Returns:
        Decoded token payload
    """
    auth_header = request.headers.get("Authorization")
    token = JWTService.extract_token_from_header(auth_header)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid, payload, error = JWTService.verify_token(token)
    
    if not is_valid:
        auth_logger.log_unauthorized_access(
            endpoint=request.url.path,
            reason=error or "Invalid token",
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def verify_rbac_role(*required_roles: str):
    """
    Dependency function for FastAPI to verify user role.
    
    Usage:
        @app.get("/admin")
        async def admin_route(
            user: dict = Depends(verify_jwt_token),
            _: dict = Depends(verify_rbac_role("admin", "staff"))
        ):
            pass
    
    Args:
        *required_roles: Variable length argument list of required roles
    
    Returns:
        Dependency function
    """
    async def verify(user: dict = Depends(verify_jwt_token)) -> dict:
        user_role = user.get("role", "user")
        
        if not RBACVerifier.verify_role(list(required_roles), user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}",
            )
        
        return user
    
    return verify
