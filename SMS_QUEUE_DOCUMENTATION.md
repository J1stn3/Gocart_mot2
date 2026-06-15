# SMS Message Queuing and Job Processing System

## Overview

GoCart now includes an advanced SMS message queuing system with the following features:

- **Priority-based queuing**: Messages can be sent with LOW, NORMAL, HIGH, or CRITICAL priority
- **Automatic retry mechanism**: Failed messages are automatically retried up to 3 times
- **Background processing**: Messages are processed asynchronously using worker threads
- **Database persistence**: Queue status is stored in the database for monitoring
- **Statistics tracking**: Real-time statistics on processed, sent, failed, and retried messages
- **Batch processing support**: Multiple messages can be queued simultaneously

## Architecture

### Components

1. **SmsQueueService**: Main queuing service with singleton pattern
   - Priority queue for message ordering
   - Multiple worker threads (processor, retry handler, stats updater)
   - Database persistence

2. **SmsMessage**: Data class representing a message in the queue
   - Contains message metadata (user_id, phone_number, message_text)
   - Tracks retry count and priority
   - Timestamps for creation and processing

3. **Database Tables**:
   - `sms_queue`: Stores all queued messages with their status
   - `sms_messages`: Original SMS messages (linked via message_id)
   - `sms_queue_stats`: Historical statistics

## API Endpoints

### 1. Send SMS Message
**Endpoint**: `POST /api/sms/send`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "phone_number": "+1234567890",
  "message": "Hello, this is a test message",
  "priority": "NORMAL"
}
```

**Priority Levels**:
- `LOW`: Processed after normal messages (3)
- `NORMAL`: Standard priority (2)
- `HIGH`: Processed before normal messages (1)
- `CRITICAL`: Highest priority (0)

**Response** (Success):
```json
{
  "success": true,
  "message": "SMS queued for sending",
  "data": {
    "message_id": 1,
    "phone_number": "+1234567890",
    "status": "QUEUED",
    "priority": "NORMAL",
    "queued_at": "2026-04-17T10:30:00"
  }
}
```

**Example Request** (with curl):
```bash
curl -X POST http://127.0.0.1:8001/api/sms/send \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "message": "Test message",
    "priority": "HIGH"
  }'
```

### 2. Get Queue Status
**Endpoint**: `GET /api/sms/queue/status`

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "queue_size": 5,
    "database_status": {
      "total": 15,
      "pending": 2,
      "queued": 3,
      "processing": 1,
      "sent": 8,
      "failed": 1,
      "retry": 0
    },
    "statistics": {
      "total_processed": 100,
      "total_sent": 95,
      "total_failed": 5,
      "total_retried": 12
    },
    "running": true
  }
}
```

### 3. Get Specific Message Status
**Endpoint**: `GET /api/sms/queue/message/{message_id}`

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "message_id": 1,
    "status": "SENT",
    "retry_count": 0,
    "max_retries": 3,
    "error_message": null,
    "sent_at": "2026-04-17T10:30:05",
    "created_at": "2026-04-17T10:30:00",
    "last_retry_at": null
  }
}
```

### 4. Get Queue Statistics
**Endpoint**: `GET /api/sms/queue/stats`

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "runtime_stats": {
      "total_processed": 150,
      "total_sent": 142,
      "total_failed": 8,
      "total_retried": 15
    },
    "queue_status": {
      "queue_size": 3,
      "database_status": {
        "total": 150,
        "pending": 0,
        "queued": 1,
        "processing": 2,
        "sent": 142,
        "failed": 3,
        "retry": 2
      },
      "statistics": { ... },
      "running": true
    }
  }
}
```

## Message States

### Queue State Diagram

```
PENDING → QUEUED → PROCESSING → SENT
                       ↓
                   FAILED (after max retries)
                       ↑
                   RETRY (with delay)
                       ↓
                   QUEUED (retry attempt)
```

### Status Definitions

| Status | Description |
|--------|-------------|
| PENDING | Message created, not yet queued |
| QUEUED | Message in processing queue |
| PROCESSING | Currently being sent to provider |
| SENT | Successfully sent to provider |
| FAILED | Failed to send after all retries |
| RETRY | Queued for retry attempt |
| DELIVERED | Confirmed delivery (when provider supports) |

## Retry Mechanism

### How Retries Work

1. **Initial Send**: Message is processed normally
2. **First Failure**: Message status changes to RETRY, retry_count increments
3. **Retry Queue**: Message is re-queued after 5-minute delay
4. **Second Attempt**: Message is processed again
5. **Repeat**: Steps 2-4 repeat up to max_retries (default: 3)
6. **Final Failure**: After 3 retries, message status becomes FAILED

### Configuration

```python
# In SmsMessage dataclass
max_retries: int = 3  # Maximum retry attempts
retry_delay: int = 5  # Minutes between retries
```

## Priority Queue Processing

### How Priorities Work

Messages are processed based on priority (lower number = higher priority):

