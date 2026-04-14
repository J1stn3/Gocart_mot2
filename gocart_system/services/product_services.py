from .storage_service import StorageService
from ..models.product import Product


class ProductServices:
   

    def __init__(self):
        self.storage = StorageService()

    def create_product(self, name: str, price, quantity):
        
        if not name:
            raise ValueError("Product name cannot be empty")

        price = float(price)
        quantity = int(quantity)

        if price < 0:
            raise ValueError("Price cannot be negative")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        product = Product(name, price, quantity)

        return self.storage.add_product(product)

    def get_products(self):
        
        return self.storage.get_products()

    def update_product(self, index: int, name: str, price, quantity):
       
        if not name:
            raise ValueError("Product name cannot be empty")

        price = float(price)
        quantity = int(quantity)

        product = Product(name, price, quantity)

        self.storage.update_product(index, product)

    def delete_product(self, index: int):
       
        self.storage.delete_product(index)