# SMS Queue Quick Start Guide

## Quick Overview

The SMS Queue system allows you to:
- **Send SMS messages** with automatic background processing
- **Set priorities** for urgent messages (CRITICAL, HIGH, NORMAL, LOW)
- **Monitor message status** in real-time
- **Track statistics** on sent, failed, and retried messages
- **Automatic retries** for failed messages (up to 3 times)

## Getting Started

### Step 1: Get Your Authentication Token

First, register or login to get a bearer token:

```bash
# Register (if new user)
curl -X POST http://127.0.0.1:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://127.0.0.1:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Copy the `access_token` from the response** - you'll need this for all requests.

### Step 2: Send Your First SMS

```bash
curl -X POST http://127.0.0.1:8001/api/sms/send \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "message": "Hello! This is your first queued SMS.",
    "priority": "NORMAL"
  }'
```

**Response**:
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

**Save the `message_id`** - you can use it to check the status later.

### Step 3: Check Message Status

```bash
curl -X GET http://127.0.0.1:8001/api/sms/queue/message/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "message_id": 1,
    "status": "SENT",
    "retry_count": 0,
    "sent_at": "2026-04-17T10:30:02"
  }
}
```

## Common Tasks

### Task 1: Send an Urgent SMS

Use `CRITICAL` priority for urgent messages:

```bash
curl -X POST http://127.0.0.1:8001/api/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "message": "ALERT: Suspicious login detected on your account!",
    "priority": "CRITICAL"
  }'
```

### Task 2: Monitor Queue Health

Check how many messages are waiting:

```bash
curl -X GET http://127.0.0.1:8001/api/sms/queue/status \
  -H "Authorization: Bearer $TOKEN"
```

Look for:
- `queue_size`: Messages waiting to be processed
- `total_sent`: Successfully sent messages
- `total_failed`: Messages that failed after retries

### Task 3: Bulk Send Messages

Send multiple messages (they'll be queued in priority order):

```python
import requests
import json

TOKEN = "your_access_token"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

messages = [
    {
        "phone_number": "+1111111111",
        "message": "Message 1",
        "priority": "NORMAL"
    },
    {
        "phone_number": "+2222222222",
        "message": "Message 2",
        "priority": "HIGH"
    },
    {
        "phone_number": "+3333333333",
        "message": "Message 3",
        "priority": "NORMAL"
    }
]

for msg in messages:
    response = requests.post(
        "http://127.0.0.1:8001/api/sms/send",
        headers=headers,
        json=msg
    )
    print(f"Message sent: {response.json()['data']['message_id']}")
```

### Task 4: Get Overall Statistics

View total performance metrics:

```bash
curl -X GET http://127.0.0.1:8001/api/sms/queue/stats \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Task 5: Build a Simple Message Status Tracker

```python
import requests
import time

TOKEN = "your_access_token"
MESSAGE_ID = 1  # From sending a message

headers = {"Authorization": f"Bearer {TOKEN}"}

print(f"Tracking message {MESSAGE_ID}...")

while True:
    response = requests.get(
        f"http://127.0.0.1:8001/api/sms/queue/message/{MESSAGE_ID}",
        headers=headers
    )
    
    data = response.json()['data']
    status = data['status']
    
    print(f"Status: {status}")
    
    if status == "SENT":
        print("✓ Message sent successfully!")
        break
    elif status == "FAILED":
        print(f"✗ Message failed: {data['error_message']}")
        break
    else:
        print("  Waiting for processing...")
        time.sleep(2)
```

## Priority Levels Explained

| Priority | Use Case | Processing Order |
|----------|----------|------------------|
| **CRITICAL** | Emergency alerts, security issues | Sent immediately |
| **HIGH** | Important notifications, OTPs | Sent before normal messages |
| **NORMAL** | Regular notifications, reminders | Standard processing |
| **LOW** | Newsletters, marketing messages | Sent after other messages |

### Example: Different Priorities