- CRITICAL (0): Processed immediately
- HIGH (1): Processed before normal messages
- NORMAL (2): Standard processing
- LOW (3): Processed last

### Example Priority Processing Order

```
Queue order (by priority):
1. CRITICAL: "Urgent alert"        (priority=0)
2. HIGH: "Important notification"  (priority=1)
3. NORMAL: "Regular message"       (priority=2)
4. LOW: "Newsletter"               (priority=3)
```

## Background Workers

### Worker Threads

1. **SMS-Queue-Processor**
   - Continuously processes messages from the queue
   - Updates message status in database
   - Handles sending via provider integration
   - Default interval: 2 seconds (queue timeout)

2. **SMS-Retry-Handler**
   - Checks for messages in RETRY status
   - Re-queues messages after delay period
   - Default interval: 30 seconds

3. **SMS-Stats-Updater**
   - Saves statistics to database
   - Tracks performance metrics
   - Default interval: 60 seconds

## Database Schema

### sms_queue Table

```sql
CREATE TABLE sms_queue (
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
);
```

### sms_queue_stats Table

```sql
CREATE TABLE sms_queue_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_processed INT DEFAULT 0,
    total_sent INT DEFAULT 0,
    total_failed INT DEFAULT 0,
    total_retried INT DEFAULT 0,
    average_processing_time FLOAT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Integration with SMS Provider

### Current Implementation

The `_send_to_provider()` method is a placeholder for actual SMS provider integration.

### To Integrate with Twilio

```python
def _send_to_provider(self, message: SmsMessage) -> bool:
    try:
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        message_obj = client.messages.create(
            body=message.message_text,
            from_="+1234567890",  # Your Twilio number
            to=message.phone_number
        )
        
        return message_obj.status != 'failed'
    except Exception as e:
        logger.error(f"Twilio error: {str(e)}")
        return False
```

### To Integrate with AWS SNS

```python
def _send_to_provider(self, message: SmsMessage) -> bool:
    try:
        import boto3
        
        sns = boto3.client('sns')
        response = sns.publish(
            PhoneNumber=message.phone_number,
            Message=message.message_text
        )
        
        return 'MessageId' in response
    except Exception as e:
        logger.error(f"AWS SNS error: {str(e)}")
        return False
```

## Usage Examples

### Example 1: Send High Priority Notification

```bash
curl -X POST http://127.0.0.1:8001/api/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "message": "URGENT: Your account requires immediate attention",
    "priority": "CRITICAL"
  }'
```

### Example 2: Check Queue Status in Python

```python
import requests

headers = {"Authorization": f"Bearer {token}"}

# Get queue status
response = requests.get(
    "http://127.0.0.1:8001/api/sms/queue/status",
    headers=headers
)

print(f"Messages in queue: {response.json()['data']['queue_size']}")
print(f"Total sent: {response.json()['data']['statistics']['total_sent']}")
```

### Example 3: Monitor Specific Message

```python
import time

message_id = 1

while True:
    response = requests.get(
        f"http://127.0.0.1:8001/api/sms/queue/message/{message_id}",
        headers=headers
    )
    
    status = response.json()['data']['status']
    print(f"Message status: {status}")
    
    if status in ['SENT', 'FAILED']:
        break
    
    time.sleep(2)
```

## Performance Considerations

### Queue Performance

- **Message throughput**: ~100-500 messages/minute (depends on provider)
- **Queue size limit**: Limited only by database size
- **Memory usage**: ~1KB per message in memory queue
- **Database impact**: Minimal with indexed queries

### Optimization Tips

1. **Batch sending**: Group related messages by priority
2. **Off-peak processing**: Schedule non-critical messages during off-peak hours
3. **Database cleanup**: Archive old completed jobs periodically
4. **Provider limits**: Be aware of SMS provider rate limits

## Monitoring and Debugging

### Check Queue Health

```bash
# Get current statistics
curl -X GET http://127.0.0.1:8001/api/sms/queue/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Messages stuck in QUEUED | Worker threads crashed | Restart API server |
| High FAILED rate | Provider integration error | Check provider credentials |
| Memory usage increasing | Unprocessed messages accumulating | Check database queue table |
| Slow message processing | Low priority messages queued | Monitor queue load |

## Error Handling

All API endpoints return detailed error messages:

```json
{
  "detail": "Phone number is required"
}
```

Status codes:
- 200: Success
- 400: Bad request (validation error)
- 401: Unauthorized (missing/invalid token)
- 404: Resource not found
- 500: Server error

## Future Enhancements

Planned features for the SMS queuing system:

1. [ ] SMS delivery confirmation webhooks
2. [ ] Message scheduling (send at specific time)
3. [ ] Template-based messages
4. [ ] Bulk SMS operations
5. [ ] SMS analytics and reporting
6. [ ] Multiple provider failover
7. [ ] Message rate limiting per user
8. [ ] SMS delivery status tracking
9. [ ] Message history export
10. [ ] Admin dashboard for queue monitoring

