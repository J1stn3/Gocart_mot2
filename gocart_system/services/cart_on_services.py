from ..models.cart import Cart
from .storage_service import StorageService


class CartOnServices:
    def __init__(self):
        self.cart = Cart()
        self.storage = StorageService()
        self.completed_orders = []

    def add_to_cart(self, product_name: str, quantity: int) -> bool:
        if not product_name:
            raise ValueError("Product name cannot be empty")

        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        product = self.storage.find_product_by_name(product_name)

        if not product:
            return False

        if product.quantity < quantity:
            return False

        self.cart.add_item(product, quantity)
        product.quantity -= quantity
        self.storage.update_product_by_id(product.id, product)

        return True

    def get_cart_items(self):
        return self.cart.get_items()

    def get_total_price(self) -> float:
        return self.cart.get_total_price()

    def remove_from_cart(self, product_name: str):
        items = self.cart.get_items()

        for item in items:
            if item.product.name == product_name:
                item.product.quantity += item.quantity
                self.storage.update_product_by_id(item.product.id, item.product)
                break

        self.cart.remove_item(product_name)

    def clear_cart(self):
        items = self.cart.get_items()

        for item in items:
            item.product.quantity += item.quantity
            self.storage.update_product_by_id(item.product.id, item.product)

        self.cart.clear()

    def complete_order(self):
        items = self.cart.get_items()

        if not items:
            return None

        total = self.cart.get_total_price()

        order = {
            "items": [item.to_dict() for item in items],
            "total": total
        }

        self.completed_orders.append(order)

        self.clear_cart()

        return order

    def get_completed_orders(self):
        return self.completed_orders
