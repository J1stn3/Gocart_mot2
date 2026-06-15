"""
Advanced SMS Message Queuing Service with job processing, retries, and priority support.
"""
from __future__ import annotations
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import logging

from mysql.connector import Error
from .database_connection import DatabaseConnection

logger = logging.getLogger(__name__)


class QueueStatus(Enum):
    """Status of messages in the queue."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRY = "RETRY"
    DELIVERED = "DELIVERED"


class Priority(Enum):
    """Message priority levels."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class SmsMessage:
    """SMS message object for queue processing."""
    message_id: int
    user_id: int
    phone_number: str
    message_text: str
    priority: Priority = Priority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "message_text": self.message_text,
            "priority": self.priority.name,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SmsQueueService:
    """
    Advanced SMS message queuing service with priority, retries, and batch processing.
    Uses singleton pattern to ensure single queue instance.
    """
    _instance = None
    _message_queue: queue.PriorityQueue = queue.PriorityQueue()
    _running = False
    _stats = {
        "total_processed": 0,
        "total_sent": 0,
        "total_failed": 0,
        "total_retried": 0,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._db = DatabaseConnection()
            self._db.connect()
            self._create_tables()
            self._start_workers()

    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        # SMS Queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_queue (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message_id INT NOT NULL,
                user_id INT NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                message_text TEXT NOT NULL,
                priority INT DEFAULT 2,
                status VARCHAR(20) DEFAULT 'PENDING',
                retry_count INT DEFAULT 0,
                max_retries INT DEFAULT 3,
                error_message TEXT NULL,
                last_retry_at TIMESTAMP NULL,
                sent_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_priority (priority),
                INDEX idx_user_id (user_id),
                FOREIGN KEY (message_id) REFERENCES sms_messages(id)
            )
        """)
        
        # SMS Job Stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_queue_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                total_processed INT DEFAULT 0,
                total_sent INT DEFAULT 0,
                total_failed INT DEFAULT 0,
                total_retried INT DEFAULT 0,
                average_processing_time FLOAT DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()

    def _start_workers(self):
        """Start queue processing worker threads."""
        if not SmsQueueService._running:
            SmsQueueService._running = True
            
            # Main queue processor
            processor_thread = threading.Thread(
                target=self._process_queue_worker,
                daemon=True,
                name="SMS-Queue-Processor"
            )
            processor_thread.start()
            
            # Retry handler
            retry_thread = threading.Thread(
                target=self._retry_handler,
                daemon=True,
                name="SMS-Retry-Handler"
            )
            retry_thread.start()
            
            # Stats updater
            stats_thread = threading.Thread(
                target=self._update_stats_worker,
                daemon=True,
                name="SMS-Stats-Updater"
            )
            stats_thread.start()
            
            logger.info("SMS queue workers started")

    def _process_queue_worker(self):
        """Main worker to process messages from queue."""
        while SmsQueueService._running:
            try:
                # Get message from priority queue (non-blocking)
                try:
                    priority, message = SmsQueueService._message_queue.get(timeout=2)
                    self._process_message(message)
                except queue.Empty:
                    time.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"Queue processor error: {str(e)}")
                time.sleep(2)

    def _retry_handler(self):
        """Handle retry logic for failed messages."""
        while SmsQueueService._running:
            try:
                self._retry_failed_messages()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Retry handler error: {str(e)}")
                time.sleep(30)

    def _update_stats_worker(self):
        """Update statistics in database."""
        while SmsQueueService._running:
            try:
                self._save_stats()
                time.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Stats updater error: {str(e)}")
                time.sleep(60)

    def send_sms(
        self,
        user_id: int,
        phone_number: str,
        message_text: str,
        priority: Priority = Priority.NORMAL,
        auto_queue: bool = True
    ) -> Dict[str, Any]:
        """
        Send an SMS message (queues it automatically).
        
        Args:
            user_id: User ID sending the message
            phone_number: Recipient phone number
            message_text: Message text to send
            priority: Message priority (LOW, NORMAL, HIGH, CRITICAL)
            auto_queue: Automatically add to processing queue
        
        Returns:
            Dictionary with message_id and queue status
        """
        if not phone_number:
            raise ValueError("Phone number is required")
        if not message_text:
            raise ValueError("Message text is required")
        
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert into sms_messages
            cursor.execute("""
                INSERT INTO sms_messages (user_id, phone_number, message, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (user_id, phone_number, message_text, QueueStatus.PENDING.value))
            
            message_id = cursor.lastrowid
            conn.commit()
            
            # Queue for processing
            sms_msg = SmsMessage(
                message_id=message_id,
                user_id=user_id,
                phone_number=phone_number,
                message_text=message_text,
                priority=priority
            )
            
            if auto_queue:
                self.queue_message(sms_msg)
            
            return {
                "message_id": message_id,
                "phone_number": phone_number,
                "status": QueueStatus.QUEUED.value,
                "priority": priority.name,
                "queued_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to send SMS: {str(e)}")
            raise
        finally:
            cursor.close()

    def queue_message(self, message: SmsMessage) -> int:
        """
        Add message to processing queue.
        
        Args:
            message: SmsMessage object to queue
        
        Returns:
            Position in queue
        """
        # Update database status
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sms_queue (message_id, user_id, phone_number, message_text, priority, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                message.message_id,
                message.user_id,
                message.phone_number,
                message.message_text,
                message.priority.value,
                QueueStatus.QUEUED.value
            ))
            
            conn.commit()
            queue_entry_id = cursor.lastrowid
        finally:
            cursor.close()
        
        # Add to priority queue (lower priority value = higher priority)
        SmsQueueService._message_queue.put((message.priority.value, message))
        
        logger.info(f"Message {message.message_id} queued with priority {message.priority.name}")
        return queue_entry_id

    def _process_message(self, message: SmsMessage) -> bool:
        """
        Process a single SMS message.
        
        Args:
            message: SmsMessage to process
        
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update status to PROCESSING
            cursor.execute("""
                UPDATE sms_queue SET status = %s WHERE message_id = %s
            """, (QueueStatus.PROCESSING.value, message.message_id))
            conn.commit()
            
            # Simulate sending (in production, integrate with SMS provider)
            success = self._send_to_provider(message)
            
            if success:
                # Update to SENT
                cursor.execute("""
                    UPDATE sms_messages SET status = %s, sent_at = NOW() WHERE id = %s
                """, (QueueStatus.SENT.value, message.message_id))
                
                cursor.execute("""
                    UPDATE sms_queue SET status = %s, sent_at = NOW() WHERE message_id = %s
                """, (QueueStatus.SENT.value, message.message_id))
                
                conn.commit()
                SmsQueueService._stats["total_sent"] += 1
                
                logger.info(f"Message {message.message_id} sent successfully")
                return True
            else:
                raise Exception("Provider returned failure")
                
        except Exception as e:
            logger.error(f"Failed to process message {message.message_id}: {str(e)}")
            
            # Check if we should retry
            message.retry_count += 1
            
            if message.retry_count < message.max_retries:
                cursor.execute("""
                    UPDATE sms_queue SET status = %s, retry_count = %s, last_retry_at = NOW(), error_message = %s
                    WHERE message_id = %s
                """, (QueueStatus.RETRY.value, message.retry_count, str(e), message.message_id))
                
                SmsQueueService._stats["total_retried"] += 1
                logger.info(f"Message {message.message_id} queued for retry (attempt {message.retry_count})")
            else:
                cursor.execute("""
                    UPDATE sms_queue SET status = %s, error_message = %s WHERE message_id = %s
                """, (QueueStatus.FAILED.value, str(e), message.message_id))
                
                cursor.execute("""
                    UPDATE sms_messages SET status = %s WHERE id = %s
                """, (QueueStatus.FAILED.value, message.message_id))
                
                SmsQueueService._stats["total_failed"] += 1
                logger.error(f"Message {message.message_id} failed permanently after {message.retry_count} retries")
            
            conn.commit()
            return False
        finally:
            cursor.close()
            processing_time = time.time() - start_time
            SmsQueueService._stats["total_processed"] += 1

    def _send_to_provider(self, message: SmsMessage) -> bool:
        """
        Send message to SMS provider (placeholder for actual implementation).
        In production, integrate with Twilio, AWS SNS, etc.
        
        Args:
            message: SmsMessage to send
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Placeholder: Simulate API call
            logger.debug(f"Sending to provider: {message.phone_number} - {message.message_text[:50]}")
            
            # Simulate occasional failures for testing retry logic
            import random
            if random.random() < 0.1:  # 10% failure rate for testing
                return False
            
            return True
        except Exception as e:
            logger.error(f"Provider error: {str(e)}")
            return False

    def _retry_failed_messages(self):
        """Requeue messages that are in RETRY status."""
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get messages with RETRY status that haven't been retried recently
            cursor.execute("""
                SELECT message_id, user_id, phone_number, message_text, priority, retry_count
                FROM sms_queue
                WHERE status = %s AND (last_retry_at IS NULL OR last_retry_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE))
                LIMIT 50
            """, (QueueStatus.RETRY.value,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                message = SmsMessage(
                    message_id=row["message_id"],
                    user_id=row["user_id"],
                    phone_number=row["phone_number"],
                    message_text=row["message_text"],
                    priority=Priority(row["priority"]),
                    retry_count=row["retry_count"]
                )
                
                # Re-queue the message
                self.queue_message(message)
                logger.info(f"Message {message.message_id} re-queued after retry delay")
        finally:
            cursor.close()

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and statistics."""
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'QUEUED' THEN 1 ELSE 0 END) as queued,
                    SUM(CASE WHEN status = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = 'SENT' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'RETRY' THEN 1 ELSE 0 END) as retry
                FROM sms_queue
            """)
            
            row = cursor.fetchone()
            
            return {
                "queue_size": SmsQueueService._message_queue.qsize(),
                "database_status": {
                    "total": row["total"] or 0,
                    "pending": row["pending"] or 0,
                    "queued": row["queued"] or 0,
                    "processing": row["processing"] or 0,
                    "sent": row["sent"] or 0,
                    "failed": row["failed"] or 0,
                    "retry": row["retry"] or 0,
                },
                "statistics": SmsQueueService._stats,
                "running": SmsQueueService._running,
            }
        finally:
            cursor.close()

    def get_message_status(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific message."""
        conn = self._db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM sms_queue WHERE message_id = %s
            """, (message_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "message_id": row["message_id"],
                    "status": row["status"],
                    "retry_count": row["retry_count"],
                    "max_retries": row["max_retries"],
                    "error_message": row["error_message"],
                    "sent_at": row["sent_at"].isoformat() if row["sent_at"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "last_retry_at": row["last_retry_at"].isoformat() if row["last_retry_at"] else None,
                }
            return None
        finally:
            cursor.close()

    def _save_stats(self):
        """Save statistics to database."""
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sms_queue_stats (total_processed, total_sent, total_failed, total_retried)
                VALUES (%s, %s, %s, %s)
            """, (
                SmsQueueService._stats["total_processed"],
                SmsQueueService._stats["total_sent"],
                SmsQueueService._stats["total_failed"],
                SmsQueueService._stats["total_retried"]
            ))
            
            conn.commit()
        finally:
            cursor.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed statistics."""
        return {
            "runtime_stats": SmsQueueService._stats,
            "queue_status": self.get_queue_status(),
        }
