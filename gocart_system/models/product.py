class Product:
    def __init__(self, name, price, quantity, product_id=None):
        self.__id = product_id
        self.__name = name
        self.__price = price
        self.__quantity = quantity

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        self.__price = value

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, value):
        self.__quantity = value

    def __str__(self):
        return f"{self.__name} - ${self.__price} - Qty: {self.__quantity}"

    def to_dict(self):
        return {
            "id": self.__id,
            "name": self.__name,
            "price": self.__price,
            "quantity": self.__quantity,
        }
