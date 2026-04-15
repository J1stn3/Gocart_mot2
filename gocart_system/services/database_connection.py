import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import threading

load_dotenv()

class DatabaseConnection:
    _instance = None
    _initialized = False
    _init_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        try:
            # Initialize database/schema once (safe for concurrent requests)
            if not self._initialized:
                with self._init_lock:
                    if not self._initialized:
                        self._ensure_database_and_tables()
                        self._initialized = True

            # Return a fresh connection per call (FastAPI-safe)
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                port=int(os.getenv("DB_PORT", 3306)),
                database="gocart_db",
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def _ensure_database_and_tables(self):
        # Create DB if missing
        admin_conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", 3306)),
        )
        admin_cursor = admin_conn.cursor()
        admin_cursor.execute("CREATE DATABASE IF NOT EXISTS gocart_db")
        admin_cursor.close()
        admin_conn.close()

        # Ensure tables inside gocart_db
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", 3306)),
            database="gocart_db",
        )
        self._ensure_tables(conn)
        conn.close()

    def _ensure_tables(self, conn):
        cursor = conn.cursor()

        def table_exists(table_name: str) -> bool:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = %s
                """,
                (table_name,),
            )
            return int(cursor.fetchone()[0]) > 0

        def column_exists(table_name: str, column_name: str) -> bool:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = %s
                  AND column_name = %s
                """,
                (table_name, column_name),
            )
            return int(cursor.fetchone()[0]) > 0

        def recreate_cart_order_tables_if_legacy():
            """
            Legacy tables (from early versions) don't have required columns like:
            - carts.user_id/status/updated_at
            - cart_items.unit_price/updated_at and unique(cart_id, product_id)
            - orders/order_items tables may not exist
            For consistency, when legacy schema is detected, we recreate those tables.
            """
            legacy = False
            if table_exists("carts") and not column_exists("carts", "user_id"):
                legacy = True
            if table_exists("cart_items") and not column_exists("cart_items", "unit_price"):
                legacy = True

            if legacy:
                # Drop in FK-safe order (dev-friendly migration)
                cursor.execute("DROP TABLE IF EXISTS order_items")
                cursor.execute("DROP TABLE IF EXISTS orders")
                cursor.execute("DROP TABLE IF EXISTS cart_items")
                cursor.execute("DROP TABLE IF EXISTS carts")

        # Recreate legacy cart/order tables before creating new ones
        recreate_cart_order_tables_if_legacy()

        # Products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                price DECIMAL(18, 2) NOT NULL,
                quantity INT NOT NULL
            )
        """)

        # Users (auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NULL,
                last_login DATETIME NULL,
                failed_login_attempts INT DEFAULT 0,
                is_locked BOOLEAN DEFAULT FALSE,
                locked_until DATETIME NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_valid BOOLEAN DEFAULT TRUE,
                UNIQUE KEY uq_user_sessions_refresh_token (refresh_token(255)),
                INDEX idx_user_sessions_user_id (user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # Carts / cart items (per user, one active cart)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                INDEX idx_carts_user_status (user_id, status),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cart_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                UNIQUE KEY uq_cart_product (cart_id, product_id),
                FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        # Orders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                cart_id INT NULL,
                total DECIMAL(18, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_orders_user_created (user_id, created_at),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                unit_price DECIMAL(18, 2) NOT NULL,
                quantity INT NOT NULL,
                line_total DECIMAL(18, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        # If tables already existed with smaller decimals, widen them.
        # (Safe to run repeatedly; if already widened, MySQL is a no-op.)
        for stmt in [
            "ALTER TABLE products MODIFY COLUMN price DECIMAL(18,2) NOT NULL",
            "ALTER TABLE cart_items MODIFY COLUMN unit_price DECIMAL(18,2) NOT NULL",
            "ALTER TABLE orders MODIFY COLUMN total DECIMAL(18,2) NOT NULL",
            "ALTER TABLE order_items MODIFY COLUMN unit_price DECIMAL(18,2) NOT NULL",
            "ALTER TABLE order_items MODIFY COLUMN line_total DECIMAL(18,2) NOT NULL",
        ]:
            try:
                cursor.execute(stmt)
            except Exception:
                # Ignore if table/column missing (created later) or permissions/locks in dev
                pass

        conn.commit()
        cursor.close()

    def disconnect(self):
        # Connections are per-call; nothing to do here.
        return

    def get_connection(self):
        return self.connect()
