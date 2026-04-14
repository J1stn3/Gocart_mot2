# requests/__init__.py
from .base_request import BaseRequest, ValidationResult
from .product_requests import CreateProductRequest, UpdateProductRequest, DeleteProductRequest
from .cart_requests import AddToCartRequest, RemoveFromCartRequest, CompleteOrderRequest

__all__ = [
    'BaseRequest',
    'ValidationResult',
    'CreateProductRequest',
    'UpdateProductRequest',
    'DeleteProductRequest',
    'AddToCartRequest',
    'RemoveFromCartRequest',
    'CompleteOrderRequest'
]