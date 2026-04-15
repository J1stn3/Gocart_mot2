import flet as ft
import os
import requests
from ..controllers.product_controller import ProductController
from ..controllers.cart_controller import CartController

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8001/api"
)

class MainView:
    def __init__(self, page, on_shopping_click=None, cart_controller=None, auth_manager=None):

        self.page = page
        self.page.title = "Cart-Ons"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0b1020"
        self.page.window_min_width = 1100
        self.page.window_min_height = 720

        self.on_shopping_click = on_shopping_click
        self.on_cart_click = None  # Will be set by AppManager
        self.on_orders_click = None  # Will be set by AppManager

        # Controllers kept for compatibility but UI is API-driven
        self.product_controller = ProductController()
        self.cart_controller = cart_controller if cart_controller else CartController()
        self.auth_manager = auth_manager

        self.selected_product_id = None

        # Colorful Professional Palette
        self.primary = "#6366f1"     # Indigo
        self.secondary = "#06b6d4"   # Cyan
        self.accent = "#f43f5e"      # Pink/Red
        self.success = "#22c55e"     # Green
        self.warning = "#f59e0b"     # Orange

        self.card = "#141b34"
        self.surface = "#1c2548"

        # Fields
        self.name_field = self._field("Product Name", icon=ft.Icons.INVENTORY)
        self.price_field = self._field("Price (₱)", icon=ft.Icons.PAYMENT)
        self.quantity_field = self._field("Stock", icon=ft.Icons.STORAGE)
        self.cart_quantity_field = self._field("Qty", "1", 100, ft.Icons.SHOPPING_CART)

        # Lists
        self.product_list = ft.ListView(spacing=12, height=320)
        self.cart_list = ft.ListView(spacing=12, height=260)

        self.total_text = ft.Text(
            "Total: ₱0.00",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=self.success
        )

        self.status_text = ft.Text("", size=14)

        self.setup_ui()

    # --------------------------------------------------

    def _field(self, label, value="", width=220, icon=None):
        return ft.TextField(
            label=label,
            value=value,
            width=width,
            prefix_icon=icon,
            border_radius=12,
            filled=True,
            bgcolor=self.surface,
            border_color="#2c355e",
            focused_border_color=self.secondary,
            cursor_color=self.secondary,
            text_style=ft.TextStyle(size=14),
        )

    # --------------------------------------------------

    def _button(self, text, click, icon=None, color=None, width=150):
        if color is None:
            color = self.primary
        return ft.ElevatedButton(
            content=text,
            icon=icon,
            width=width,
            height=46,
            on_click=click,
            style=ft.ButtonStyle(
                bgcolor=color,
                color="white",
                elevation=4,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

    # --------------------------------------------------

    def setup_ui(self):

        # Header
        header = ft.Container(
            padding=30,
            border_radius=18,
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment.TOP_LEFT,
                end=ft.alignment.Alignment.BOTTOM_RIGHT,
                colors=["#6366f1", "#06b6d4"]
            ),
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row([
                                ft.Icon(ft.Icons.STORE, size=34, color="white"),
                                ft.Text(
                                    "Cart-Ons",
                                    size=34,
                                    weight=ft.FontWeight.BOLD,
                                    color="white"
                                )
                            ]),
                            ft.Text(
                                "Smart Shopping Cart Management",
                                color="white70",
                                size=14
                            )
                        ]
                    ),
                    ft.Container(expand=True),
                    # Top buttons in a row
                    ft.Row([
                        self._button(
                            "Go Shopping",
                            self._on_shopping_button_click,
                            ft.Icons.SHOPPING_CART,
                            "#17eb44"
                        ),
                        self._button(
                            "View Cart",
                            self._on_cart_button_click,
                            ft.Icons.SHOPPING_BAG,
                            "#ff6b35"
                        ),
                        self._button(
                            "Orders",
                            self._on_orders_button_click,
                            ft.Icons.RECEIPT,
                            "#6366f1"
                        )
                    ], spacing=10)
                ]
            ),
        )

        # Product Input Section
        product_input = ft.Container(
            padding=22,
            border_radius=16,
            bgcolor=self.card,
            content=ft.Column(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, color=self.secondary),
                        ft.Text(
                            "Product Management",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        )
                    ]),

                    ft.Row(
                        [
                            self.name_field,
                            self.price_field,
                            self.quantity_field,
                        ],
                        spacing=15
                    ),

                    ft.Row(
                        [
                            self._button("Add Product", self.add_product, ft.Icons.ADD, self.success),
                            self._button("Update", self.update_product, ft.Icons.EDIT, self.secondary),
                            self._button("Delete", self.delete_product, ft.Icons.DELETE, self.accent),
                        ],
                        spacing=10
                    ),

                    self.status_text
                ]
            )
        )

        # Products List
        products_section = ft.Container(
            padding=22,
            border_radius=16,
            bgcolor=self.card,
            content=ft.Column(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.SHOPPING_BAG, color=self.primary),
                        ft.Text(
                            "Available Products",
                            size=20,
                            weight=ft.FontWeight.BOLD
                        )
                    ]),
                    self.product_list
                ]
            )
        )

        # Cart Section
        cart_section = ft.Container(
            padding=22,
            border_radius=16,
            bgcolor=self.card,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SHOPPING_CART, color=self.success),
                            ft.Text(
                                "Shopping Cart",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(expand=True),
                            self.cart_quantity_field,
                            self._button(
                                "Add to Cart",
                                self.add_to_cart,
                                ft.Icons.ADD_SHOPPING_CART,
                                self.primary,
                                170
                            )
                        ]
                    ),
                    self.cart_list,
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.Row([
                                ft.Icon(ft.Icons.PAYMENTS, color=self.success),
                                self.total_text
                            ])
                        ]
                    )
                ]
            )
        )

        # Layout
        layout = ft.Column(
            [
                header,
                product_input,
                products_section,
                cart_section,
            ],
            spacing=22,
            scroll=ft.ScrollMode.AUTO
        )

        self.page.clean()
        self.page.add(layout)

        self.update_product_table()
        self.update_cart_table()

    # --------------------------------------------------

    def _on_shopping_button_click(self, e):
        if self.on_shopping_click:
            self.on_shopping_click()

    def _on_cart_button_click(self, e):
        if self.on_cart_click:
            self.on_cart_click()

    def _on_orders_button_click(self, e):
        if self.on_orders_click:
            self.on_orders_click()

    # --------------------------------------------------
    # Product Table
    # --------------------------------------------------

    def update_product_table(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/products",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            products = response.json().get("products", [])
        except Exception as e:
            self.product_list.controls = [ft.Text(f"Error loading products: {str(e)}", italic=True)]
            self.page.update()
            return

        if not products:
            self.product_list.controls = [
                ft.Text("No products available", italic=True)
            ]
        else:
            self.product_list.controls = [
                self._product_card(p, i) for i, p in enumerate(products)
            ]
        self.page.update()

    def _product_card(self, product, index):
        selected = self.selected_product_id == product.get("id")
        return ft.Container(
            padding=16,
            border_radius=14,
            bgcolor=self.surface,
            border=ft.border.all(
                2,
                self.secondary if selected else "#2c355e"
            ),
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INVENTORY, color=self.primary),
                    ft.Column(
                        [
                            ft.Text(
                                product.get("name"),
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        bgcolor=self.success,
                                        padding=6,
                                        border_radius=6,
                                        content=ft.Text(
                                            f"₱{product.get('price')}",
                                            color="white",
                                            size=12
                                        )
                                    ),
                                    ft.Text(
                                        f"Stock: {product.get('quantity')}",
                                        color="white70"
                                    )
                                ]
                            )
                        ],
                        expand=True
                    ),
                    self._button(
                        "Select",
                        lambda e, pid=product.get("id"): self.select_product(pid),
                        ft.Icons.CHECK,
                        self.secondary,
                        120
                    )
                ]
            )
        )

    # --------------------------------------------------
    # Cart Table
    # --------------------------------------------------

    def _create_cart_item_card(self, item):
        return ft.Container(
            padding=15,
            border_radius=14,
            bgcolor=self.surface,
            border=ft.border.all(1, "#2c355e"),
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SHOPPING_BAG, color=self.secondary),
                    ft.Column(
                        [
                            ft.Text(
                                item.product.name,
                                weight=ft.FontWeight.BOLD,
                                size=15
                            ),
                            ft.Text(
                                f"Qty: {item.quantity} | ₱{item.product.price}",
                                color="white70"
                            )
                        ],
                        expand=True
                    ),
                    ft.Text(
                        f"₱{item.get_total_price():.2f}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.success
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=self.accent,
                        on_click=lambda e: self.remove_from_cart(item.product.name)
                    )
                ]
            )
        )

    def update_cart_table(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/cart",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            items = data.get("cart_items", [])
            total = float(data.get("total_price", 0))
        except Exception as e:
            self.cart_list.controls = [ft.Text(f"Error loading cart: {str(e)}", italic=True)]
            self.total_text.value = "Total: ₱0.00"
            self.page.update()
            return

        if not items:
            self.cart_list.controls = [ft.Text("Your cart is empty 🛒", italic=True)]
        else:
            # Reuse existing card renderer by adapting shape
            class _Item:
                def __init__(self, d):
                    self.product = type("P", (), {"id": d["product"]["id"], "name": d["product"]["name"], "price": d["product"]["price"]})()
                    self.quantity = d["quantity"]
                def get_total_price(self):
                    return float(self.product.price) * int(self.quantity)
            self.cart_list.controls = [self._create_cart_item_card(_Item(i)) for i in items]

        self.total_text.value = f"Total: ₱{total:.2f}"
        self.page.update()

    # --------------------------------------------------
    # Product Selection
    # --------------------------------------------------

    def select_product(self, product_id):
        self.selected_product_id = int(product_id) if product_id is not None else None
        try:
            response = requests.get(
                f"{API_BASE_URL}/products",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            products = response.json().get("products", [])
            p = next((x for x in products if int(x.get("id")) == self.selected_product_id), None)
            if not p:
                self._show_status("Product not found", self.accent)
                return
            self.name_field.value = p.get("name", "")
            self.price_field.value = str(p.get("price", ""))
            self.quantity_field.value = str(p.get("quantity", ""))
        except Exception as e:
            self._show_status(f"Error selecting product: {str(e)}", self.accent)
        self.update_product_table()

    # --------------------------------------------------
    # Cart Actions
    # --------------------------------------------------

    def remove_from_cart(self, product_name):
        try:
            # Resolve product_id from cart
            response = requests.get(
                f"{API_BASE_URL}/cart",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            match = next((i for i in data.get("cart_items", []) if i["product"]["name"] == product_name), None)
            if not match:
                self._show_status("Item not found in cart", self.warning)
                return

            product_id = int(match["product"]["id"])
            response = requests.delete(
                f"{API_BASE_URL}/cart/{product_id}",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()

            self.update_product_table()
            self.update_cart_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def add_to_cart(self, e):
        qty = self.cart_quantity_field.value.strip()
        if self.selected_product_id is None:
            self._show_status("Select a product to add to cart", self.accent)
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/cart/add",
                json={"product_id": int(self.selected_product_id), "quantity": int(qty or "1")},
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()

            self._show_status("Added to cart", self.success)
            self.update_cart_table()
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    # --------------------------------------------------
    # Product CRUD Actions
    # --------------------------------------------------

    def add_product(self, e):
        name = self.name_field.value.strip()
        price = self.price_field.value.strip()
        quantity = self.quantity_field.value.strip()

        try:
            response = requests.post(
                f"{API_BASE_URL}/products",
                json={"name": name, "price": float(price), "quantity": int(quantity)},
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            self._show_status(f"Added {name} successfully!", self.success)
            self.clear_fields()
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def update_product(self, e):
        if self.selected_product_id is None:
            self._show_status("Select a product to update", self.accent)
            return

        name = self.name_field.value.strip()
        price = self.price_field.value.strip()
        quantity = self.quantity_field.value.strip()

        try:
            response = requests.put(
                f"{API_BASE_URL}/products/{int(self.selected_product_id)}",
                json={"name": name, "price": float(price), "quantity": int(quantity)},
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            self._show_status(f"Updated {name} successfully!", self.success)
            self.clear_fields()
            self.selected_product_id = None
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def delete_product(self, e):
        if self.selected_product_id is None:
            self._show_status("Select a product to delete", self.accent)
            return

        try:
            response = requests.delete(
                f"{API_BASE_URL}/products/{int(self.selected_product_id)}",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )
            response.raise_for_status()
            self._show_status("Deleted product!", self.warning)
            self.clear_fields()
            self.selected_product_id = None
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _show_status(self, message, color):
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()

    def clear_fields(self):
        self.name_field.value = ""
        self.price_field.value = ""
        self.quantity_field.value = ""
        self.cart_quantity_field.value = "1"
        self.page.update()