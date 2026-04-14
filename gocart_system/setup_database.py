import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect without specifying database to create it
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = connection.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS gocart_db")
        print("Database 'gocart_db' created successfully")

        # Switch to the database
        cursor.execute("USE gocart_db")

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL
            )
        """)
        print("Products table created successfully")

        # Create carts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Carts table created successfully")

        # Create cart_items table
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
        print("Cart items table created successfully")

        connection.commit()
        cursor.close()
        connection.close()
        print("Database setup completed successfully!")

    except Error as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    create_database()