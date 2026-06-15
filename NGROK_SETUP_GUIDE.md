# Connecting GoCart API to ngrok - Complete Step-by-Step Guide

## What is ngrok?

ngrok is a tool that creates a secure public URL tunnel to your local API server, making it accessible from the internet. This allows you to:
- Test webhooks without deploying to production
- Share your local API with others
- Access your API from mobile devices
- Integrate with external services

## Prerequisites

Before you start, make sure you have:
- GoCart API running on `http://127.0.0.1:8001`
- Windows PowerShell or Command Prompt
- Internet connection
- Valid email address

## Step 1: Download and Install ngrok

### Option A: Download from Website

1. Go to **https://ngrok.com/download**
2. Select **Windows** as your platform
3. Click **Download** (the ZIP file)
4. Extract the ZIP file to a folder (e.g., `C:\ngrok`)

### Option B: Using Chocolatey (Faster)

If you have Chocolatey installed:

```powershell
choco install ngrok
```

### Option C: Using npm

```powershell
npm install -g ngrok
```

## Step 2: Create a Free ngrok Account

1. Go to **https://ngrok.com/signup**
2. Enter your email and create a password
3. Click **Sign up**
4. Check your email and verify your account
5. Log in to your ngrok dashboard

## Step 3: Get Your ngrok Authentication Token

1. Log in to **https://dashboard.ngrok.com**
2. Go to **Auth** (left menu)
3. Copy your **Authtoken**
4. Save it somewhere safe (you'll use it in the next step)

## Step 4: Configure ngrok on Your Computer

### Step 4a: Open PowerShell

Press `Win + X` and select **Windows PowerShell (Admin)**

### Step 4b: Navigate to ngrok folder

If you extracted ngrok to `C:\ngrok`, run:

```powershell
cd C:\ngrok
```

### Step 4c: Add Your Authentication Token

Replace `YOUR_AUTH_TOKEN` with the token from Step 3:

```powershell
.\ngrok.exe config add-authtoken YOUR_AUTH_TOKEN
```

**Example**:
```powershell
.\ngrok.exe config add-authtoken 2V6ibNbQ7jJ2Z6Rq7qH_5jyWu8oN2pR3sT4u5vW6x
```

You should see:
```
Authtoken saved to configuration file
```

## Step 5: Make Sure Your API is Running

In another PowerShell window, start your GoCart API:

```powershell
cd c:\Users\USER\GoCart
python -m gocart_system.main
```

Wait for the message:
```
Uvicorn running on http://127.0.0.1:8001
```

**Keep this window open** - your API must stay running while using ngrok.

## Step 6: Start ngrok Tunnel

In your ngrok PowerShell window (from Step 4), run:

```powershell
.\ngrok.exe http 8001
```

Or if ngrok is in your PATH:

```powershell
ngrok http 8001
```

## Step 7: You're Connected! 🎉

You should see output like:

```
ngrok by @inconshreveable

Session Status                online
Account                       your-email@gmail.com
Version                       3.0.0
Region                        us (United States)
Hostname                       [random-string].ngrok.io
Forwarding                    https://[random-string].ngrok.io -> http://localhost:8001

Connections                   ttl    opn    rt1    rt5    p50    p95
                              0      0      0.00s  0.00s  0.00s  0.00s

HTTP Requests
```

**Copy the URL**: `https://[random-string].ngrok.io`

This is your public API URL! It will change every time you restart ngrok (unless you have a paid account).

## Step 8: Test Your ngrok Connection

Open a new PowerShell window and test the connection:

```powershell
# Test the root endpoint
curl https://[random-string].ngrok.io/

# Example:
curl https://abc123def456.ngrok.io/
```

You should get:
```
{"message":"GoCart API is running","status":"active"}
```

## Step 9: Use Your Public API URL

Now you can use your ngrok URL for external requests!

### Login via ngrok URL

```powershell
curl -X POST https://[random-string].ngrok.io/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### Send SMS via ngrok URL

```powershell
curl -X POST https://[random-string].ngrok.io/api/sms/send `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "phone_number": "+1234567890",
    "message": "Test message from ngrok",
    "priority": "NORMAL"
  }'
