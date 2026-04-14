from .base_request import BaseRequest, ValidationResult

class CreateProductRequest(BaseRequest):
    """Request validation for creating a new product."""

    def validate(self) -> ValidationResult:
        """Validate product creation data."""
        # Validate product name
        if not self.validate_string_length('name', 'Product name', min_length=1, max_length=255):
            pass  # Error already added

        # Validate price
        if not self.validate_price('price', 'Price'):
            pass  # Error already added

        # Validate quantity
        if not self.validate_non_negative_integer('quantity', 'Quantity'):
            pass  # Error already added

        return self.result

class UpdateProductRequest(BaseRequest):
    """Request validation for updating an existing product."""

    def __init__(self, data: dict, product_index: int, products_list: list):
        super().__init__(data)
        self.product_index = product_index
        self.products_list = products_list

    def validate(self) -> ValidationResult:
        """Validate product update data."""
        # Validate product index
        if not self._validate_product_index():
            return self.result

        # Validate product name
        if not self.validate_string_length('name', 'Product name', min_length=1, max_length=255):
            pass  # Error already added

        # Validate price
        if not self.validate_price('price', 'Price'):
            pass  # Error already added

        # Validate quantity
        if not self.validate_non_negative_integer('quantity', 'Quantity'):
            pass  # Error already added

        return self.result

    def _validate_product_index(self) -> bool:
        """Validate that the product index is valid."""
        try:
            index = int(self.product_index)
            if index < 0:
                self.result.add_error('product_index', "Product index cannot be negative.")
                return False
            if index >= len(self.products_list):
                self.result.add_error('product_index', f"Product index {index} is out of range. Valid range: 0 to {len(self.products_list) - 1}.")
                return False
            self.result.set_data('product_index', index)
            return True
        except (ValueError, TypeError):
            self.result.add_error('product_index', "Product index must be a valid integer.")
            return False

class DeleteProductRequest(BaseRequest):
    """Request validation for deleting a product."""

    def __init__(self, product_index: int, products_list: list):
        super().__init__({})
        self.product_index = product_index
        self.products_list = products_list

    def validate(self) -> ValidationResult:
        """Validate product deletion request."""
        try:
            index = int(self.product_index)
            if index < 0:
                self.result.add_error('product_index', "Product index cannot be negative.")
                return self.result
            if index >= len(self.products_list):
                self.result.add_error('product_index', f"Product index {index} is out of range. Valid range: 0 to {len(self.products_list) - 1}.")
                return self.result
            self.result.set_data('product_index', index)
            return self.result
        except (ValueError, TypeError):
            self.result.add_error('product_index', "Product index must be a valid integer.")
            return self.result