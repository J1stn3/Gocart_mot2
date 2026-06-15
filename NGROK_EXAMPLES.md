# ngrok + GoCart API - Practical Examples

## Complete Working Examples

### Example 1: Simple Login and Send SMS

**File**: `test_gocart_ngrok.ps1`

```powershell
# Configuration
$NGROK_URL = "https://abc123def456.ngrok.io"  # Replace with your URL
$USERNAME = "testuser"
$PASSWORD = "SecurePass123!"
$PHONE = "+1234567890"
$MESSAGE = "Hello from GoCart via ngrok!"

Write-Host "Testing GoCart API via ngrok" -ForegroundColor Cyan

# Step 1: Register
Write-Host "`n[1/4] Registering user..." -ForegroundColor Yellow

$registerBody = @{
    username = "newuser_$(Get-Random)"
    email = "test_$(Get-Random)@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$registerResponse = curl -X POST "$NGROK_URL/api/auth/register" `
    -H "Content-Type: application/json" `
    -d $registerBody -UseBasicParsing | ConvertFrom-Json

Write-Host "✓ User registered: $($registerResponse.data.username)" -ForegroundColor Green

# Step 2: Login
Write-Host "`n[2/4] Logging in..." -ForegroundColor Yellow

$loginBody = @{
    username = "jus@gmail.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$loginResponse = curl -X POST "$NGROK_URL/api/auth/login" `
    -H "Content-Type: application/json" `
    -d $loginBody -UseBasicParsing | ConvertFrom-Json

$TOKEN = $loginResponse.data.access_token
Write-Host "✓ Logged in successfully" -ForegroundColor Green
Write-Host "Token: $($TOKEN.Substring(0,20))..." -ForegroundColor Cyan

# Step 3: Send SMS
Write-Host "`n[3/4] Sending SMS..." -ForegroundColor Yellow

$smsBody = @{
    phone_number = $PHONE
    message = $MESSAGE
    priority = "HIGH"
} | ConvertTo-Json

$smsResponse = curl -X POST "$NGROK_URL/api/sms/send" `
    -H "Authorization: Bearer $TOKEN" `
    -H "Content-Type: application/json" `
    -d $smsBody -UseBasicParsing | ConvertFrom-Json

$MESSAGE_ID = $smsResponse.data.message_id
Write-Host "✓ SMS queued successfully" -ForegroundColor Green
Write-Host "Message ID: $MESSAGE_ID" -ForegroundColor Cyan

# Step 4: Check Status
Write-Host "`n[4/4] Checking message status..." -ForegroundColor Yellow

Start-Sleep -Seconds 2

$statusResponse = curl -X GET "$NGROK_URL/api/sms/queue/message/$MESSAGE_ID" `
    -H "Authorization: Bearer $TOKEN" -UseBasicParsing | ConvertFrom-Json

Write-Host "✓ Message status: $($statusResponse.data.status)" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test completed successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
```

**Run it:**
```powershell
powershell -ExecutionPolicy Bypass -File test_gocart_ngrok.ps1
```

---

### Example 2: Batch Send Multiple SMS with Progress

**File**: `bulk_sms_ngrok.ps1`

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$NgrokUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [Parameter(Mandatory=$false)]
    [int]$DelayMs = 500
)

# List of numbers to send to
$phones = @(
    @{ number = "+1111111111"; message = "First message"; priority = "HIGH" },
    @{ number = "+2222222222"; message = "Second message"; priority = "NORMAL" },
    @{ number = "+3333333333"; message = "Third message"; priority = "NORMAL" },
    @{ number = "+4444444444"; message = "Fourth message"; priority = "LOW" }
)

$results = @()
$count = 0
$total = $phones.Count

Write-Host "Starting bulk SMS send..." -ForegroundColor Cyan

foreach ($phone in $phones) {
    $count++
    Write-Host "[$count/$total] Sending to $($phone.number)..." -ForegroundColor Yellow
    
    try {
        $body = @{
            phone_number = $phone.number
            message = $phone.message
            priority = $phone.priority
        } | ConvertTo-Json
        
        $response = curl -X POST "$NgrokUrl/api/sms/send" `
            -H "Authorization: Bearer $Token" `
            -H "Content-Type: application/json" `
            -d $body -UseBasicParsing -ErrorAction Stop | ConvertFrom-Json
        
        $results += @{
            phone = $phone.number
            message_id = $response.data.message_id
            status = "SENT"
            timestamp = Get-Date
        }
        
        Write-Host "✓ Message ID: $($response.data.message_id)" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed: $_" -ForegroundColor Red
        $results += @{
            phone = $phone.number
            status = "FAILED"
            error = $_.Exception.Message
            timestamp = Get-Date
        }
    }
    
    Start-Sleep -Milliseconds $DelayMs
}

# Summary
Write-Host "`n========== SUMMARY ==========" -ForegroundColor Cyan
Write-Host "Total sent: $(($results | Where {$_.status -eq 'SENT'}).Count)" -ForegroundColor Green
Write-Host "Total failed: $(($results | Where {$_.status -eq 'FAILED'}).Count)" -ForegroundColor Red
Write-Host "============================" -ForegroundColor Cyan

# Export results
$results | Export-Csv -Path "sms_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation
Write-Host "`nResults saved to CSV" -ForegroundColor Yellow
```

**Run it:**
```powershell
$token = "your_token_here"
$url = "https://abc123def456.ngrok.io"
powershell -ExecutionPolicy Bypass -File bulk_sms_ngrok.ps1 -NgrokUrl $url -Token $token
```

---

### Example 3: Continuous Monitoring Dashboard

**File**: `monitor_queue.ps1`

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$NgrokUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$Token
)

Write-Host "Starting Queue Monitor..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

$interval = 5  # seconds

while ($true) {
    Clear-Host
    Write-Host "========== SMS QUEUE STATUS ==========" -ForegroundColor Cyan
    Write-Host "Last updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    try {
        $response = curl -X GET "$NgrokUrl/api/sms/queue/status" `
            -H "Authorization: Bearer $Token" `
            -UseBasicParsing | ConvertFrom-Json
        
        $stats = $response.data
        
        # Queue size
        Write-Host "Queue Size: $($stats.queue_size) messages" -ForegroundColor Yellow
        Write-Host ""
        
        # Database status
        Write-Host "Database Status:" -ForegroundColor Cyan
        $db = $stats.database_status
        Write-Host "  Total:       $($db.total)" -ForegroundColor White
        Write-Host "  Pending:     $($db.pending)" -ForegroundColor Yellow
        Write-Host "  Queued:      $($db.queued)" -ForegroundColor Blue
        Write-Host "  Processing:  $($db.processing)" -ForegroundColor Cyan
        Write-Host "  Sent:        $($db.sent)" -ForegroundColor Green
        Write-Host "  Failed:      $($db.failed)" -ForegroundColor Red
        Write-Host "  Retry:       $($db.retry)" -ForegroundColor Yellow
        Write-Host ""
        
        # Statistics
        Write-Host "Overall Statistics:" -ForegroundColor Cyan
        $s = $stats.statistics
        Write-Host "  Processed: $($s.total_processed)" -ForegroundColor White
        Write-Host "  Sent:      $($s.total_sent)" -ForegroundColor Green
        Write-Host "  Failed:    $($s.total_failed)" -ForegroundColor Red
        Write-Host "  Retried:   $($s.total_retried)" -ForegroundColor Yellow
        Write-Host ""
        
        # Health status
        Write-Host "Health:" -ForegroundColor Cyan
        if ($stats.running) {
            Write-Host "  Status: RUNNING ✓" -ForegroundColor Green
        } else {
            Write-Host "  Status: STOPPED ✗" -ForegroundColor Red
        }
        
        # Calculate success rate
        if ($s.total_processed -gt 0) {
            $successRate = [math]::Round(($s.total_sent / $s.total_processed) * 100, 2)
            Write-Host "  Success Rate: $successRate%" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Host "ERROR: Failed to connect to API" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host "Refreshing in $interval seconds..." -ForegroundColor Gray
    
    Start-Sleep -Seconds $interval
}
```

**Run it:**
```powershell
$token = "your_token"
$url = "https://abc123def456.ngrok.io"
powershell -ExecutionPolicy Bypass -File monitor_queue.ps1 -NgrokUrl $url -Token $token
```

---

### Example 4: Postman Collection JSON

**File**: `GoCart_ngrok.postman_collection.json`

```json
{
  "info": {
    "name": "GoCart ngrok API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"testuser\",\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{ngrok_url}}/api/auth/register",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"testuser\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{ngrok_url}}/api/auth/login",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "auth", "login"]
            },
            "tests": "if (pm.response.code === 200) {\n  var jsonData = pm.response.json();\n  pm.collectionVariables.set(\"access_token\", jsonData.data.access_token);\n  console.log(\"Token saved: \" + jsonData.data.access_token.substring(0, 20) + \"...\");\n}"
          }
        }
      ]
    },
    {
      "name": "SMS Queue",
      "item": [
        {
          "name": "Send SMS",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"phone_number\": \"+1234567890\",\n  \"message\": \"Test message from ngrok\",\n  \"priority\": \"HIGH\"\n}"
            },
            "url": {
              "raw": "{{ngrok_url}}/api/sms/send",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "sms", "send"]
            }
          }
        },
        {
          "name": "Get Queue Status",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{ngrok_url}}/api/sms/queue/status",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "sms", "queue", "status"]
            }
          }
        },
        {
          "name": "Get Message Status",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{ngrok_url}}/api/sms/queue/message/1",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "sms", "queue", "message", "1"]
            }
          }
        },
        {
          "name": "Get Queue Stats",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{ngrok_url}}/api/sms/queue/stats",
              "host": ["{{ngrok_url}}"],
              "path": ["api", "sms", "queue", "stats"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "ngrok_url",
      "value": "https://your-ngrok-url.ngrok.io",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    }
  ]
}
```

**How to use:**
1. Import into Postman
2. Set `ngrok_url` variable to your ngrok URL
3. Run Login request first to get token
4. Run other requests

---

## Complete Step-by-Step Workflow

### Scenario: Testing GoCart SMS Feature via ngrok

```
Step 1: Setup
├─ Download and install ngrok
├─ Create ngrok account
├─ Get authtoken
└─ Configure ngrok

Step 2: Start Services
├─ Start GoCart API (port 8001)
└─ Start ngrok tunnel

Step 3: Get Access
├─ Register user (or use existing)
├─ Login to get token
└─ Copy token

Step 4: Test SMS
├─ Send SMS via ngrok URL
├─ Monitor queue status
└─ Check message status

Step 5: Monitor
├─ Watch requests in ngrok inspector (http://localhost:4040)
├─ Track statistics
└─ Debug any issues

Step 6: Cleanup
└─ Stop ngrok and API
```

---

## Performance Benchmarks

### Expected Performance via ngrok

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Login | 50-150ms | ~100/min |
| Send SMS | 20-50ms | ~1000/min |
| Queue Status | 10-30ms | ~5000/min |
| Message Status | 10-30ms | ~5000/min |

**Notes**:
- Times vary based on internet speed
- Free ngrok may have lower limits
- Paid ngrok has higher rate limits
- Local testing (~5x faster for reference)

---

## Troubleshooting via ngrok

### Debugging Failed SMS

```powershell
# 1. Check message status
curl "$URL/api/sms/queue/message/1" -H "Authorization: Bearer $TOKEN"

# 2. Check error message in response
# Look for "error_message" field

# 3. Common errors:
# - "Invalid phone number format"
# - "SMS provider error"
# - "Rate limit exceeded"

# 4. Check queue statistics
curl "$URL/api/sms/queue/stats" -H "Authorization: Bearer $TOKEN"

# 5. View full logs via ngrok inspector
# http://localhost:4040
```

### Network Issues

```powershell
# Check if ngrok tunnel is alive
curl https://your-url.ngrok.io/

# Check ngrok status
ngrok status

# Restart if needed
# Ctrl+C and run: ngrok http 8001
```

---

## Next Steps

1. **Deploy to production** - Use static ngrok domain or own domain
2. **Mobile testing** - Test GoCart app with ngrok URL
3. **Webhook integration** - Set up third-party webhooks
4. **Load testing** - Test with multiple concurrent requests
5. **Security hardening** - Implement rate limiting and IP whitelisting

---

**Ready to test? Start with Example 1 above!**
