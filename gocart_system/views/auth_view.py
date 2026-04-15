"""
Flet login and authentication UI.
"""
import flet as ft
import requests
import json
from typing import Callable, Optional
import os


class AuthenticationManager:
    """Manages authentication tokens and API communication."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user: Optional[dict] = None
        self.token_expires_in: Optional[int] = None
    
    def register(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email
            password: Password
        
        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return True, "Registration successful! Please login."
            else:
                data = response.json()
                return False, data.get("message", data.get("detail", "Registration failed"))
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Make sure the API is running."
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Login user.
        
        Args:
            username: Username or email
            password: Password
        
        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tokens = data.get("data", {})
                
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                self.token_expires_in = tokens.get("expires_in")
                
                # Fetch user info
                self._fetch_user_info()
                
                return True, "Login successful!"
            else:
                data = response.json()
                return False, data.get("detail", "Login failed")
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server. Make sure the API is running."
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def _fetch_user_info(self):
        """Fetch current user information."""
        try:
            response = requests.get(
                f"{self.api_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user = data.get("data", {})
        except Exception as e:
            print(f"Error fetching user info: {e}")
    
    def refresh_access_token(self) -> bool:
        """
        Refresh access token.
        
        Returns:
            True if refresh successful
        """
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/refresh",
                json={"refresh_token": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tokens = data.get("data", {})
                self.access_token = tokens.get("access_token")
                self.token_expires_in = tokens.get("expires_in")
                return True
            return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Logout and invalidate tokens.
        
        Returns:
            True if logout successful
        """
        try:
            if self.refresh_token:
                requests.post(
                    f"{self.api_url}/api/auth/logout",
                    json={"refresh_token": self.refresh_token},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10
                )
            
            self.access_token = None
            self.refresh_token = None
            self.user = None
            self.token_expires_in = None
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.access_token is not None
    
    def get_auth_header(self) -> dict:
        """Get Authorization header with token."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}


class LoginView:
    """Login UI component."""
    
    def __init__(
        self,
        page: ft.Page,
        on_login_success: Callable,
        auth_manager: AuthenticationManager
    ):
        self.page = page
        self.on_login_success = on_login_success
        self.auth_manager = auth_manager
        self.is_register_mode = False
    
    def build(self) -> ft.Column:
        """Build login UI."""
        
        # Title
        title = ft.Text("GoCart Secure System", size=32, weight="bold")
        subtitle = ft.Text("Login to your account", size=16, color=ft.Colors.GREY_700)
        
        # Input fields
        self.username_field = ft.TextField(
            label="Username or Email",
            width=300,
            on_change=self._on_input_change
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_change=self._on_input_change
        )
        
        # Additional fields for registration
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            visible=False,
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            width=300,
            visible=False,
        )
        
        # Message display
        self.message_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.RED_600,
            text_align=ft.TextAlign.CENTER,
        )
        
        # Login button
        self.login_btn = ft.ElevatedButton(
            "LOGIN",
            width=300,
            height=50,
            on_click=self._on_login_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(size=16, weight="bold")
            )
        )
        
        # Toggle button
        self.toggle_btn = ft.TextButton(
            "Don't have an account? Register here",
            on_click=self._toggle_mode
        )
        
        # Build layout
        self.form_column = ft.Column(
            controls=[
                ft.Container(height=20),
                title,
                subtitle,
                ft.Container(height=20),
                self.username_field,
                self.password_field,
                self.email_field,
                self.confirm_password_field,
                ft.Container(height=10),
                self.message_text,
                ft.Container(height=10),
                self.login_btn,
                ft.Container(height=10),
                self.toggle_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        return ft.Container(
            content=self.form_column,
            alignment=ft.Alignment.CENTER,
            expand=True,
        )
    
    def _on_input_change(self, e):
        """Clear error message on input change."""
        if self.message_text.value:
            self.message_text.value = ""
            self.message_text.color = ft.Colors.RED_600
            self.page.update()
    
    def _on_login_click(self, e):
        """Handle login button click."""
        try:
            username = self.username_field.value.strip()
            password = self.password_field.value.strip()
            
            if not username or not password:
                self._show_error("Please enter username and password")
                return
            
            if self.is_register_mode:
                self._register(username, password)
            else:
                self._login(username, password)
        except Exception as ex:
            self._show_error(f"Error: {str(ex)}")
    
    def _login(self, username: str, password: str):
        """Perform login."""
        self.login_btn.disabled = True
        self.page.update()
        
        success, message = self.auth_manager.login(username, password)
        
        if success:
            self._show_success(message)
            # Call success callback
            self.on_login_success()
        else:
            self._show_error(message)
        
        self.login_btn.disabled = False
        self.page.update()
    
    def _register(self, username: str, password: str):
        """Perform registration."""
        email = self.email_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()
        
        if not email or not confirm_password:
            self._show_error("Please fill in all fields")
            return
        
        if password != confirm_password:
            self._show_error("Passwords do not match")
            return
        
        self.login_btn.disabled = True
        self.page.update()
        
        success, message = self.auth_manager.register(username, email, password)
        
        if success:
            self._show_success(message)
            # Switch back to login mode
            self._toggle_mode(None)
            self.username_field.value = ""
            self.password_field.value = ""
            self.email_field.value = ""
            self.confirm_password_field.value = ""
        else:
            self._show_error(message)
        
        self.login_btn.disabled = False
        self.page.update()
    
    def _toggle_mode(self, e):
        """Toggle between login and register modes."""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.login_btn.text = "REGISTER"
            self.toggle_btn.text = "Already have an account? Login here"
            self.email_field.visible = True
            self.confirm_password_field.visible = True
        else:
            self.login_btn.text = "LOGIN"
            self.toggle_btn.text = "Don't have an account? Register here"
            self.email_field.visible = False
            self.confirm_password_field.visible = False
            self.message_text.value = ""
        
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error message."""
        self.message_text.value = message
        self.message_text.color = ft.Colors.RED_600
        self.page.update()
    
    def _show_success(self, message: str):
        """Show success message."""
        self.message_text.value = message
        self.message_text.color = ft.Colors.GREEN_600
        self.page.update()
