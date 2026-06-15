from __future__ import annotations
import threading
import queue
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from mysql.connector import Error

from .database_connection import DatabaseConnection


class JobStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SmsJobService:
    _instance = None
    _job_queue: queue.Queue = queue.Queue()
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._start_worker()

    def _start_worker(self):
        if not SmsJobService._running:
            SmsJobService._running = True
            worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            worker_thread.start()

    def _process_queue(self):
        while SmsJobService._running:
            try:
                if not SmsJobService._job_queue.empty():
                    job = SmsJobService._job_queue.get()
                    self._execute_job(job)
                time.sleep(1)
            except Exception:
                time.sleep(1)

    def _execute_job(self, job: Dict[str, Any]):
        try:
            job_id = job["job_id"]
            sms_id = job["sms_id"]
            user_id = job["user_id"]
            new_status = job["new_status"]

            db = DatabaseConnection()
            db.connect()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE sms_messages SET status = %s, sent_at = NOW(), updated_at = NOW() WHERE id = %s AND user_id = %s",
                (new_status, sms_id, user_id),
            )
            conn.commit()
            cursor.close()
            conn.close()

            self._update_job_status(job_id, JobStatus.COMPLETED)
        except Exception as e:
            self._update_job_status(job_id, JobStatus.FAILED, str(e))

    def _update_job_status(self, job_id: int, status: JobStatus, error: Optional[str] = None):
        db = DatabaseConnection()
        db.connect()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sms_jobs SET status = %s, error_message = %s, completed_at = NOW() WHERE id = %s",
            (status.value, error, job_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

    def create_queue_table(self):
        db = DatabaseConnection()
        db.connect()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sms_id INT NOT NULL,
                user_id INT NOT NULL,
                new_status VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'PENDING',
                error_message TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                INDEX idx_jobs_status (status)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def enqueue_job(self, sms_id: int, user_id: int, new_status: str) -> int:
        self.create_queue_table()

        db = DatabaseConnection()
        db.connect()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sms_jobs (sms_id, user_id, new_status, status) VALUES (%s, %s, %s, 'PENDING')",
            (sms_id, user_id, new_status),
        )
        job_id = int(cursor.lastrowid)
        conn.commit()
        cursor.close()
        conn.close()

        job = {
            "job_id": job_id,
            "sms_id": sms_id,
            "user_id": user_id,
            "new_status": new_status,
        }
        SmsJobService._job_queue.put(job)

        return job_id

    def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        db = DatabaseConnection()
        db.connect()
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, sms_id, user_id, new_status, status, error_message, created_at, completed_at FROM sms_jobs WHERE id = %s",
            (job_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return {
                "job_id": int(row["id"]),
                "sms_id": int(row["sms_id"]),
                "new_status": str(row["new_status"]),
                "status": str(row["status"]),
                "error_message": row["error_message"],
                "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                "completed_at": row["completed_at"].isoformat() if row["completed_at"] and hasattr(row["completed_at"], "isoformat") else None,
            }
        return None

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        db = DatabaseConnection()
        db.connect()
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, sms_id, user_id, new_status, status, error_message, created_at, completed_at FROM sms_jobs ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        results = []
        for row in rows:
            results.append({
                "job_id": int(row["id"]),
                "sms_id": int(row["sms_id"]),
                "new_status": str(row["new_status"]),
                "status": str(row["status"]),
                "error_message": row["error_message"],
                "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                "completed_at": row["completed_at"].isoformat() if row["completed_at"] and hasattr(row["completed_at"], "isoformat") else None,
            })
        return results