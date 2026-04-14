import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._connection and self._connection.is_connected():
            return self._connection

        try:
            self._connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                port=int(os.getenv('DB_PORT', 3306))
            )
            self._ensure_database()
            print("Connected to MySQL database")
            return self._connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def _ensure_database(self):
        cursor = self._connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS gocart_db")
        self._connection.database = 'gocart_db'
        cursor.close()
        self._ensure_tables()

    def _ensure_tables(self):
        cursor = self._connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cart_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        self._connection.commit()
        cursor.close()

    def disconnect(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("Disconnected from MySQL database")

    def get_connection(self):
        return self.connect()
