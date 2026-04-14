import os
import flet as ft
import requests
from ..controllers.cart_controller import CartController

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    f"http://127.0.0.1:{os.getenv('PORT', '61471')}"
)

class CartView:
    def __init__(self, page, on_back_to_main, cart_controller):
        self.page = page
        self.on_back_to_main = on_back_to_main
        self.cart_controller = cart_controller

        # Futuristic color scheme (matching shopping view)
        self.primary_color = "#00d4ff"   # Cyan
        self.secondary_color = "#7c3aed" # Purple
        self.accent_color = "#ff006e"    # Pink
        self.success_color = "#1cbad2"   # Green (muted)
        self.warning_color = "#f59e0b"   # Orange
        self.dark_bg = "#0f1729"
        self.card_bg = "#1a1f3a"

        # Cart items list
        self.cart_list = ft.ListView(height=400, spacing=10)

        # Total and checkout section
        self.total_text = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=self.success_color)
        self.checkout_button = self._create_futuristic_button("🛒 CHECKOUT", self.checkout_cart, self.success_color, 200)

        # Status message
        self.status_text = ft.Text("", size=14, color=self.primary_color)

        # Setup UI
        self.setup_ui()

    def _create_futuristic_button(self, text, on_click, color=None, width=120):
        """Stylized futuristic button with icon support."""
        if color is None:
            color = self.primary_color
        return ft.ElevatedButton(
            content=text,
            on_click=on_click,
            width=width,
            bgcolor=color,
            color="#ffffff",
            elevation=5,
            icon=ft.Icons.SHOPPING_CART if "CART" in text.upper() else None,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

    def setup_ui(self):
        """Setup the cart page UI."""
        # Back button
        back_button = ft.IconButton(
            ft.Icons.ARROW_BACK,
            icon_color=self.primary_color,
            icon_size=30,
            on_click=lambda e: self.on_back_to_main(),
        )

        # Header
        header = ft.Container(
            content=ft.Row([
                back_button,
                ft.Column([
                    ft.Text(
                        "🛒 YOUR CART",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=self.primary_color,
                    ),
                    ft.Text(
                        "Review & Checkout Your Items",
                        size=12,
                        color=self.secondary_color,
                        italic=True,
                    )
                ]),
            ], spacing=20),
            padding=20,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(2, self.primary_color),
        )

        # Cart items section
        cart_section = ft.Container(
            content=ft.Column([
                ft.Text("🛍️ CART ITEMS", size=14, weight=ft.FontWeight.BOLD, color=self.accent_color),
                ft.Container(
                    content=self.cart_list,
                    height=400,
                    bgcolor=self.card_bg,
                    border_radius=10,
                    border=ft.border.all(1, self.primary_color),
                    padding=10,
                )
            ]),
            padding=20,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(1, self.primary_color),
        )

        # Total and checkout section
        checkout_section = ft.Container(
            content=ft.Column([
                ft.Text("💰 ORDER SUMMARY", size=14, weight=ft.FontWeight.BOLD, color=self.success_color),
                ft.Divider(color=self.primary_color),
                self.total_text,
                ft.Container(height=20),
                self.checkout_button,
                self.status_text,
            ]),
            padding=20,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(1, self.success_color),
        )

        main_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                cart_section,
                checkout_section,
            ]
        )

        self.page.clean()
        self.page.add(main_column)
        self.display_cart_items()

    def display_cart_items(self):
        """Display cart items."""
        try:
            response = requests.get(f"{API_BASE_URL}/cart")
            response.raise_for_status()
            data = response.json()
            cart_items = data.get("cart_items", [])
            total_price = data.get("total_price", 0)
            
            # Convert dicts back to cart item-like objects
            class CartItem:
                def __init__(self, d):
                    self.product = type('Product', (), {
                        'name': d['product']['name'],
                        'price': d['product']['price']
                    })()
                    self.quantity = d['quantity']
            
            cart_items = [CartItem(item) for item in cart_items]
        except Exception as e:
            self.cart_list.controls = [
                ft.Container(
                    content=ft.Text(
                        f"Error loading cart: {str(e)}",
                        color=self.accent_color,
                        italic=True
                    ),
                    padding=20,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            ]
            self.total_text.value = "Total: ₱0.00"
            self.page.update()
            return

        if not cart_items:
            self.cart_list.controls = [
                ft.Container(
                    content=ft.Text(
                        "Your cart is empty. Add some products from the shopping page!",
                        color=self.primary_color,
                        italic=True
                    ),
                    padding=20,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            ]
            self.total_text.value = f"Total: ₱{total_price:.2f}"
        else:
            self.cart_list.controls = [
                self._create_cart_item_card(item, i)
                for i, item in enumerate(cart_items)
            ]

            self.total_text.value = f"Total: ₱{total_price:.2f}"

        self.page.update()

    def _create_cart_item_card(self, cart_item, index):
        """Create a futuristic cart item card."""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        cart_item.product.name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.primary_color
                    ),
                    ft.Row([
                        ft.Text(
                            f"💰 ₱{cart_item.product.price:.2f} each",
                            size=13,
                            color=self.success_color,
                        ),
                        ft.Text(
                            f"📦 Quantity: {cart_item.quantity}",
                            size=12,
                            color=self.secondary_color,
                        ),
                        ft.Text(
                            f"💵 Subtotal: ₱{cart_item.product.price * cart_item.quantity:.2f}",
                            size=13,
                            color=self.accent_color,
                            weight=ft.FontWeight.BOLD
                        ),
                    ], spacing=15),
                ], expand=True),
                ft.IconButton(
                    ft.Icons.DELETE,
                    icon_color=self.accent_color,
                    icon_size=24,
                    on_click=lambda e, name=cart_item.product.name: self.remove_from_cart(name),
                    tooltip="Remove from cart"
                )
            ], spacing=15),
            padding=15,
            bgcolor=self.card_bg,
            border=ft.border.all(1, self.primary_color),
            border_radius=10,
        )

    def remove_from_cart(self, product_name):
        """Remove item from cart."""
        try:
            response = requests.delete(f"{API_BASE_URL}/cart/{product_name}")
            response.raise_for_status()
            self._show_status(f"Removed {product_name} from cart", self.warning_color)
            self.display_cart_items()
        except requests.exceptions.RequestException as re:
            self._show_status(f"API Error: {str(re)}", self.accent_color)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent_color)

    def checkout_cart(self, e):
        """Process checkout."""
        try:
            response = requests.post(f"{API_BASE_URL}/cart/complete")
            response.raise_for_status()
            data = response.json()
            order = data.get("order", {})
            total = order.get("total", 0)
            self._show_status(f"✅ Checkout successful! Total: ₱{total:.2f}", self.success_color)
            self.display_cart_items()
        except requests.exceptions.RequestException as re:
            self._show_status(f"API Error: {str(re)}", self.accent_color)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent_color)

    def _show_status(self, message, color):
        """Display status message."""
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()