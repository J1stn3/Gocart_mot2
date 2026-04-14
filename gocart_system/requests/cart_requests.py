from .base_request import BaseRequest, ValidationResult

class AddToCartRequest(BaseRequest):
    """Request validation for adding items to cart."""

    def __init__(self, data: dict, product_name: str, available_quantity: int):
        super().__init__(data)
        self.product_name = product_name
        self.available_quantity = available_quantity

    def validate(self) -> ValidationResult:
        """Validate add to cart request."""
        # Validate product name
        if not self._validate_product_name():
            return self.result

        # Validate quantity
        if not self.validate_positive_integer('quantity', 'Quantity'):
            return self.result

        # Check if enough stock is available
        quantity = self.result.data.get('quantity', 0)
        if quantity > self.available_quantity:
            self.result.add_error('quantity', f"Insufficient stock. Requested: {quantity}, Available: {self.available_quantity}.")
            return self.result

        return self.result

    def _validate_product_name(self) -> bool:
        """Validate product name."""
        if not self.product_name or (isinstance(self.product_name, str) and self.product_name.strip() == ""):
            self.result.add_error('product_name', "Product name is required.")
            return False
        if not isinstance(self.product_name, str):
            self.result.add_error('product_name', "Product name must be a string.")
            return False
        if len(self.product_name.strip()) > 255:
            self.result.add_error('product_name', "Product name cannot exceed 255 characters.")
            return False
        self.result.set_data('product_name', self.product_name.strip())
        return True

class RemoveFromCartRequest(BaseRequest):
    """Request validation for removing items from cart."""

    def __init__(self, product_name: str, cart_items: list):
        super().__init__({})
        self.product_name = product_name
        self.cart_items = cart_items

    def validate(self) -> ValidationResult:
        """Validate remove from cart request."""
        # Validate product name
        if not self._validate_product_name():
            return self.result

        # Check if product is in cart
        if not self._validate_product_in_cart():
            return self.result

        return self.result

    def _validate_product_name(self) -> bool:
        """Validate product name."""
        if not self.product_name or (isinstance(self.product_name, str) and self.product_name.strip() == ""):
            self.result.add_error("Product name is required.")
            return False
        if not isinstance(self.product_name, str):
            self.result.add_error("Product name must be a string.")
            return False
        if len(self.product_name.strip()) > 255:
            self.result.add_error("Product name cannot exceed 255 characters.")
            return False
        self.result.set_data('product_name', self.product_name.strip())
        return True

    def _validate_product_in_cart(self) -> bool:
        """Validate that the product exists in the cart."""
        product_name = self.result.data.get('product_name')
        for item in self.cart_items:
            if item.product.name == product_name:
                return True
        self.result.add_error('product_name', f"Product '{product_name}' is not in the cart.")
        return False

class CompleteOrderRequest(BaseRequest):
    """Request validation for completing an order."""

    def __init__(self, cart_items: list):
        super().__init__({})
        self.cart_items = cart_items

    def validate(self) -> ValidationResult:
        """Validate order completion request."""
        # Validate that cart is not empty
        if not self.cart_items:
            self.result.add_error('general', "Cart is empty. Add items before completing the order.")
            return self.result

        return self.result