```python
import requests

TOKEN = "your_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Critical - emergency alert
requests.post(
    "http://127.0.0.1:8001/api/sms/send",
    headers=headers,
    json={
        "phone_number": "+1234567890",
        "message": "EMERGENCY: System maintenance starting now",
        "priority": "CRITICAL"
    }
)

# High - OTP code
requests.post(
    "http://127.0.0.1:8001/api/sms/send",
    headers=headers,
    json={
        "phone_number": "+1234567890",
        "message": "Your OTP: 123456",
        "priority": "HIGH"
    }
)

# Normal - reminder
requests.post(
    "http://127.0.0.1:8001/api/sms/send",
    headers=headers,
    json={
        "phone_number": "+1234567890",
        "message": "Reminder: Your appointment is tomorrow",
        "priority": "NORMAL"
    }
)

# Low - newsletter
requests.post(
    "http://127.0.0.1:8001/api/sms/send",
    headers=headers,
    json={
        "phone_number": "+1234567890",
        "message": "Check out our latest deals this week!",
        "priority": "LOW"
    }
)
```

## Understanding Message States

```
Your SMS journey:
1. PENDING → Created, not yet queued
2. QUEUED → Waiting in the processing queue
3. PROCESSING → Currently being sent to SMS provider
4. SENT → Successfully sent! ✓

If something goes wrong:
3. PROCESSING → Attempt to send failed
4. RETRY → Waiting to retry (delay of 5 minutes)
5. QUEUED → Attempting again
... (repeat up to 3 times)
6. FAILED → Gave up after 3 failed attempts ✗
```

## Monitoring Tips

### Check Queue Health Regularly

```bash
# Save this as check_queue.sh
TOKEN="your_token"

while true; do
  echo "=== SMS Queue Status ==="
  curl -s http://127.0.0.1:8001/api/sms/queue/status \
    -H "Authorization: Bearer $TOKEN" | python -m json.tool
  echo ""
  sleep 10
done
```

### Identify Problematic Messages

```python
import requests

TOKEN = "your_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Get statistics
stats = requests.get(
    "http://127.0.0.1:8001/api/sms/queue/stats",
    headers=headers
).json()

failed = stats['data']['queue_status']['database_status']['failed']
retrying = stats['data']['queue_status']['database_status']['retry']

print(f"Messages failed: {failed}")
print(f"Messages retrying: {retrying}")

if failed > 0 or retrying > 0:
    print("⚠️  Review failed messages and check SMS provider integration")
```

## Troubleshooting

### Problem: Message stuck in QUEUED state

**Cause**: Worker threads may not be processing

**Solution**:
```bash
# Restart the API server
# Kill the current process and run:
python -m gocart_system.main
```

### Problem: Message shows FAILED with error

**Cause**: SMS provider integration error (credentials, rate limit, etc.)

**Solution**:
1. Check provider account (Twilio, AWS SNS, etc.)
2. Verify API credentials
3. Check rate limits
4. Review error message for details

### Problem: High failure rate

**Causes**:
- Invalid phone numbers
- Provider account issues
- Network connectivity
- Rate limiting

**Solutions**:
1. Validate phone numbers before sending
2. Monitor provider account status
3. Implement exponential backoff in retry logic
4. Check queue statistics regularly

## API Reference Quick Lookup

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sms/send` | POST | Send a new SMS message |
| `/api/sms/queue/status` | GET | Get current queue status |
| `/api/sms/queue/message/{id}` | GET | Get specific message status |
| `/api/sms/queue/stats` | GET | Get detailed statistics |

All endpoints require `Authorization: Bearer <token>` header.

## Next Steps

- **Integrate with SMS Provider**: Modify `_send_to_provider()` in `sms_queue_service.py`
- **Set Up Monitoring**: Create dashboards for queue statistics
- **Enable Webhooks**: Add delivery confirmation callbacks
- **Implement Rate Limiting**: Prevent account suspension due to rate limits
- **Schedule Messages**: Add support for sending at specific times

