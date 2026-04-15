"""
Password hashing and security utilities.
"""
import bcrypt
import os
from typing import Optional


class PasswordHasher:
    """Password hashing and verification using bcrypt."""
    
    @staticmethod
    def hash_password(password: str, rounds: Optional[int] = None) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            rounds: Number of bcrypt rounds (default from env or 12)
        
        Returns:
            Hashed password string
        """
        if rounds is None:
            rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
        
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        
        Args:
            password: Plain text password to verify
            password_hash: Hashed password to check against
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False


class PasswordValidator:
    """Password validation utilities."""
    
    MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        """
        Validate password against security requirements.
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < PasswordValidator.MIN_LENGTH:
            return False, f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long"
        
        if PasswordValidator.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if PasswordValidator.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if PasswordValidator.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if PasswordValidator.REQUIRE_SPECIAL:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character (!@#$%^&*...)"
        
        return True, "Password is valid"


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must not exceed 50 characters"
        
        # Allow only alphanumeric, underscore, and hyphen
        if not all(c.isalnum() or c in ('_', '-') for c in username):
            return False, "Username can only contain alphanumeric characters, underscores, and hyphens"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email or len(email) > 255:
            return False, "Invalid email format"
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, "Email is valid"
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 255) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized input string
        """
        if not isinstance(input_str, str):
            return ""
        
        # Truncate to max length
        sanitized = input_str[:max_length]
        
        # Remove null bytes and control characters
        sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\n\r\t')
        
        return sanitized.strip()
