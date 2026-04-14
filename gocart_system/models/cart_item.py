from .product import Product

class CartItem:
    def __init__(self, product, quantity):
        self.__product = product
        self.__quantity = quantity

    @property
    def product(self):
        return self.__product

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        self.__quantity = value

    def get_total_price(self):
        return self.__product.price * self.__quantity

    def to_dict(self):
        return {
            "product": self.__product.to_dict(),
            "quantity": self.__quantity,
            "subtotal": self.get_total_price(),
        }
        return self.__product.price * self.__quantity

    def __str__(self):
        return f"{self.__product.name} - Qty: {self.__quantity} - Total: ${self.get_total_price()}"