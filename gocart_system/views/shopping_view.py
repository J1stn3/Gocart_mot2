import os
import flet as ft
import requests
from ..controllers.product_controller import ProductController
from ..controllers.cart_controller import CartController

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    f"http://127.0.0.1:{os.getenv('PORT', '61471')}"
)

class ShoppingView:
    def __init__(self, page, on_back_to_main, cart_controller):
        self.page = page
        self.on_back_to_main = on_back_to_main
        self.product_controller = ProductController()
        self.cart_controller = cart_controller
        
        # Futuristic color scheme
        self.primary_color = "#00d4ff"   # Cyan
        self.secondary_color = "#7c3aed" # Purple
        self.accent_color = "#ff006e"    # Pink
        self.success_color = "#1cbad2"   # Green (muted)
        self.dark_bg = "#0f1729"
        self.card_bg = "#1a1f3a"
        
        # Search state
        self.search_query = ""
        self.search_field = self._create_futuristic_field("🔍 Search products...")
        self.search_field.on_change = self.on_search_changed
        
        # Cart quantity field for shopping
        self.cart_quantity_field = self._create_futuristic_field("Quantity", "1")
        
        # Product list
        self.product_list = ft.ListView(height=400, spacing=10)
        
        # Status message
        self.status_text = ft.Text("", size=14, color=self.primary_color)
        
        # Setup UI
        self.setup_ui()
        
    def _create_futuristic_field(self, label, value=""):
        """Stylized futuristic text field."""
        return ft.TextField(
            label=label,
            value=value,
            width=250,
            bgcolor=self.card_bg,
            border_color=self.primary_color,
            label_style=ft.TextStyle(color=self.primary_color, size=12),
            text_style=ft.TextStyle(color=self.primary_color),
            cursor_color=self.accent_color,
            focused_border_color=self.secondary_color,
            prefix_icon=ft.Icons.SEARCH if "Search" in label else ft.Icons.DIALPAD,
        )
    
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
        """Setup the shopping page UI."""
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
                        "🛍️ SHOPPING STORE",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=self.primary_color,
                    ),
                    ft.Text(
                        "Browse & Add Products to Cart",
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
        
        # Search section
        search_section = ft.Container(
            content=ft.Column([
                ft.Text("🔎 SEARCH PRODUCTS", size=14, weight=ft.FontWeight.BOLD, color=self.accent_color),
                self.search_field,
                ft.Text("Showing all products", size=11, color=self.primary_color, italic=True),
            ]),
            padding=15,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(1, self.accent_color),
        )
        
        # Product selection section
        add_to_cart_section = ft.Container(
            content=ft.Column([
                ft.Text("📦 QUICK ADD TO CART", size=14, weight=ft.FontWeight.BOLD, color=self.success_color),
                ft.Row([
                    ft.Text("Quantity:", color=self.primary_color),
                    self.cart_quantity_field,
                    self._create_futuristic_button("ADD TO CART", self.add_selected_to_cart, self.success_color, 140),
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                self.status_text,
            ]),
            padding=15,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(1, self.success_color),
        )
        
        # Products section
        products_section = ft.Container(
            content=ft.Column([
                ft.Text("🏪 AVAILABLE PRODUCTS", size=14, weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Container(
                    content=self.product_list,
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
        
        main_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                search_section,
                add_to_cart_section,
                products_section,
            ]
        )
        
        self.page.clean()
        self.page.add(main_column)
        self.display_products()
    
    def on_search_changed(self, e):
        """Handle search input changes."""
        self.search_query = self.search_field.value.lower().strip()
        self.display_products()
    
    def display_products(self):
        """Display products based on search query."""
        try:
            response = requests.get(f"{API_BASE_URL}/products")
            response.raise_for_status()
            data = response.json()
            products = data.get("products", [])
            
            # Convert dicts back to product-like objects for compatibility
            class Product:
                def __init__(self, d):
                    self.name = d['name']
                    self.price = d['price']
                    self.quantity = d['quantity']
            
            products = [Product(p) for p in products]
        except Exception as e:
            self.product_list.controls = [
                ft.Container(
                    content=ft.Text(
                        f"Error loading products: {str(e)}",
                        color=self.accent_color,
                        italic=True
                    ),
                    padding=20,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            ]
            self.page.update()
            return
        
        if not products:
            self.product_list.controls = [
                ft.Container(
                    content=ft.Text(
                        "No products available. Add some in the Cart Manager!",
                        color=self.primary_color,
                        italic=True
                    ),
                    padding=20,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            ]
        else:
            # Filter products based on search
            filtered_products = [
                p for p in products
                if self.search_query in p.name.lower() or
                   self.search_query in str(p.price).lower()
            ]
            
            if not filtered_products:
                self.product_list.controls = [
                    ft.Container(
                        content=ft.Text(
                            f"❌ No products found for '{self.search_query}'",
                            color=self.accent_color,
                            italic=True
                        ),
                        padding=20,
                        alignment=ft.alignment.Alignment.CENTER,
                    )
                ]
            else:
                self.product_list.controls = [
                    self._create_shopping_product_card(product, i)
                    for i, product in enumerate(filtered_products)
                ]
        
        self.page.update()
    
    def _create_shopping_product_card(self, product, index):
        """Create a futuristic shopping product card."""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        product.name,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=self.primary_color
                    ),
                    ft.Row([
                        ft.Text(
                            f"💰 ₱{product.price}",
                            size=13,
                            color=self.success_color,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            f"📦 In Stock: {product.quantity}",
                            size=12,
                            color=self.secondary_color,
                        ),
                    ], spacing=20),
                ], expand=True),
                ft.ElevatedButton(
                    "select",
                    on_click=lambda e, prod=product: self.select_product_for_cart(prod),
                    width=130,
                    bgcolor=self.success_color,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                )
            ], spacing=15),
            padding=15,
            bgcolor=self.card_bg,
            border=ft.border.all(1, self.primary_color),
            border_radius=10,
        )
    
    def select_product_for_cart(self, product):
        """Select a product for adding to cart."""
        self.selected_product = product
        self._show_status(f"📌 Selected: {product.name}", self.primary_color)
    
    def add_selected_to_cart(self, e):
        """Add selected product to cart."""
        if not hasattr(self, 'selected_product'):
            self._show_status("⚠️ Please select a product first", self.accent_color)
            return

        try:
            quantity = int(self.cart_quantity_field.value or "1")
            
            response = requests.post(
                f"{API_BASE_URL}/cart/add",
                json={"product_name": self.selected_product.name, "quantity": quantity}
            )
            response.raise_for_status()
            
            self._show_status(
                f"✅ Added {quantity}x '{self.selected_product.name}' to cart!",
                self.success_color
            )
            self.cart_quantity_field.value = "1"
            self.display_products()  # Refresh to show updated stock
        except requests.exceptions.RequestException as re:
            self._show_status(f"❌ API Error: {str(re)}", self.accent_color)
        except ValueError as ve:
            self._show_status(f"❌ Invalid quantity: {str(ve)}", self.accent_color)
        except Exception as e:
            self._show_status(f"❌ An error occurred: {str(e)}", self.accent_color)
    
    def _show_status(self, message, color):
        """Display status message."""
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()