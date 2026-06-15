"""
Flet login and authentication UI - Modern Design
"""
import flet as ft
import requests
import json
from typing import Callable, Optional
import os
from ..design_system import Colors, Typography, Spacing, BorderRadius, Shadows, Styles, ModernComponents


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
    """Modern Login UI component."""
    
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
        
        # Setup page theme
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = Colors.BACKGROUND
    
    def build(self) -> ft.Stack:
        """Build modern login UI."""
        
        # Background with gradient
        background = ModernComponents.gradient_background()
        
        # Main login card
        login_card = self._create_login_card()
        
        # Floating elements for visual appeal
        floating_shapes = self._create_floating_shapes()
        
        return ft.Stack([
            background,
            floating_shapes,
            ft.Container(
                content=login_card,
                alignment=ft.Alignment.CENTER,
                padding=Spacing.LG,
                expand=True,
            )
        ], expand=True)
    
    def _create_login_card(self) -> ft.Container:
        """Create the main login/signup card."""
        
        # Title section
        title_section = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.SHOPPING_CART,
                    size=48,
                    color=Colors.PRIMARY
                ),
                ft.Text(
                    "Welcome to GoCart",
                    style=Typography.H1,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Secure Shopping System",
                    style=Typography.BODY,
                    text_align=ft.TextAlign.CENTER
                ),
            ], spacing=Spacing.SM, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(bottom=Spacing.XL)
        )
        
        # Form fields
        form_fields = self._create_form_fields()
        
        # Action buttons
        action_buttons = self._create_action_buttons()
        
        # Toggle section
        toggle_section = self._create_toggle_section()
        
        # Card content
        card_content = ft.Column([
            title_section,
            form_fields,
            action_buttons,
            toggle_section,
        ], spacing=Spacing.LG, tight=True)
        
        return ModernComponents.animated_card(card_content)
    
    def _create_form_fields(self) -> ft.Column:
        """Create form input fields."""
        
        # Username/Email field
        self.username_field = ft.TextField(
            label="Username or Email",
            prefix_icon=ft.Icons.PERSON,
            width=350,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
            on_change=self._on_input_change
        )
        
        # Password field
        self.password_field = ft.TextField(
            label="Password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=350,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
            on_change=self._on_input_change
        )
        
        # Registration fields (hidden initially)
        self.email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            width=350,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
            visible=False,
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=350,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
            visible=False,
        )
        
        # Message display
        self.message_text = ft.Text(
            value="",
            size=12,
            text_align=ft.TextAlign.CENTER,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        
        return ft.Column([
            self.username_field,
            self.password_field,
            self.email_field,
            self.confirm_password_field,
            self.message_text,
        ], spacing=Spacing.MD, tight=True)
    
    def _create_action_buttons(self) -> ft.Container:
        """Create action buttons."""
        
        self.login_btn = ft.ElevatedButton(
            "Sign In",
            width=350,
            height=48,
            on_click=self._on_login_click,
            style=Styles.button_primary(),
            icon=ft.Icons.LOGIN,
        )
        
        return ft.Container(
            content=self.login_btn,
            margin=ft.margin.symmetric(vertical=Spacing.MD)
        )
    
    def _create_toggle_section(self) -> ft.Container:
        """Create mode toggle section."""
        
        self.toggle_text = ft.Text(
            "Don't have an account? Sign Up",
            size=14,
            weight=ft.FontWeight.W_600,
            color=Colors.SECONDARY,
        )
        
        self.toggle_btn = ft.TextButton(
            content=self.toggle_text,
            on_click=self._toggle_mode,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: Colors.SECONDARY,
                    ft.ControlState.HOVERED: Colors.SECONDARY_LIGHT,
                },
            )
        )
        
        return ft.Container(
            content=self.toggle_btn,
            alignment=ft.Alignment.CENTER
        )
    
    def _create_floating_shapes(self) -> ft.Stack:
        """Create floating decorative shapes."""
        
        shapes = []
        for i in range(5):
            shape = ft.Container(
                width=60 + i * 20,
                height=60 + i * 20,
                border_radius=30 + i * 10,
                bgcolor=ft.Colors.with_opacity(0.1, Colors.PRIMARY if i % 2 == 0 else Colors.SECONDARY),
                animate_position=ft.Animation(2000 + i * 500, ft.AnimationCurve.EASE_IN_OUT),
                left=50 + i * 100,
                top=100 + i * 80,
            )
            shapes.append(shape)
        
        return ft.Stack(shapes, expand=True)
    
    def _on_input_change(self, e):
        """Clear error message on input change."""
        if self.message_text.value:
            self.message_text.value = ""
            self.message_text.color = Colors.ERROR
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
        self.login_btn.text = "Signing In..."
        self.page.update()
        
        success, message = self.auth_manager.login(username, password)
        
        if success:
            self._show_success(message)
            # Call success callback
            self.on_login_success()
        else:
            self._show_error(message)
        
        self.login_btn.disabled = False
        self.login_btn.text = "Sign In" if not self.is_register_mode else "Sign Up"
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
        self.login_btn.text = "Creating Account..."
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
        self.login_btn.text = "Sign Up"
        self.page.update()
    
    def _toggle_mode(self, e):
        """Toggle between login and register modes."""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.login_btn.text = "Sign Up"
            self.toggle_text.value = "Already have an account? Sign In"
            self.email_field.visible = True
            self.confirm_password_field.visible = True
        else:
            self.login_btn.text = "Sign In"
            self.toggle_text.value = "Don't have an account? Sign Up"
            self.email_field.visible = False
            self.confirm_password_field.visible = False
            self.message_text.value = ""
        
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error message."""
        self.message_text.value = message
        self.message_text.color = Colors.ERROR
        self.message_text.opacity = 1.0
        self.page.update()
    
    def _show_success(self, message: str):
        """Show success message."""
        self.message_text.value = message
        self.message_text.color = Colors.SUCCESS
        self.message_text.opacity = 1.0
        self.page.update()
