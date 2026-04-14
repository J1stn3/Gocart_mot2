import flet as ft
from ..controllers.product_controller import ProductController
from ..controllers.cart_controller import CartController


class MainView:
    def __init__(self, page, on_shopping_click=None, cart_controller=None):

        self.page = page
        self.page.title = "Cart-Ons"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0b1020"
        self.page.window_min_width = 1100
        self.page.window_min_height = 720

        self.on_shopping_click = on_shopping_click
        self.on_cart_click = None  # Will be set by AppManager
        self.on_orders_click = None  # Will be set by AppManager

        self.product_controller = ProductController()
        self.cart_controller = cart_controller if cart_controller else CartController()

        self.selected_product_index = None

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
                cart_section
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
        products = self.product_controller.get_products()
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
        selected = index == self.selected_product_index
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
                                product.name,
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
                                            f"₱{product.price}",
                                            color="white",
                                            size=12
                                        )
                                    ),
                                    ft.Text(
                                        f"Stock: {product.quantity}",
                                        color="white70"
                                    )
                                ]
                            )
                        ],
                        expand=True
                    ),
                    self._button(
                        "Select",
                        lambda e: self.select_product(index),
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
        items = self.cart_controller.get_cart_items()
        if not items:
            self.cart_list.controls = [
                ft.Text("Your cart is empty 🛒", italic=True)
            ]
        else:
            self.cart_list.controls = [
                self._create_cart_item_card(i) for i in items
            ]
        self.total_text.value = f"Total: ₱{self.cart_controller.get_total_price():.2f}"
        self.page.update()

    # --------------------------------------------------
    # Product Selection
    # --------------------------------------------------

    def select_product(self, index):
        products = self.product_controller.get_products()
        self.selected_product_index = index
        p = products[index]
        self.name_field.value = p.name
        self.price_field.value = str(p.price)
        self.quantity_field.value = str(p.quantity)
        self.update_product_table()

    # --------------------------------------------------
    # Cart Actions
    # --------------------------------------------------

    def remove_from_cart(self, product_name):
        try:
            self.cart_controller.remove_from_cart(product_name)
            self.update_product_table()
            self.update_cart_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def add_to_cart(self, e):
        qty = self.cart_quantity_field.value.strip()
        if self.selected_product_index is None:
            self._show_status("Select a product to add to cart", self.accent)
            return

        try:
            product = self.product_controller.get_products()[self.selected_product_index]
            added = self.cart_controller.add_to_cart(product.name, qty)
            if not added:
                self._show_status("Could not add to cart (check stock)", self.accent)
                return

            self._show_status(f"Added {qty} x {product.name} to cart", self.success)
            self.update_cart_table()
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
            self.product_controller.create_product(name, price, quantity)
            self._show_status(f"Added {name} successfully!", self.success)
            self.clear_fields()
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def update_product(self, e):
        if self.selected_product_index is None:
            self._show_status("Select a product to update", self.accent)
            return

        name = self.name_field.value.strip()
        price = self.price_field.value.strip()
        quantity = self.quantity_field.value.strip()

        try:
            self.product_controller.update_product(self.selected_product_index, name, price, quantity)
            self._show_status(f"Updated {name} successfully!", self.success)
            self.clear_fields()
            self.selected_product_index = None
            self.update_product_table()
        except ValueError as ve:
            self._show_status(str(ve), self.accent)
        except Exception as e:
            self._show_status(f"An error occurred: {str(e)}", self.accent)

    def delete_product(self, e):
        if self.selected_product_index is None:
            self._show_status("Select a product to delete", self.accent)
            return

        try:
            products = self.product_controller.get_products()
            product = products[self.selected_product_index]
            self.product_controller.delete_product(self.selected_product_index)
            self._show_status(f"Deleted {product.name}!", self.warning)
            self.clear_fields()
            self.selected_product_index = None
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