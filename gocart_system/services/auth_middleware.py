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


async def _validate_token(request: Request) -> dict:
    """Validate JWT token from request and return payload. Raises HTTPException on failure."""
    auth_header = request.headers.get("Authorization")
    token = JWTService.extract_token_from_header(auth_header)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required and cannot be omitted.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_valid, payload, error = JWTService.verify_token(token)

    if not is_valid:
        reason = error or "Invalid token"
        auth_logger.log_unauthorized_access(
            endpoint=request.url.path,
            reason=reason,
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unauthorized token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("token_type") != "access":
        auth_logger.log_unauthorized_access(
            endpoint=request.url.path,
            reason="Invalid token type",
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unauthorized token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    required_fields = ["user_id", "username", "email", "role"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        auth_logger.log_unauthorized_access(
            endpoint=request.url.path,
            reason=f"Missing required claims: {', '.join(missing)}",
            ip_address=request.client.host if request.client else None,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unauthorized token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


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
        payload = await _validate_token(request)
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
            payload = await _validate_token(request)
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
    return await _validate_token(request)


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
