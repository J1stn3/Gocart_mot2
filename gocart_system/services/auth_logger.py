"""
Logging and monitoring service for authentication events.
"""
import logging
import os
from datetime import datetime
from typing import Optional
import sqlite3


class AuthLogger:
    """Logger for authentication events."""
    
    def __init__(self, log_file: str = "auth_events.log"):
        """Initialize authentication logger."""
        self.log_file = log_file
        self.logger = logging.getLogger("auth_service")
        
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        log_path = os.path.join(logs_dir, log_file)
        
        # Set up file and console handlers
        handler = logging.FileHandler(log_path)
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize audit table
        self._init_audit_table()
    
    def _init_audit_table(self):
        """Initialize audit log table."""
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type VARCHAR(50) NOT NULL,
                    user_id INTEGER,
                    username VARCHAR(50),
                    action VARCHAR(100),
                    status VARCHAR(20),
                    ip_address VARCHAR(45),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error initializing audit table: {e}")
    
    def log_login_attempt(
        self,
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Log login attempt.
        
        Args:
            username: Username attempting to login
            success: Whether login was successful
            ip_address: IP address of the request
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"Login attempt for user '{username}': {status}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
        
        self._log_to_db(
            event_type="LOGIN",
            username=username,
            action="Authentication attempt",
            status=status,
            ip_address=ip_address,
            details=details or message
        )
    
    def log_registration(
        self,
        username: str,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Log registration attempt.
        
        Args:
            username: Username being registered
            email: Email being registered
            success: Whether registration was successful
            ip_address: IP address of the request
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"Registration for user '{username}' ({email}): {status}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
        
        self._log_to_db(
            event_type="REGISTRATION",
            username=username,
            action=f"User registration: {email}",
            status=status,
            ip_address=ip_address,
            details=details or message
        )
    
    def log_logout(
        self,
        user_id: int,
        username: str,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Log logout event.
        
        Args:
            user_id: User ID
            username: Username
            ip_address: IP address of the request
            details: Additional details
        """
        message = f"Logout for user '{username}' (ID: {user_id})"
        self.logger.info(message)
        
        self._log_to_db(
            event_type="LOGOUT",
            user_id=user_id,
            username=username,
            action="User logout",
            status="SUCCESS",
            ip_address=ip_address,
            details=details or message
        )
    
    def log_token_refresh(
        self,
        user_id: int,
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Log token refresh event.
        
        Args:
            user_id: User ID
            username: Username
            success: Whether refresh was successful
            ip_address: IP address of the request
            details: Additional details
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"Token refresh for user '{username}' (ID: {user_id}): {status}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
        
        self._log_to_db(
            event_type="TOKEN_REFRESH",
            user_id=user_id,
            username=username,
            action="Access token refresh",
            status=status,
            ip_address=ip_address,
            details=details or message
        )
    
    def log_unauthorized_access(
        self,
        endpoint: str,
        reason: str,
        ip_address: Optional[str] = None,
        token_info: Optional[str] = None
    ):
        """
        Log unauthorized access attempt.
        
        Args:
            endpoint: Endpoint attempted
            reason: Reason for denial
            ip_address: IP address of the request
            token_info: Token information
        """
        message = f"Unauthorized access attempt to '{endpoint}': {reason}"
        self.logger.warning(message)
        
        self._log_to_db(
            event_type="UNAUTHORIZED_ACCESS",
            action=f"Access to {endpoint}",
            status="DENIED",
            ip_address=ip_address,
            details=f"{message}. Token info: {token_info or 'N/A'}"
        )
    
    def log_account_locked(
        self,
        user_id: int,
        username: str,
        ip_address: Optional[str] = None
    ):
        """
        Log account lockout event.
        
        Args:
            user_id: User ID
            username: Username
            ip_address: IP address of the request
        """
        message = f"Account '{username}' (ID: {user_id}) locked due to failed attempts"
        self.logger.warning(message)
        
        self._log_to_db(
            event_type="ACCOUNT_LOCKED",
            user_id=user_id,
            username=username,
            action="Account locked",
            status="LOCKED",
            ip_address=ip_address,
            details=message
        )
    
    def _log_to_db(
        self,
        event_type: str,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Log event to database.
        
        Args:
            event_type: Type of event
            username: Username involved
            user_id: User ID involved
            action: Action performed
            status: Status of the action
            ip_address: IP address
            details: Additional details
        """
        try:
            db_path = os.getenv("DB_PATH", "gocart.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_logs 
                (event_type, user_id, username, action, status, ip_address, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_type, user_id, username, action, status, ip_address, details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error logging to database: {e}")


# Global logger instance
auth_logger = AuthLogger()
