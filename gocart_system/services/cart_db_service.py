from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from mysql.connector import Error

from .database_connection import DatabaseConnection


@dataclass
class CartItemRow:
    product_id: int
    name: str
    unit_price: Decimal
    quantity: int

    def to_api_dict(self) -> dict:
        return {
            "product": {
                "id": self.product_id,
                "name": self.name,
                "price": float(self.unit_price),
            },
            "quantity": self.quantity,
            "subtotal": float(self.unit_price * self.quantity),
        }


class CartDbService:
    """
    MySQL-backed cart + order logic.

    Notes:
    - Stock is reserved immediately when items are added to cart (product.quantity decremented).
    - Stock is restored when items are removed/cleared.
    - Checkout finalizes the cart and creates an order snapshot.
    """

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()
        self.db.connect()

    def _conn(self):
        conn = self.db.get_connection()
        if conn is None:
            raise ConnectionError("Cannot connect to MySQL database")
        return conn

    def _get_or_create_open_cart_id(self, user_id: int, cursor) -> int:
        cursor.execute(
            "SELECT id FROM carts WHERE user_id = %s AND status = 'open' ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])

        cursor.execute(
            "INSERT INTO carts (user_id, status, created_at, updated_at) VALUES (%s, 'open', NOW(), NOW())",
            (user_id,),
        )
        return int(cursor.lastrowid)

    def get_cart(self, user_id: int) -> Tuple[List[CartItemRow], Decimal]:
        conn = self._conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT c.id AS cart_id
                FROM carts c
                WHERE c.user_id = %s AND c.status = 'open'
                ORDER BY c.id DESC
                LIMIT 1
                """,
                (user_id,),
            )
            cart_row = cursor.fetchone()
            if not cart_row:
                return [], Decimal("0.00")

            cart_id = int(cart_row["cart_id"])
            cursor.execute(
                """
                SELECT p.id AS product_id, p.name, ci.unit_price, ci.quantity
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id = %s
                ORDER BY p.id
                """,
                (cart_id,),
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        items: List[CartItemRow] = []
        total = Decimal("0.00")
        for r in rows:
            item = CartItemRow(
                product_id=int(r["product_id"]),
                name=str(r["name"]),
                unit_price=Decimal(str(r["unit_price"])),
                quantity=int(r["quantity"]),
            )
            items.append(item)
            total += item.unit_price * item.quantity

        return items, total

    def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        conn = self._conn()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            cart_id = self._get_or_create_open_cart_id(user_id, cursor)

            # Lock product row
            cursor.execute(
                "SELECT id, name, price, quantity FROM products WHERE id = %s FOR UPDATE",
                (product_id,),
            )
            p = cursor.fetchone()
            if not p:
                raise ValueError("Product not found")

            _, _, price, stock_qty = p
            stock_qty = int(stock_qty)
            if stock_qty < quantity:
                raise ValueError("Insufficient stock")

            # Lock existing cart item (if any)
            cursor.execute(
                "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s FOR UPDATE",
                (cart_id, product_id),
            )
            ci = cursor.fetchone()

            if ci:
                cart_item_id, existing_qty = int(ci[0]), int(ci[1])
                cursor.execute(
                    """
                    UPDATE cart_items
                    SET quantity = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (existing_qty + quantity, cart_item_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO cart_items (cart_id, product_id, quantity, unit_price, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (cart_id, product_id, quantity, price),
                )

            # Reserve stock
            cursor.execute(
                "UPDATE products SET quantity = quantity - %s WHERE id = %s",
                (quantity, product_id),
            )
            cursor.execute("UPDATE carts SET updated_at = NOW() WHERE id = %s", (cart_id,))

            conn.commit()
            cursor.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def remove_from_cart(self, user_id: int, product_id: int) -> None:
        conn = self._conn()
        try:
            conn.start_transaction()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM carts WHERE user_id = %s AND status = 'open' ORDER BY id DESC LIMIT 1 FOR UPDATE",
                (user_id,),
            )
            cart_row = cursor.fetchone()
            if not cart_row:
                raise ValueError("Cart is empty")

            cart_id = int(cart_row[0])

            cursor.execute(
                "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s FOR UPDATE",
                (cart_id, product_id),
            )
            ci = cursor.fetchone()
            if not ci:
                raise ValueError("Item not found in cart")

            cart_item_id, qty = int(ci[0]), int(ci[1])

            # Restore stock
            cursor.execute(
                "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                (qty, product_id),
            )
            cursor.execute("DELETE FROM cart_items WHERE id = %s", (cart_item_id,))
            cursor.execute("UPDATE carts SET updated_at = NOW() WHERE id = %s", (cart_id,))

            conn.commit()
            cursor.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def clear_cart(self, user_id: int) -> None:
        conn = self._conn()
        try:
            conn.start_transaction()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM carts WHERE user_id = %s AND status = 'open' ORDER BY id DESC LIMIT 1 FOR UPDATE",
                (user_id,),
            )
            cart_row = cursor.fetchone()
            if not cart_row:
                conn.commit()
                cursor.close()
                return

            cart_id = int(cart_row[0])
            cursor.execute(
                "SELECT product_id, quantity FROM cart_items WHERE cart_id = %s FOR UPDATE",
                (cart_id,),
            )
            rows = cursor.fetchall()
            for product_id, qty in rows:
                cursor.execute(
                    "UPDATE products SET quantity = quantity + %s WHERE id = %s",
                    (int(qty), int(product_id)),
                )
            cursor.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))
            cursor.execute("UPDATE carts SET updated_at = NOW() WHERE id = %s", (cart_id,))
            conn.commit()
            cursor.close()
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def checkout(self, user_id: int) -> Dict[str, Any]:
        conn = self._conn()
        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id
                FROM carts
                WHERE user_id = %s AND status = 'open'
                ORDER BY id DESC
                LIMIT 1
                FOR UPDATE
                """,
                (user_id,),
            )
            cart_row = cursor.fetchone()
            if not cart_row:
                raise ValueError("Cart is empty")

            cart_id = int(cart_row["id"])

            cursor.execute(
                """
                SELECT p.id AS product_id, p.name, ci.unit_price, ci.quantity
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id = %s
                FOR UPDATE
                """,
                (cart_id,),
            )
            items = cursor.fetchall()
            if not items:
                raise ValueError("Cart is empty")

            total = Decimal("0.00")
            for it in items:
                total += Decimal(str(it["unit_price"])) * int(it["quantity"])

            # Create order
            cursor.execute(
                "INSERT INTO orders (user_id, cart_id, total, created_at) VALUES (%s, %s, %s, NOW())",
                (user_id, cart_id, total),
            )
            order_id = int(cursor.lastrowid)

            # Snapshot order items
            for it in items:
                unit_price = Decimal(str(it["unit_price"]))
                qty = int(it["quantity"])
                line_total = unit_price * qty
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity, line_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (order_id, int(it["product_id"]), str(it["name"]), unit_price, qty, line_total),
                )

            # Finalize cart
            cursor.execute(
                "UPDATE carts SET status = 'completed', updated_at = NOW() WHERE id = %s",
                (cart_id,),
            )

            conn.commit()
            cursor.close()

            # Return in the same shape the UI expects today
            return {
                "order_id": order_id,
                "items": [
                    {
                        "product": {
                            "id": int(it["product_id"]),
                            "name": str(it["name"]),
                            "price": float(Decimal(str(it["unit_price"]))),
                        },
                        "quantity": int(it["quantity"]),
                    }
                    for it in items
                ],
                "total": float(total),
                "created_at": datetime.utcnow().isoformat(),
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def list_orders(self, user_id: int) -> List[Dict[str, Any]]:
        conn = self._conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, total, created_at
                FROM orders
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (user_id,),
            )
            orders = cursor.fetchall()

            results: List[Dict[str, Any]] = []
            for o in orders:
                order_id = int(o["id"])
                cursor.execute(
                    """
                    SELECT product_id, product_name, unit_price, quantity
                    FROM order_items
                    WHERE order_id = %s
                    ORDER BY id
                    """,
                    (order_id,),
                )
                items = cursor.fetchall()
                results.append(
                    {
                        "order_id": order_id,
                        "items": [
                            {
                                "product": {
                                    "id": int(it["product_id"]),
                                    "name": str(it["product_name"]),
                                    "price": float(Decimal(str(it["unit_price"]))),
                                },
                                "quantity": int(it["quantity"]),
                            }
                            for it in items
                        ],
                        "total": float(Decimal(str(o["total"]))),
                        "created_at": (o["created_at"].isoformat() if hasattr(o["created_at"], "isoformat") else str(o["created_at"])),
                    }
                )

            return results
        finally:
            cursor.close()
            conn.close()

    def clear_orders(self, user_id: int) -> None:
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
