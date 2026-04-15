import os
import flet as ft
import requests
from ..controllers.cart_controller import CartController

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8001/api"
)

class OrdersView:
    def __init__(self, page, on_back_to_main, cart_controller: CartController, auth_manager):
        self.page = page
        self.on_back_to_main = on_back_to_main
        self.cart_controller = cart_controller
        self.auth_manager = auth_manager

        self.primary_color = "#00d4ff"
        self.secondary_color = "#7c3aed"
        self.accent_color = "#ff006e"
        self.success_color = "#1cbad2"
        self.warning_color = "#f59e0b"
        self.dark_bg = "#0f1729"
        self.card_bg = "#1a1f3a"

        self.orders_list = ft.ListView(height=400, spacing=10)
        self.grand_total_text = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=self.success_color)

        self.setup_ui()

    def _create_futuristic_button(self, text, on_click, color=None, width=120):
        if color is None:
            color = self.primary_color
        return ft.ElevatedButton(
            content=text,
            on_click=on_click,
            width=width,
            bgcolor=color,
            color="#ffffff",
            elevation=5,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )

    def setup_ui(self):
        back_button = ft.IconButton(
            ft.Icons.ARROW_BACK,
            icon_color=self.primary_color,
            icon_size=30,
            on_click=lambda e: self.on_back_to_main(),
        )

        header = ft.Container(
            content=ft.Row([
                back_button,
                ft.Column([
                    ft.Text("📋 ORDER HISTORY", size=32, weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ft.Text("View Your Completed Orders", size=12, color=self.secondary_color, italic=True)
                ]),
            ], spacing=20),
            padding=20,
            bgcolor=self.dark_bg,
            border_radius=12,
            border=ft.border.all(2, self.primary_color),
        )

        orders_section = ft.Container(
            content=ft.Column([
                ft.Text("📦 COMPLETED ORDERS", size=14, weight=ft.FontWeight.BOLD, color=self.accent_color),
                ft.Container(
                    content=self.orders_list,
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

        grand_total_section = ft.Container(
            content=ft.Column([
                ft.Text("💰 TOTAL REVENUE", size=14, weight=ft.FontWeight.BOLD, color=self.success_color),
                ft.Divider(color=self.primary_color),
                self.grand_total_text,
                self._create_futuristic_button("🗑️ CLEAR ORDERS", self.clear_all_orders, self.warning_color, 150),
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
                orders_section,
                grand_total_section,
            ],
        )

        self.page.clean()
        self.page.add(main_column)
        self.display_orders()

    def display_orders(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/orders",
                headers=self.auth_manager.get_auth_header(),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            orders = data.get('orders', [])
        except Exception as e:
            orders = []
            error_text = f"Error loading orders: {str(e)}"
            self.orders_list.controls = [
                ft.Container(
                    content=ft.Text(error_text, color="#ff006e", italic=True),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            ]
            self.page.update()
            return

        if not orders:
            self.orders_list.controls = [
                ft.Container(
                    content=ft.Text("No completed orders yet. Start shopping!",
                                     color=self.primary_color, italic=True),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            ]
            self.grand_total_text.value = "Total Revenue: ₱0.00"
        else:
            self.orders_list.controls = [self._create_order_card(order, i) for i, order in enumerate(orders)]
            grand_total = sum(order.get('total', 0) for order in orders)
            self.grand_total_text.value = f"Total Revenue: ₱{grand_total:.2f}"

        self.page.update()

    def _create_order_card(self, order, order_index):
        items = order.get('items', [])
        total = order.get('total', 0)

        items_text = "\n".join([
            f"  • {item['product']['name']} × {item['quantity']} = ₱{item['product']['price'] * item['quantity']:.2f}"
            if isinstance(item['product'], dict)
            else f"  • {item['product'].name} × {item['quantity']} = ₱{item['product'].price * item['quantity']:.2f}"
            for item in items
        ])

        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(f"Order #{order_index + 1}", size=16, weight=ft.FontWeight.BOLD, color=self.primary_color)]),
                ft.Divider(color=self.secondary_color, height=1),
                ft.Text("Order Items:", size=12, color=self.accent_color, weight=ft.FontWeight.BOLD),
                ft.Text(items_text, size=11, color=self.primary_color, selectable=True),
                ft.Divider(color=self.secondary_color, height=1),
                ft.Row([ft.Text(f"💰 Total: ₱{total:.2f}", size=13, color=self.success_color, weight=ft.FontWeight.BOLD)])
            ], spacing=5),
            padding=15,
            bgcolor=self.card_bg,
            border=ft.border.all(1, self.primary_color),
            border_radius=10,
        )

    def clear_all_orders(self, e):
        try:
            response = requests.post(
                f"{API_BASE_URL}/orders/clear",
                headers=self.auth_manager.get_auth_header(),
                timeout=10,
            )
            response.raise_for_status()
            # Refresh the orders display after clearing
            self.display_orders()
        except Exception as error:
            print(f"Error clearing orders: {str(error)}")
            # Still refresh display even if there's an error
            self.display_orders()