```

## Step 10: Update Your Application Settings

### For Mobile Apps or External Services

Update your API base URL to use the ngrok URL:

**Before** (local only):
```
http://127.0.0.1:8001
```

**After** (accessible from internet):
```
https://[your-ngrok-url].ngrok.io
```

### Example Python Configuration

```python
# Before
API_URL = "http://127.0.0.1:8001"

# After
API_URL = "https://abc123def456.ngrok.io"
```

### Example JavaScript Configuration

```javascript
// Before
const API_BASE = 'http://localhost:8001';

// After
const API_BASE = 'https://abc123def456.ngrok.io';
```

## Step 11: Monitor Your Requests

While ngrok is running, you can access the **Web Inspector**:

1. Open your browser
2. Go to `http://localhost:4040`
3. See all requests in real-time
4. Inspect request/response details
5. Replay requests for testing

## Common Tasks

### Task 1: Keep ngrok Running in Background

Option A - Use ngrok Dashboard (paid):
- Premium accounts get static URLs that don't change

Option B - Create a batch file:

Create a file `start_ngrok.bat`:
```batch
@echo off
cd C:\ngrok
.\ngrok.exe http 8001
pause
```

Double-click to start whenever needed.

### Task 2: Use Static Subdomain (Paid Feature)

If you have ngrok Pro:

```powershell
ngrok http --subdomain=myapi-gocart 8001
```

Your URL will always be:
```
https://myapi-gocart.ngrok.io
```

### Task 3: Add Custom Headers

```powershell
ngrok http 8001 --add-header x-gocart=true
```

### Task 4: Restrict Access with IP Whitelist

```powershell
ngrok http 8001 --allow-from-ips "192.168.1.100,203.0.113.50"
```

## Troubleshooting

### Problem: "Command ngrok not found"

**Solution**: Navigate to ngrok folder first:
```powershell
cd C:\ngrok
.\ngrok.exe http 8001
```

Or add ngrok to system PATH.

### Problem: "Port 8001 in use"

**Solution**: Kill the process using port 8001:
```powershell
# Find the process
Get-NetTCPConnection -LocalPort 8001

# Kill it (replace PID with the actual process ID)
Stop-Process -Id PID -Force
```

### Problem: "Invalid auth token"

**Solution**: Re-add your token:
1. Go to https://dashboard.ngrok.com/auth
2. Copy your **Authtoken**
3. Run: `ngrok config add-authtoken YOUR_TOKEN`

### Problem: Connection timeout

**Solutions**:
1. Make sure API is running on port 8001
2. Check firewall settings
3. Restart ngrok tunnel
4. Try different region (ngrok http --region us 8001)

### Problem: ngrok URL changes every time

**Solution**: Use paid ngrok account for static URLs

**Free alternative**: Create a script to update your settings when ngrok restarts

## Complete Example: Full Testing Workflow

### Step 1: Start API

```powershell
cd c:\Users\USER\GoCart
python -m gocart_system.main
```

Keep this window open.

### Step 2: Start ngrok (in another window)

```powershell
cd C:\ngrok
.\ngrok.exe http 8001
```

Copy your ngrok URL from the output.

### Step 3: Register a User

```powershell
$API_URL = "https://abc123def456.ngrok.io"  # Replace with your URL

curl -X POST "$API_URL/api/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }' | ConvertFrom-Json | Select-Object -ExpandProperty data
```

### Step 4: Login

```powershell
$response = curl -X POST "$API_URL/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }' -UseBasicParsing | ConvertFrom-Json

$TOKEN = $response.data.access_token
echo "Token: $TOKEN"
```

### Step 5: Send SMS

```powershell
curl -X POST "$API_URL/api/sms/send" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "phone_number": "+1234567890",
    "message": "Test message",
    "priority": "HIGH"
  }' | ConvertFrom-Json
```

