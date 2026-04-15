import os
import threading
import flet as ft
from .views.main_view import MainView
from .views.shopping_view import ShoppingView
from .views.cart_view import CartView
from .views.orders_view import OrdersView
from .views.auth_view import AuthenticationManager, LoginView
from .controllers.cart_controller import CartController

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8001"))  # Use 8001 for API server
API_URL = f"http://{API_HOST}:{API_PORT}"

class AppManager:
    def __init__(self, page: ft.Page, auth_manager: AuthenticationManager):
        self.page = page
        self.page.title = "GoCart - Secure Shopping System"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0a0e27"
        
        # Authentication manager
        self.auth_manager = auth_manager
        
        # Shared cart controller
        self.cart_controller = CartController()
        
        # View instances
        self.main_view = None
        self.shopping_view = None
        self.cart_view = None
        self.orders_view = None
        
        # Initialize with main view
        self.show_main_view()
    
    def show_main_view(self):
        """Show the main cart management view."""
        self.main_view = MainView(
            self.page,
            on_shopping_click=self.show_shopping_view,
            cart_controller=self.cart_controller
        )
        self.main_view.on_cart_click = self.show_cart_view
        self.main_view.on_orders_click = self.show_orders_view
        # Sync cart display if it was used in shopping
        if self.shopping_view:
            self.main_view.update_cart_table()
    
    def show_shopping_view(self):
        """Show the shopping/browsing view."""
        self.shopping_view = ShoppingView(
            self.page,
            on_back_to_main=self.show_main_view,
            cart_controller=self.cart_controller
        )

    def show_cart_view(self):
        """Show the cart view."""
        self.cart_view = CartView(
            self.page,
            on_back_to_main=self.show_main_view,
            cart_controller=self.cart_controller
        )

    def show_orders_view(self):
        """Show the orders view."""
        self.orders_view = OrdersView(
            self.page,
            on_back_to_main=self.show_main_view,
            cart_controller=self.cart_controller
        )
    
    def on_logout(self):
        """Handle logout."""
        self.auth_manager.logout()
        show_login_screen(self.page)

def start_api_server():
    import uvicorn
    import time
    # Small delay to ensure clean startup
    time.sleep(0.5)
    uvicorn.run(
        "gocart_system.api:app",
        host=API_HOST,
        port=API_PORT,
        log_level="info",
    )


def show_login_screen(page: ft.Page):
    """Display login screen."""
    page.clean()
    
    auth_manager = AuthenticationManager(api_url=API_URL)
    
    def on_login_success():
        """Callback when login is successful."""
        app = AppManager(page, auth_manager)
        page.update()
    
    login_view = LoginView(page, on_login_success, auth_manager)
    page.add(login_view.build())


def main(page: ft.Page):
    # Start API server in background thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Show login screen
    show_login_screen(page)

if __name__ == "__main__":
    print(f"Starting FastAPI API on http://{API_HOST}:{API_PORT}")
    ft.run(main)