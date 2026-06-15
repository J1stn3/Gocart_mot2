from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from mysql.connector import Error

from .database_connection import DatabaseConnection


class SmsService:
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()
        self.db.connect()

    def _conn(self):
        conn = self.db.get_connection()
        if conn is None:
            raise ConnectionError("Cannot connect to MySQL database")
        return conn

    def send_sms(self, user_id: int, phone_number: str, message: str) -> Dict[str, Any]:
        if not phone_number:
            raise ValueError("Phone number is required")
        if not message:
            raise ValueError("Message is required")

        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO sms_messages (user_id, phone_number, message, status, created_at, updated_at)
                VALUES (%s, %s, %s, 'pending', NOW(), NOW())
                """,
                (user_id, phone_number, message),
            )
            sms_id = int(cursor.lastrowid)
            conn.commit()
            cursor.close()

            return {
                "sms_id": sms_id,
                "phone_number": phone_number,
                "message": message,
                "status": "pending",
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

    def get_sms_messages(self, user_id: int) -> List[Dict[str, Any]]:
        return self.get_all_sms(user_id, None)

    def get_all_sms(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._conn()
        cursor = conn.cursor(dictionary=True)
        try:
            if status:
                cursor.execute(
                    """
                    SELECT id, phone_number, message, status, sent_at, delivered_at, created_at
                    FROM sms_messages
                    WHERE user_id = %s AND status = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id, status.upper()),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, phone_number, message, status, sent_at, delivered_at, created_at
                    FROM sms_messages
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,),
                )
            rows = cursor.fetchall()

            results: List[Dict[str, Any]] = []
            for row in rows:
                results.append(self._row_to_dict(row))

            return results
        finally:
            cursor.close()
            conn.close()

    def get_all_sms_no_filter(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._conn()
        cursor = conn.cursor(dictionary=True)
        try:
            if status:
                cursor.execute(
                    """
                    SELECT id, user_id, phone_number, message, status, sent_at, delivered_at, created_at
                    FROM sms_messages
                    WHERE status = %s
                    ORDER BY created_at DESC
                    """,
                    (status.upper(),),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, user_id, phone_number, message, status, sent_at, delivered_at, created_at
                    FROM sms_messages
                    ORDER BY created_at DESC
                    """
                )
            rows = cursor.fetchall()

            results: List[Dict[str, Any]] = []
            for row in rows:
                results.append({
                    "sms_id": int(row["id"]),
                    "user_id": int(row["user_id"]),
                    "phone_number": str(row["phone_number"]),
                    "message": str(row["message"]),
                    "status": str(row["status"]).upper(),
                    "sent_at": row["sent_at"].isoformat() if row["sent_at"] else None,
                    "delivered_at": row["delivered_at"].isoformat() if row["delivered_at"] else None,
                    "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                })

            return results
        finally:
            cursor.close()
            conn.close()

    def _row_to_dict(self, row: dict) -> dict:
        return {
            "sms_id": int(row["id"]),
            "phone_number": str(row["phone_number"]),
            "message": str(row["message"]),
            "status": str(row["status"]).upper(),
            "sent_at": row["sent_at"].isoformat() if row["sent_at"] else None,
            "delivered_at": row["delivered_at"].isoformat() if row["delivered_at"] else None,
            "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
        }

    def get_sms_by_id(self, user_id: int, sms_id: int) -> Optional[Dict[str, Any]]:
        conn = self._conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, phone_number, message, status, sent_at, delivered_at, created_at
                FROM sms_messages
                WHERE user_id = %s AND id = %s
                """,
                (user_id, sms_id),
            )
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "sms_id": int(row["id"]),
                "phone_number": str(row["phone_number"]),
                "message": str(row["message"]),
                "status": str(row["status"]).upper(),
                "sent_at": row["sent_at"].isoformat() if row["sent_at"] else None,
                "delivered_at": row["delivered_at"].isoformat() if row["delivered_at"] else None,
                "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
            }
        finally:
            cursor.close()
            conn.close()

    def update_sms_status(self, user_id: int, sms_id: int, status: str) -> Dict[str, Any]:
        valid_statuses = ["PENDING", "SENT", "FAILED"]
        if status.upper() not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        status = status.upper()

        conn = self._conn()
        try:
            cursor = conn.cursor()

            sent_at = "NOW()" if status == "SENT" else "NULL"

            cursor.execute(
                f"""
                UPDATE sms_messages
                SET status = %s, sent_at = {sent_at}, updated_at = NOW()
                WHERE user_id = %s AND id = %s
                """,
                (status, user_id, sms_id),
            )
            conn.commit()
            cursor.close()

            return {"sms_id": sms_id, "status": status}
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def delete_sms(self, user_id: int, sms_id: int) -> None:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM sms_messages WHERE user_id = %s AND id = %s",
                (user_id, sms_id),
            )
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

    def update_sms(self, user_id: int, sms_id: int, phone_number: str, message: str) -> Dict[str, Any]:
        if not phone_number:
            raise ValueError("Phone number is required")
        if not message:
            raise ValueError("Message is required")

        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sms_messages
                SET phone_number = %s, message = %s, status = 'pending', updated_at = NOW()
                WHERE user_id = %s AND id = %s
                """,
                (phone_number, message, user_id, sms_id),
            )
            conn.commit()
            cursor.close()

            return {
                "sms_id": sms_id,
                "phone_number": phone_number,
                "message": message,
                "status": "pending",
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass