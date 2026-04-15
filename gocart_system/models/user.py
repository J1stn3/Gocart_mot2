from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"


class User:
    """User model representing a system user."""
    
    def __init__(
        self,
        user_id: Optional[int] = None,
        username: str = None,
        email: str = None,
        password_hash: str = None,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        failed_login_attempts: int = 0,
        is_locked: bool = False,
        locked_until: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.is_locked = is_locked
        self.locked_until = locked_until

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, role={self.role.value})>"
