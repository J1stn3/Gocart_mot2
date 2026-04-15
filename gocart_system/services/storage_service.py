from .database_connection import DatabaseConnection
from ..models.product import Product

class StorageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = DatabaseConnection()
        return cls._instance

    def add_product(self, product):
        connection = self.db.get_connection()
        if connection is None:
            raise ConnectionError("Cannot connect to MySQL database")

        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
                (product.name, product.price, product.quantity)
            )
            connection.commit()
            product.id = cursor.lastrowid
            return product
        finally:
            cursor.close()
            connection.close()

    def get_products(self):
        connection = self.db.get_connection()
        if connection is None:
            raise ConnectionError("Cannot connect to MySQL database")

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name, price, quantity FROM products ORDER BY id")
            rows = cursor.fetchall()
            return [Product(row['name'], float(row['price']), int(row['quantity']), product_id=row['id']) for row in rows]
        finally:
            cursor.close()
            connection.close()

    def update_product(self, index, product):
        products = self.get_products()
        if 0 <= index < len(products):
            product_id = products[index].id
            self.update_product_by_id(product_id, product)

    def update_product_by_id(self, product_id, product):
        connection = self.db.get_connection()
        if connection is None:
            raise ConnectionError("Cannot connect to MySQL database")

        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE products SET name = %s, price = %s, quantity = %s WHERE id = %s",
                (product.name, product.price, product.quantity, product_id)
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def delete_product(self, index):
        products = self.get_products()
        if 0 <= index < len(products):
            product_id = products[index].id
            connection = self.db.get_connection()
            if connection is None:
                raise ConnectionError("Cannot connect to MySQL database")
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                connection.commit()
            finally:
                cursor.close()
                connection.close()

    def find_product_by_name(self, name):
        connection = self.db.get_connection()
        if connection is None:
            raise ConnectionError("Cannot connect to MySQL database")

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name, price, quantity FROM products WHERE name = %s LIMIT 1", (name,))
            row = cursor.fetchone()
            if row:
                return Product(row['name'], float(row['price']), int(row['quantity']), product_id=row['id'])
            return None
        finally:
            cursor.close()
            connection.close()

    def get_product_by_id(self, product_id):
        connection = self.db.get_connection()
        if connection is None:
            raise ConnectionError("Cannot connect to MySQL database")

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name, price, quantity FROM products WHERE id = %s", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(row['name'], float(row['price']), int(row['quantity']), product_id=row['id'])
            return None
        finally:
            cursor.close()
            connection.close()
