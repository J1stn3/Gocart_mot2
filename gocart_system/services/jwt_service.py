"""
JWT Token service for handling token generation and validation.
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class JWTConfig:
    """JWT configuration."""
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenPayload:
    """Token payload data class."""
    
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        role: str,
        token_type: str = "access",
        issued_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.token_type = token_type
        self.issued_at = issued_at or datetime.utcnow()
        self.expires_at = expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token payload to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "token_type": self.token_type,
            "iat": self.issued_at,
            "exp": self.expires_at,
        }


class JWTService:
    """JWT Token service for creating and validating tokens."""
    
    @staticmethod
    def create_access_token(user_id: int, username: str, email: str, role: str) -> str:
        """
        Create an access token.
        
        Args:
            user_id: User ID
            username: Username
            email: Email
            role: User role
        
        Returns:
            JWT access token
        """
        expires_delta = timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        return JWTService._create_token(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            expires_delta=expires_delta,
            token_type="access",
        )
    
    @staticmethod
    def create_refresh_token(user_id: int, username: str, email: str, role: str) -> str:
        """
        Create a refresh token.
        
        Args:
            user_id: User ID
            username: Username
            email: Email
            role: User role
        
        Returns:
            JWT refresh token
        """
        expires_delta = timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        return JWTService._create_token(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            expires_delta=expires_delta,
            token_type="refresh",
        )
    
    @staticmethod
    def _create_token(
        user_id: int,
        username: str,
        email: str,
        role: str,
        expires_delta: timedelta,
        token_type: str,
    ) -> str:
        """
        Internal method to create a JWT token.
        
        Args:
            user_id: User ID
            username: Username
            email: Email
            role: User role
            expires_delta: Token expiration delta
            token_type: Type of token (access or refresh)
        
        Returns:
            JWT token
        """
        issued_at = datetime.utcnow()
        expires_at = issued_at + expires_delta
        
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "token_type": token_type,
            "iat": issued_at,
            "exp": expires_at,
        }
        
        token = jwt.encode(
            payload,
            JWTConfig.SECRET_KEY,
            algorithm=JWTConfig.ALGORITHM,
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
        
        Returns:
            Tuple of (is_valid, payload_dict, error_message)
        """
        try:
            payload = jwt.decode(
                token,
                JWTConfig.SECRET_KEY,
                algorithms=[JWTConfig.ALGORITHM],
            )
            return True, payload, None
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
        except Exception as e:
            return False, None, f"Token verification error: {str(e)}"
    
    @staticmethod
    def extract_token_from_header(auth_header: Optional[str]) -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Args:
            auth_header: Authorization header value
        
        Returns:
            Token string or None
        """
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    @staticmethod
    def create_token_pair(user_id: int, username: str, email: str, role: str) -> Dict[str, str]:
        """
        Create both access and refresh tokens.
        
        Args:
            user_id: User ID
            username: Username
            email: Email
            role: User role
        
        Returns:
            Dictionary containing both tokens
        """
        return {
            "access_token": JWTService.create_access_token(user_id, username, email, role),
            "refresh_token": JWTService.create_refresh_token(user_id, username, email, role),
            "token_type": "bearer",
        }