### Step 6: Check Queue Status

```powershell
curl -X GET "$API_URL/api/sms/queue/status" `
  -H "Authorization: Bearer $TOKEN" | ConvertFrom-Json
```

## Using ngrok with Postman

### Step 1: Create Collection Variable

1. Open Postman
2. Edit your collection
3. Go to **Variables** tab
4. Create variable: `ngrok_url`
5. Set value: `https://abc123def456.ngrok.io`
6. Click **Save**

### Step 2: Update Requests

Replace `{{base_url}}` with `{{ngrok_url}}` in all requests:

```
{{ngrok_url}}/api/auth/login
{{ngrok_url}}/api/sms/send
{{ngrok_url}}/api/sms/queue/status
```

### Step 3: Update Authtoken Script

In request **Tests** tab:
```javascript
if (pm.response.code === 200) {
  var jsonData = pm.response.json();
  pm.collectionVariables.set("access_token", jsonData.data.access_token);
}
```

Now all requests use ngrok URL automatically!

## Security Considerations

### ⚠️ Important Security Tips

1. **Never share your ngrok URL in public** - Anyone with the URL can access your API
2. **Use authentication** - Always require JWT tokens (you already have this)
3. **Enable IP whitelisting** (paid feature) if exposing sensitive data
4. **Use HTTPS only** - ngrok provides HTTPS by default ✓
5. **Change credentials** - Don't use the same credentials as your production API
6. **Monitor access** - Check ngrok's web inspector frequently
7. **Disable when not needed** - Stop ngrok when you're done testing
8. **Set rate limits** - Protect against abuse

### Example: Add Rate Limiting

```python
# In api.py, add this:
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(...):
    # Only 5 login attempts per minute per IP
    pass
```

## Advanced: Custom Domain with ngrok

### Option 1: Use ngrok Custom Domain (Paid)

```powershell
ngrok http --domain=my-api.ngrok.io 8001
```

### Option 2: Use Your Own Domain (CNAME)

1. Get ngrok static domain
2. Update your DNS CNAME to point to ngrok
3. Configure ngrok to use your domain

See: https://ngrok.com/docs/cloud-edge/domains/

## Stopping ngrok

### Method 1: Press Ctrl+C

In the ngrok window:
```
Press Ctrl + C
```

### Method 2: Kill the Process

```powershell
Get-Process ngrok | Stop-Process -Force
```

## What Happens After You Stop ngrok?

- Your ngrok URL becomes inaccessible
- All requests will fail with "Connection refused"
- Start ngrok again to get a new tunnel

## Summary

| Step | Command | Action |
|------|---------|--------|
| 1 | Download ngrok | Get ngrok binary |
| 2 | Create account | https://ngrok.com/signup |
| 3 | Get authtoken | Copy from dashboard |
| 4 | Configure | `ngrok config add-authtoken` |
| 5 | Start API | `python -m gocart_system.main` |
| 6 | Start ngrok | `ngrok http 8001` |
| 7 | Get public URL | Copy from ngrok output |
| 8 | Test connection | `curl https://[url]/` |
| 9 | Use in apps | Replace localhost with ngrok URL |

## Next Steps

- [ ] Set up ngrok with your GoCart API
- [ ] Test all endpoints using ngrok URL
- [ ] Update mobile app to use ngrok URL
- [ ] Configure external service webhooks
- [ ] Monitor requests via ngrok inspector
- [ ] Upgrade to ngrok Pro for static URLs
- [ ] Set up rate limiting and security

## Additional Resources

- **ngrok Documentation**: https://ngrok.com/docs
- **ngrok API Reference**: https://ngrok.com/docs/api
- **ngrok Best Practices**: https://ngrok.com/docs/cloud-edge/security
- **GoCart API Docs**: See API_FIXES_SUMMARY.md and SMS_QUEUE_DOCUMENTATION.md

