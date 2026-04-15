"""
Authentication service for user registration, login, and account management.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import sqlite3
from .security_service import PasswordHasher, PasswordValidator, InputValidator
from .jwt_service import JWTService
from ..models.user import User, UserRole


class AuthenticationService:
    """Service for handling user authentication."""
    
    def __init__(self, db_connection=None):
        """Initialize authentication service."""
        self.db_connection = db_connection
        self.max_login_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.lockout_duration = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        self._init_user_table()
    
    def _init_user_table(self):
        """Initialize user table if it doesn't exist."""
        try:
            # Note: Adapt this for your database system (MySQL, PostgreSQL, etc.)
            # This is an SQLite example - modify for your actual DB
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    last_login DATETIME,
                    failed_login_attempts INTEGER DEFAULT 0,
                    is_locked BOOLEAN DEFAULT FALSE,
                    locked_until DATETIME
                )
            """)
            
            # Create sessions table for refresh tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    refresh_token TEXT UNIQUE NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_valid BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing user table: {e}")
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user"
    ) -> Tuple[bool, Optional[User], str]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            role: User role (default: user)
        
        Returns:
            Tuple of (success, user_object, message)
        """
        # Validate inputs
        username_valid, username_msg = InputValidator.validate_username(username)
        if not username_valid:
            return False, None, username_msg
        
        email_valid, email_msg = InputValidator.validate_email(email)
        if not email_valid:
            return False, None, email_msg
        
        password_valid, password_msg = PasswordValidator.validate(password)
        if not password_valid:
            return False, None, password_msg
        
        # Check if user already exists
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return False, None, "Username or email already exists"
            
            # Hash password
            password_hash = PasswordHasher.hash_password(password)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Create user object
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=UserRole(role),
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            return True, user, "User registered successfully"
        
        except Exception as e:
            return False, None, f"Registration error: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Authenticate user and return tokens.
        
        Args:
            username: Username or email
            password: Plain text password
        
        Returns:
            Tuple of (success, token_dict, message)
        """
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Fetch user
            cursor.execute("""
                SELECT user_id, username, email, password_hash, role, is_active, 
                       is_locked, locked_until, failed_login_attempts
                FROM users WHERE username = ? OR email = ?
            """, (username, username))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, None, "Invalid username or password"
            
            (user_id, db_username, email, password_hash, role, is_active,
             is_locked, locked_until, failed_attempts) = result
            
            # Check if user is active
            if not is_active:
                conn.close()
                return False, None, "User account is deactivated"
            
            # Check if account is locked
            if is_locked and locked_until:
                try:
                    locked_until_dt = datetime.fromisoformat(locked_until)
                    if datetime.utcnow() < locked_until_dt:
                        conn.close()
                        return False, None, "Account is locked due to too many login attempts"
                    else:
                        # Unlock account
                        cursor.execute("""
                            UPDATE users SET is_locked = ?, locked_until = ?, failed_login_attempts = ?
                            WHERE user_id = ?
                        """, (False, None, 0, user_id))
                        conn.commit()
                except ValueError:
                    pass
            
            # Verify password
            if not PasswordHasher.verify_password(password, password_hash):
                # Increment failed attempts
                new_attempts = failed_attempts + 1
                is_now_locked = new_attempts >= self.max_login_attempts
                locked_until = None
                
                if is_now_locked:
                    locked_until = (datetime.utcnow() + timedelta(minutes=self.lockout_duration)).isoformat()
                
                cursor.execute("""
                    UPDATE users SET failed_login_attempts = ?, is_locked = ?, locked_until = ?
                    WHERE user_id = ?
                """, (new_attempts, is_now_locked, locked_until, user_id))
                conn.commit()
                conn.close()
                
                if is_now_locked:
                    return False, None, f"Account locked after {self.max_login_attempts} failed attempts"
                return False, None, f"Invalid username or password ({self.max_login_attempts - new_attempts} attempts remaining)"
            
            # Reset failed login attempts
            cursor.execute("""
                UPDATE users SET failed_login_attempts = 0, is_locked = 0, last_login = ?
                WHERE user_id = ?
            """, (datetime.utcnow().isoformat(), user_id))
            conn.commit()
            
            # Create tokens
            tokens = JWTService.create_token_pair(user_id, db_username, email, role)
            
            # Store refresh token in database
            cursor.execute("""
                INSERT INTO user_sessions (user_id, refresh_token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, tokens['refresh_token'], 
                  (datetime.utcnow() + timedelta(days=7)).isoformat()))
            conn.commit()
            conn.close()
            
            return True, tokens, "Login successful"
        
        except Exception as e:
            return False, None, f"Login error: {str(e)}"
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[str], str]:
        """
        Refresh access token using a valid refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Tuple of (success, new_access_token, message)
        """
        try:
            # Verify token
            is_valid, payload, error = JWTService.verify_token(refresh_token)
            
            if not is_valid:
                return False, None, f"Invalid refresh token: {error}"
            
            if payload.get('token_type') != 'refresh':
                return False, None, "Token is not a refresh token"
            
            # Check if refresh token exists in database
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id FROM user_sessions 
                WHERE refresh_token = ? AND is_valid = TRUE AND expires_at > ?
            """, (refresh_token, datetime.utcnow().isoformat()))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False, None, "Refresh token is invalid or expired"
            
            # Create new access token
            new_access_token = JWTService.create_access_token(
                payload['user_id'],
                payload['username'],
                payload['email'],
                payload['role']
            )
            
            return True, new_access_token, "Access token refreshed successfully"
        
        except Exception as e:
            return False, None, f"Token refresh error: {str(e)}"
    
    def logout(self, refresh_token: str) -> Tuple[bool, str]:
        """
        Logout user by invalidating refresh token.
        
        Args:
            refresh_token: Refresh token to invalidate
        
        Returns:
            Tuple of (success, message)
        """
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions SET is_valid = FALSE
                WHERE refresh_token = ?
            """, (refresh_token,))
            
            conn.commit()
            conn.close()
            
            return True, "Logout successful"
        
        except Exception as e:
            return False, f"Logout error: {str(e)}"
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            User object or None
        """
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, email, role, is_active, created_at, last_login
                FROM users WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            user_id, username, email, role, is_active, created_at, last_login = result
            
            return User(
                user_id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                is_active=is_active,
                created_at=datetime.fromisoformat(created_at) if created_at else None,
                last_login=datetime.fromisoformat(last_login) if last_login else None,
            )
        
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
