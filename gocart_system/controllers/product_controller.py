from ..services.product_services import ProductServices
from ..requests import CreateProductRequest, UpdateProductRequest, DeleteProductRequest

class ProductController:

    def __init__(self):
        self.service = ProductServices()

    def _validate(self, request):
        result = request.validate()
        if not result.is_valid:
            raise ValueError('; '.join(result.errors.values()))
        return result.validated_data

    def create_product(self, name, price, quantity):
        request = CreateProductRequest({'name': name, 'price': price, 'quantity': quantity})
        validated = self._validate(request)
        self.service.create_product(validated['name'], validated['price'], validated['quantity'])

    def get_products(self):
        return self.service.get_products()

    def update_product(self, index, name, price, quantity):
        products = self.get_products()
        request = UpdateProductRequest({'name': name, 'price': price, 'quantity': quantity}, index, products)
        validated = self._validate(request)
        self.service.update_product(validated['product_index'], validated['name'], validated['price'], validated['quantity'])

    def delete_product(self, index):
        products = self.get_products()
        request = DeleteProductRequest(index, products)
        validated = self._validate(request)
        self.service.delete_product(validated['product_index'])