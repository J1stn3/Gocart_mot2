import flet as ft
import os
import requests
from ..controllers.product_controller import ProductController
from ..controllers.cart_controller import CartController
from ..design_system import Colors, Typography, Spacing, BorderRadius, Shadows, Styles, ModernComponents

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8001/api"
)

class MainView:
    def __init__(self, page, on_shopping_click=None, cart_controller=None, auth_manager=None):

        self.page = page
        self.page.title = "GoCart - Modern Shopping System"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = Colors.BACKGROUND
        self.page.window_min_width = 1200
        self.page.window_min_height = 720

        self.on_shopping_click = on_shopping_click
        self.on_cart_click = None  # Will be set by AppManager
        self.on_orders_click = None  # Will be set by AppManager

        # Controllers kept for compatibility but UI is API-driven
        self.product_controller = ProductController()
        self.cart_controller = cart_controller if cart_controller else CartController()
        self.auth_manager = auth_manager

        self.selected_product_id = None

        # Navigation state
        self.current_view = "dashboard"
        self.sidebar_expanded = True

        # Initialize UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup modern UI with sidebar navigation."""

        # Create sidebar
        self.sidebar = self._create_sidebar()

        # Create main content area
        self.main_content = self._create_main_content()

        # Create top bar
        self.top_bar = self._create_top_bar()

        # Layout structure
        layout = ft.Row([
            self.sidebar,
            ft.VerticalDivider(width=1, color=Colors.BORDER),
            ft.Column([
                self.top_bar,
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(
                    content=self.main_content,
                    expand=True,
                    padding=Spacing.LG,
                    bgcolor=Colors.BACKGROUND,
                )
            ], expand=True)
        ], expand=True, spacing=0)

        self.page.clean()
        self.page.add(layout)

        # Load initial data
        self.update_product_table()
        self.update_cart_table()

    def _create_sidebar(self) -> ft.Container:
        """Create collapsible sidebar navigation."""

        # Navigation items
        nav_items = [
            {
                "icon": ft.Icons.DASHBOARD,
                "label": "Dashboard",
                "view": "dashboard",
                "active": True
            },
            {
                "icon": ft.Icons.SHOPPING_BAG,
                "label": "Shopping",
                "view": "shopping",
                "action": self._on_shopping_button_click
            },
            {
                "icon": ft.Icons.SHOPPING_CART,
                "label": "Cart",
                "view": "cart",
                "action": self._on_cart_button_click
            },
            {
                "icon": ft.Icons.RECEIPT,
                "label": "Orders",
                "view": "orders",
                "action": self._on_orders_button_click
            },
        ]

        # Create navigation buttons
        self.nav_buttons = []
        for item in nav_items:
            btn = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        item["icon"],
                        size=24,
                        color=Colors.SECONDARY if item.get("active", False) else Colors.TEXT_SECONDARY
                    ),
                    ft.Text(
                        item["label"],
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=Colors.SECONDARY if item.get("active", False) else Colors.TEXT_SECONDARY,
                        visible=self.sidebar_expanded
                    ),
                ], spacing=Spacing.MD, tight=True),
                padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
                border_radius=BorderRadius.MD,
                bgcolor=ft.Colors.with_opacity(0.1, Colors.SECONDARY) if item.get("active", False) else None,
                on_click=lambda e, item=item: self._on_nav_click(e, item),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
            self.nav_buttons.append(btn)

        # Sidebar content
        sidebar_content = ft.Column([
            # Logo section
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART, size=32, color=Colors.PRIMARY),
                    ft.Text(
                        "GoCart",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=Colors.TEXT_PRIMARY,
                        visible=self.sidebar_expanded
                    ),
                ], spacing=Spacing.SM, tight=True),
                padding=Spacing.LG,
                margin=ft.margin.only(bottom=Spacing.XL)
            ),

            # Navigation items
            ft.Column(self.nav_buttons, spacing=Spacing.XS),

            # Spacer
            ft.Container(expand=True),

            # Toggle button
            ft.Container(
                content=ModernComponents.icon_button(
                    ft.Icons.CHEVRON_LEFT if self.sidebar_expanded else ft.Icons.CHEVRON_RIGHT,
                    on_click=self._toggle_sidebar,
                    tooltip="Toggle Sidebar"
                ),
                alignment=ft.Alignment.CENTER,
                padding=Spacing.MD
            )
        ], spacing=0, tight=True)

        return ft.Container(
            content=sidebar_content,
            width=280 if self.sidebar_expanded else 80,
            bgcolor=Colors.SURFACE,
            shadow=Shadows.MD,
            animate_size=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    def _create_top_bar(self) -> ft.Container:
        """Create top navigation bar."""

        # Search field
        search_field = ft.TextField(
            prefix_icon=ft.Icons.SEARCH,
            hint_text="Search products...",
            width=300,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            hint_style=ft.TextStyle(size=14, color=Colors.TEXT_MUTED),
        )

        # User profile section
        user_section = ft.Row([
            ModernComponents.icon_button(
                ft.Icons.NOTIFICATIONS,
                tooltip="Notifications"
            ),
            ft.Container(width=Spacing.SM),
            ft.Container(
                content=ft.Row([
                    ft.CircleAvatar(
                        content=ft.Text("U", color=Colors.TEXT_PRIMARY),
                        bgcolor=Colors.PRIMARY,
                        radius=20
                    ),
                    ft.Column([
                        ft.Text(
                            self.auth_manager.user.get("username", "User") if self.auth_manager.user else "User",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=Colors.TEXT_PRIMARY
                        ),
                        ft.Text(
                            "Online",
                            size=12,
                            color=Colors.SUCCESS
                        ),
                    ], spacing=0, tight=True),
                    ModernComponents.icon_button(
                        ft.Icons.LOGOUT,
                        on_click=self._on_logout_click,
                        tooltip="Logout"
                    ),
                ], spacing=Spacing.SM, tight=True),
                padding=Spacing.SM,
                border_radius=BorderRadius.MD,
                on_hover=lambda e: setattr(e.control, 'bgcolor', ft.Colors.with_opacity(0.1, Colors.SECONDARY) if e.data == "true" else None) or e.control.update()
            )
        ], spacing=Spacing.SM)

        return ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                search_field,
                ft.Container(expand=True),
                user_section,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            bgcolor=Colors.SURFACE,
            border_radius=ft.border_radius.only(bottom_left=BorderRadius.LG, bottom_right=BorderRadius.LG),
        )

    def _create_main_content(self) -> ft.Container:
        """Create main content area with dashboard."""

        # Stats cards
        stats_cards = self._create_stats_cards()

        # Product management section
        product_section = self._create_product_section()

        # Cart section
        cart_section = self._create_cart_section()

        return ft.Container(
            content=ft.Column([
                # Page title
                ft.Container(
                    content=ft.Text(
                        "Dashboard",
                        style=Typography.H2
                    ),
                    margin=ft.margin.only(bottom=Spacing.LG)
                ),

                # Stats overview
                stats_cards,

                # Main content grid
                ft.Row([
                    ft.Column([
                        product_section,
                    ], expand=2),
                    ft.Container(width=Spacing.LG),
                    ft.Column([
                        cart_section,
                    ], expand=1),
                ], expand=True, alignment=ft.MainAxisAlignment.START),

            ], spacing=Spacing.LG, scroll=ft.ScrollMode.AUTO),
            expand=True
        )

    def _create_stats_cards(self) -> ft.Container:
        """Create statistics overview cards."""

        # Mock stats - in real app, these would come from API
        stats = [
            {
                "title": "Total Products",
                "value": "0",
                "icon": ft.Icons.INVENTORY,
                "color": Colors.PRIMARY,
                "change": "+12%"
            },
            {
                "title": "Cart Items",
                "value": "0",
                "icon": ft.Icons.SHOPPING_CART,
                "color": Colors.SECONDARY,
                "change": "+5%"
            },
            {
                "title": "Total Value",
                "value": "₱0.00",
                "icon": ft.Icons.PAYMENTS,
                "color": Colors.SUCCESS,
                "change": "+8%"
            },
            {
                "title": "Orders",
                "value": "0",
                "icon": ft.Icons.RECEIPT,
                "color": Colors.WARNING,
                "change": "+15%"
            },
        ]

        cards = []
        for stat in stats:
            card = ModernComponents.animated_card(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(
                                stat["icon"],
                                size=32,
                                color=stat["color"]
                            ),
                            width=60,
                            height=60,
                            border_radius=BorderRadius.MD,
                            bgcolor=ft.Colors.with_opacity(0.1, stat["color"]),
                            alignment=ft.Alignment.CENTER
                        ),
                        ft.Column([
                            ft.Text(
                                stat["title"],
                                size=12,
                                color=Colors.TEXT_MUTED,
                                weight=ft.FontWeight.W_600
                            ),
                            ft.Text(
                                stat["value"],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.TEXT_PRIMARY
                            ),
                            ft.Text(
                                stat["change"],
                                size=12,
                                color=Colors.SUCCESS,
                                weight=ft.FontWeight.W_600
                            ),
                        ], spacing=Spacing.XS, expand=True),
                    ], spacing=Spacing.MD, alignment=ft.MainAxisAlignment.START),
                    padding=Spacing.LG
                )
            )
            cards.append(card)

        return ft.Container(
            content=ft.Row(cards, spacing=Spacing.LG, wrap=True),
            margin=ft.margin.only(bottom=Spacing.LG)
        )

    def _create_product_section(self) -> ft.Container:
        """Create product management section."""

        # Product input form
        product_form = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY_2, color=Colors.SECONDARY),
                    ft.Text("Product Management", style=Typography.H4),
                ], spacing=Spacing.SM),

                ft.Row([
                    self._create_text_field("Product Name", ft.Icons.SHOPPING_BAG),
                    self._create_text_field("Price (₱)", ft.Icons.PAYMENTS),
                    self._create_text_field("Stock", ft.Icons.STORAGE),
                ], spacing=Spacing.MD),

                ft.Row([
                    self._create_button("Add Product", self.add_product, Colors.SUCCESS, ft.Icons.ADD),
                    self._create_button("Update", self.update_product, Colors.SECONDARY, ft.Icons.EDIT),
                    self._create_button("Delete", self.delete_product, Colors.ERROR, ft.Icons.DELETE),
                ], spacing=Spacing.MD),

                self.status_text,
            ], spacing=Spacing.MD),
            padding=Spacing.LG,
            border_radius=BorderRadius.LG,
            bgcolor=Colors.CARD,
            shadow=Shadows.MD
        )

        # Products table
        products_table = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_BAG, color=Colors.PRIMARY),
                    ft.Text("Available Products", style=Typography.H4),
                ], spacing=Spacing.SM),

                ft.Container(
                    content=self.product_list,
                    height=300,
                    border_radius=BorderRadius.MD,
                    bgcolor=Colors.SURFACE_LIGHT,
                    padding=Spacing.SM
                )
            ], spacing=Spacing.MD),
            padding=Spacing.LG,
            border_radius=BorderRadius.LG,
            bgcolor=Colors.CARD,
            shadow=Shadows.MD
        )

        return ft.Column([
            product_form,
            products_table,
        ], spacing=Spacing.LG)

    def _create_cart_section(self) -> ft.Container:
        """Create cart section."""

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SHOPPING_CART, color=Colors.SUCCESS),
                    ft.Text("Shopping Cart", style=Typography.H4),
                ], spacing=Spacing.SM),

                ft.Row([
                    self.cart_quantity_field,
                    self._create_button("Add to Cart", self.add_to_cart, Colors.PRIMARY, ft.Icons.ADD_SHOPPING_CART, width=140),
                ], spacing=Spacing.MD),

                ft.Container(
                    content=self.cart_list,
                    height=250,
                    border_radius=BorderRadius.MD,
                    bgcolor=Colors.SURFACE_LIGHT,
                    padding=Spacing.SM
                ),

                ft.Divider(),

                ft.Row([
                    ft.Container(expand=True),
                    ft.Row([
                        ft.Icon(ft.Icons.PAYMENTS, color=Colors.SUCCESS),
                        self.total_text
                    ], spacing=Spacing.SM)
                ]),
            ], spacing=Spacing.MD),
            padding=Spacing.LG,
            border_radius=BorderRadius.LG,
            bgcolor=Colors.CARD,
            shadow=Shadows.MD,
            expand=True
        )

    def _create_text_field(self, label, icon=None, value="", width=200):
        """Create styled text field."""
        return ft.TextField(
            label=label,
            value=value,
            prefix_icon=icon,
            width=width,
            border_radius=BorderRadius.MD,
            filled=True,
            bgcolor=Colors.SURFACE_LIGHT,
            border_color=Colors.BORDER,
            focused_border_color=Colors.SECONDARY,
            cursor_color=Colors.SECONDARY,
            text_style=ft.TextStyle(size=14, color=Colors.TEXT_PRIMARY),
            label_style=ft.TextStyle(size=12, color=Colors.TEXT_MUTED),
        )

    def _create_button(self, text, click, color=None, icon=None, width=120):
        """Create styled button."""
        if color is None:
            color = Colors.PRIMARY

        return ft.ElevatedButton(
            text,
            icon=icon,
            width=width,
            height=40,
            on_click=click,
            style=ft.ButtonStyle(
                bgcolor=color,
                color=Colors.TEXT_PRIMARY,
                elevation=2,
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
            ),
        )

    # Navigation and interaction methods
    def _on_nav_click(self, e, item):
        """Handle navigation click."""
        # Update active state
        for btn in self.nav_buttons:
            btn.bgcolor = None
            btn.content.controls[0].color = Colors.TEXT_SECONDARY
            if hasattr(btn.content.controls[1], 'color'):
                btn.content.controls[1].color = Colors.TEXT_SECONDARY

        e.control.bgcolor = ft.Colors.with_opacity(0.1, Colors.SECONDARY)
        e.control.content.controls[0].color = Colors.SECONDARY
        if hasattr(e.control.content.controls[1], 'color'):
            e.control.content.controls[1].color = Colors.SECONDARY

        # Handle navigation action
        if "action" in item and item["action"]:
            item["action"](e)
        elif item["view"] == "dashboard":
            self.current_view = "dashboard"
            # Refresh dashboard data
            self.update_product_table()
            self.update_cart_table()

        self.page.update()

    def _toggle_sidebar(self, e):
        """Toggle sidebar expansion."""
        self.sidebar_expanded = not self.sidebar_expanded
        self.sidebar.width = 280 if self.sidebar_expanded else 80

        # Toggle text visibility
        for btn in self.nav_buttons:
            if len(btn.content.controls) > 1:
                btn.content.controls[1].visible = self.sidebar_expanded

        # Update logo visibility
        logo_row = self.sidebar.content.controls[0].content
        if len(logo_row.controls) > 1:
            logo_row.controls[1].visible = self.sidebar_expanded

        self.page.update()

    def _on_logout_click(self, e):
        """Handle logout."""
        from ..main import show_login_screen
        show_login_screen(self.page)

    def _on_shopping_button_click(self, e):
        if self.on_shopping_click:
            self.on_shopping_click()

    def _on_cart_button_click(self, e):
        if self.on_cart_click:
            self.on_cart_click()

    def _on_orders_button_click(self, e):
        if self.on_orders_click:
            self.on_orders_click()

    # Initialize fields (keeping original field creation for compatibility)
    def _field(self, label, value="", width=220, icon=None):
        return self._create_text_field(label, icon, value, width)

    def _button(self, text, click, icon=None, color=None, width=150):
        return self._create_button(text, click, color, icon, width)

    # Status text
    @property
    def status_text(self):
        if not hasattr(self, '_status_text'):
            self._status_text = ft.Text("", size=14, color=Colors.TEXT_SECONDARY)
        return self._status_text

    # Cart quantity field
    @property
    def cart_quantity_field(self):
        if not hasattr(self, '_cart_quantity_field'):
            self._cart_quantity_field = self._create_text_field("Qty", "1", 80, ft.Icons.SHOPPING_CART)
        return self._cart_quantity_field

    # Product and cart lists
    @property
    def product_list(self):
        if not hasattr(self, '_product_list'):
            self._product_list = ft.ListView(spacing=Spacing.SM, height=320)
        return self._product_list

    @property
    def cart_list(self):
        if not hasattr(self, '_cart_list'):
            self._cart_list = ft.ListView(spacing=Spacing.SM, height=260)
        return self._cart_list

    # Total text
    @property
    def total_text(self):
        if not hasattr(self, '_total_text'):
            self._total_text = ft.Text(
                "Total: ₱0.00",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=Colors.SUCCESS
            )
        return self._total_text

    # Product and cart management methods
    def update_product_table(self):
        """Update the product list display."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/products",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code == 200:
                products = response.json().get("data", [])
                self.product_list.controls.clear()

                for product in products:
                    product_card = self._create_product_card(product)
                    self.product_list.controls.append(product_card)

                self.status_text.value = f"Loaded {len(products)} products"
                self.status_text.color = Colors.SUCCESS
            else:
                self.status_text.value = "Failed to load products"
                self.status_text.color = Colors.ERROR

        except Exception as e:
            self.status_text.value = f"Error loading products: {str(e)}"
            self.status_text.color = Colors.ERROR

        self.page.update()

    def update_cart_table(self):
        """Update the cart display."""
        try:
            response = requests.get(
                f"{API_BASE_URL}/cart",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code == 200:
                cart_items = response.json().get("data", [])
                self.cart_list.controls.clear()

                total = 0
                for item in cart_items:
                    cart_item_card = self._create_cart_item_card(item)
                    self.cart_list.controls.append(cart_item_card)
                    total += item.get("total_price", 0)

                self.total_text.value = f"Total: ₱{total:.2f}"
            else:
                self.total_text.value = "Total: ₱0.00"

        except Exception as e:
            self.total_text.value = "Total: ₱0.00"
            print(f"Error loading cart: {e}")

        self.page.update()

    def _create_product_card(self, product):
        """Create a product card for the list."""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        product.get("name", "Unknown"),
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT_PRIMARY
                    ),
                    ft.Text(
                        f"₱{product.get('price', 0):.2f}",
                        size=14,
                        color=Colors.SUCCESS,
                        weight=ft.FontWeight.W_600
                    ),
                    ft.Text(
                        f"Stock: {product.get('quantity', 0)}",
                        size=12,
                        color=Colors.TEXT_MUTED
                    ),
                ], spacing=Spacing.XS, expand=True),
                ModernComponents.icon_button(
                    ft.Icons.EDIT,
                    on_click=lambda e: self._select_product(product),
                    color=Colors.SECONDARY,
                    tooltip="Edit Product"
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=Spacing.MD,
            border_radius=BorderRadius.MD,
            bgcolor=Colors.SURFACE_LIGHT,
            border=ft.border.all(1, Colors.BORDER),
            on_hover=lambda e: setattr(e.control, 'bgcolor', ft.Colors.with_opacity(0.05, Colors.SECONDARY) if e.data == "true" else Colors.SURFACE_LIGHT) or e.control.update()
        )

    def _create_cart_item_card(self, item):
        """Create a cart item card."""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        item.get("product_name", "Unknown"),
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=Colors.TEXT_PRIMARY
                    ),
                    ft.Text(
                        f"Qty: {item.get('quantity', 1)} × ₱{item.get('price', 0):.2f}",
                        size=12,
                        color=Colors.TEXT_SECONDARY
                    ),
                ], spacing=Spacing.XS, expand=True),
                ft.Text(
                    f"₱{item.get('total_price', 0):.2f}",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=Colors.SUCCESS
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=Spacing.SM,
            border_radius=BorderRadius.SM,
            bgcolor=Colors.SURFACE_LIGHT,
            border=ft.border.all(1, Colors.BORDER),
        )

    def _select_product(self, product):
        """Select a product for editing."""
        self.selected_product_id = product.get("id")
        # Populate form fields
        if hasattr(self, 'name_field'):
            self.name_field.value = product.get("name", "")
        if hasattr(self, 'price_field'):
            self.price_field.value = str(product.get("price", ""))
        if hasattr(self, 'quantity_field'):
            self.quantity_field.value = str(product.get("quantity", ""))
        self.page.update()

    # CRUD Operations
    def add_product(self, e):
        """Add a new product."""
        try:
            name = self.name_field.value.strip()
            price = float(self.price_field.value or 0)
            quantity = int(self.quantity_field.value or 0)

            if not name:
                self.status_text.value = "Product name is required"
                self.status_text.color = Colors.ERROR
                self.page.update()
                return

            response = requests.post(
                f"{API_BASE_URL}/products",
                json={
                    "name": name,
                    "price": price,
                    "quantity": quantity
                },
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code in [200, 201]:
                self.status_text.value = "Product added successfully"
                self.status_text.color = Colors.SUCCESS
                # Clear form
                self.name_field.value = ""
                self.price_field.value = ""
                self.quantity_field.value = ""
                self.update_product_table()
            else:
                self.status_text.value = "Failed to add product"
                self.status_text.color = Colors.ERROR

        except ValueError:
            self.status_text.value = "Invalid price or quantity"
            self.status_text.color = Colors.ERROR
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = Colors.ERROR

        self.page.update()

    def update_product(self, e):
        """Update existing product."""
        if not self.selected_product_id:
            self.status_text.value = "Please select a product to update"
            self.status_text.color = Colors.WARNING
            self.page.update()
            return

        try:
            name = self.name_field.value.strip()
            price = float(self.price_field.value or 0)
            quantity = int(self.quantity_field.value or 0)

            response = requests.put(
                f"{API_BASE_URL}/products/{self.selected_product_id}",
                json={
                    "name": name,
                    "price": price,
                    "quantity": quantity
                },
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code == 200:
                self.status_text.value = "Product updated successfully"
                self.status_text.color = Colors.SUCCESS
                self.selected_product_id = None
                # Clear form
                self.name_field.value = ""
                self.price_field.value = ""
                self.quantity_field.value = ""
                self.update_product_table()
            else:
                self.status_text.value = "Failed to update product"
                self.status_text.color = Colors.ERROR

        except ValueError:
            self.status_text.value = "Invalid price or quantity"
            self.status_text.color = Colors.ERROR
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = Colors.ERROR

        self.page.update()

    def delete_product(self, e):
        """Delete a product."""
        if not self.selected_product_id:
            self.status_text.value = "Please select a product to delete"
            self.status_text.color = Colors.WARNING
            self.page.update()
            return

        try:
            response = requests.delete(
                f"{API_BASE_URL}/products/{self.selected_product_id}",
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code == 200:
                self.status_text.value = "Product deleted successfully"
                self.status_text.color = Colors.SUCCESS
                self.selected_product_id = None
                # Clear form
                self.name_field.value = ""
                self.price_field.value = ""
                self.quantity_field.value = ""
                self.update_product_table()
            else:
                self.status_text.value = "Failed to delete product"
                self.status_text.color = Colors.ERROR

        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = Colors.ERROR

        self.page.update()

    def add_to_cart(self, e):
        """Add product to cart."""
        if not self.selected_product_id:
            self.status_text.value = "Please select a product first"
            self.status_text.color = Colors.WARNING
            self.page.update()
            return

        try:
            quantity = int(self.cart_quantity_field.value or 1)

            response = requests.post(
                f"{API_BASE_URL}/cart/add",
                json={
                    "product_id": self.selected_product_id,
                    "quantity": quantity
                },
                headers=self.auth_manager.get_auth_header() if self.auth_manager else {},
                timeout=10,
            )

            if response.status_code in [200, 201]:
                self.status_text.value = "Added to cart successfully"
                self.status_text.color = Colors.SUCCESS
                self.update_cart_table()
            else:
                self.status_text.value = "Failed to add to cart"
                self.status_text.color = Colors.ERROR

        except ValueError:
            self.status_text.value = "Invalid quantity"
            self.status_text.color = Colors.ERROR
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = Colors.ERROR

        self.page.update()
