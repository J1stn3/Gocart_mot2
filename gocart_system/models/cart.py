from .cart_item import CartItem

class Cart:
    def __init__(self):
        self.__items = []

    def add_item(self, product, quantity):
        # Check if product already in cart
        for item in self.__items:
            if item.product.name == product.name:
                item.quantity += quantity
                return
        self.__items.append(CartItem(product, quantity))

    def remove_item(self, product_name):
        self.__items = [item for item in self.__items if item.product.name != product_name]

    def get_items(self):
        return self.__items

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.__items)

    def clear(self):
        self.__items = []