from ..services.cart_on_services import CartOnServices
from ..services.product_services import ProductServices
from ..requests import AddToCartRequest, RemoveFromCartRequest, CompleteOrderRequest

class CartController:

    def __init__(self):
        self.service = CartOnServices()
        self.product_service = ProductServices()

    def _validate(self, request):
        result = request.validate()
        if not result.is_valid:
            raise ValueError('; '.join(result.errors.values()))
        return result.validated_data

    def _find_product(self, product_name):
        product = self.product_service.storage.find_product_by_name(product_name)
        if not product:
            raise ValueError(f"Product '{product_name}' not found.")
        return product

    def add_to_cart(self, product_name, quantity):
        product = self._find_product(product_name)
        request = AddToCartRequest({'quantity': quantity}, product_name, product.quantity)
        validated = self._validate(request)
        return self.service.add_to_cart(validated['product_name'], validated['quantity'])

    def get_cart_items(self):
        return self.service.get_cart_items()

    def get_total_price(self):
        return self.service.get_total_price()

    def remove_from_cart(self, product_name):
        request = RemoveFromCartRequest(product_name, self.get_cart_items())
        validated = self._validate(request)
        self.service.remove_from_cart(validated['product_name'])

    def clear_cart(self):
        self.service.clear_cart()

    def complete_order(self):
        request = CompleteOrderRequest(self.get_cart_items())
        self._validate(request)
        return self.service.complete_order()

    def get_completed_orders(self):
        return self.service.get_completed_orders()