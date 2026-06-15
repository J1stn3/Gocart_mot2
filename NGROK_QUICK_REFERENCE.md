# ngrok Quick Reference Card

## Most Common Commands

### Start a Basic Tunnel
```powershell
ngrok http 8001
```

### Check if ngrok is Installed
```powershell
ngrok version
```

### View All Config
```powershell
ngrok config edit
```

### Add Your Authtoken
```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### View Web Inspector
```
http://localhost:4040
```
(Open in browser while ngrok is running)

---

## GoCart-Specific Commands

### Start GoCart API First
```powershell
cd c:\Users\USER\GoCart
python -m gocart_system.main
```

### Then in Another Window, Start ngrok
```powershell
cd C:\ngrok
ngrok http 8001
```

### Test Your ngrok Connection
```powershell
# Get your ngrok URL from the output, then:
curl https://YOUR-NGROK-URL/

# Example:
curl https://abc123def456.ngrok.io/
```

### Login to Get Token
```powershell
$URL = "https://abc123def456.ngrok.io"
$response = curl -X POST "$URL/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"username":"user","password":"pass"}' -UseBasicParsing

$response
```

### Send SMS via ngrok
```powershell
$TOKEN = "your_token_here"
$URL = "https://abc123def456.ngrok.io"

curl -X POST "$URL/api/sms/send" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "phone_number":"+1234567890",
    "message":"Test",
    "priority":"NORMAL"
  }'
```

---

## Advanced Commands

### Use Specific Region
```powershell
ngrok http --region ap 8001  # asia-pacific
ngrok http --region au 8001  # australia
ngrok http --region eu 8001  # europe
ngrok http --region in 8001  # india
ngrok http --region jp 8001  # japan
ngrok http --region sa 8001  # south america
ngrok http --region us 8001  # united states (default)
```

### Static Subdomain (Paid Feature)
```powershell
ngrok http --subdomain=my-api 8001
# URL: https://my-api.ngrok.io
```

### Add Custom Headers to All Requests
```powershell
ngrok http --add-header x-gocart=true 8001
```

### IP Whitelist (Paid Feature)
```powershell
ngrok http --allow-from-ips "192.168.1.1,203.0.113.50" 8001
```

### Traffic Control
```powershell
ngrok http --traffic-control-allow "192.168.1.0/24" 8001
```

### Multiple Tunnels (Advanced)
```powershell
# Tunnel 1
ngrok http 8001

# Tunnel 2 (in another window)
ngrok http 3000
```

### Save Configuration to File
```powershell
ngrok config add-authtoken abc123def456
ngrok config add-api-key abc123def456
```

---

## Stopping ngrok

### Method 1 (Normal)
Press `Ctrl + C` in the ngrok window

### Method 2 (Force Kill)
```powershell
Get-Process ngrok | Stop-Process -Force
```

### Method 3 (Port 4040)
Go to http://localhost:4040 and click Stop button

---

## View Logs and Debugging

### View Full Debug Logs
```powershell
ngrok http -v 8001
```

### Show All Connections
```
http://localhost:4040  # View in browser
```

### Monitor in Real-Time
```powershell
# Keep terminal window open and watch for requests
# Go to http://localhost:4040 in browser
```

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| `command not found` | Add to PATH or use full path `C:\ngrok\ngrok.exe` |
| Port already in use | `Get-Process | Where {$_.Port -eq 8001}` |
| Invalid authtoken | Re-add: `ngrok config add-authtoken YOUR_TOKEN` |
| Connection refused | Make sure API is running on port 8001 |
| Timeout errors | Check internet connection |
| No output | Add `-v` flag: `ngrok http -v 8001` |
| URL keeps changing | Upgrade to ngrok Pro for static URLs |

---

## Environment Variables

### Set Default Region
```powershell
$env:NGROK_REGION = "eu"
```

### Set API Key
```powershell
$env:NGROK_AUTHTOKEN = "your_token"
```

---

## Configuration File Location

### Windows
```
C:\Users\YOUR_USERNAME\AppData\Roaming\.ngrok2\ngrok.yml
```

### View Config
```powershell
notepad $env:APPDATA\.ngrok2\ngrok.yml
```

### Edit Config
```powershell
ngrok config edit
```

---

## Example Config File

```yaml
authtoken: 2V6ibNbQ7jJ2Z6Rq7qH_5jyWu8oN2pR3sT4u5vW6x
region: us
log_level: info
log_format: json

tunnels:
  gocart:
    addr: 8001
    proto: http
```

---

## Useful URLs

| Resource | URL |
|----------|-----|
| ngrok Website | https://ngrok.com |
| Dashboard | https://dashboard.ngrok.com |
| Download | https://ngrok.com/download |
| Docs | https://ngrok.com/docs |
| Pricing | https://ngrok.com/pricing |
| Web Inspector | http://localhost:4040 |
| API Docs | https://ngrok.com/docs/api |

---

## Quick Start Flow

```
1. Start API:
   cd C:\Users\USER\GoCart
   python -m gocart_system.main

2. Open another window and start ngrok:
   cd C:\ngrok
   ngrok http 8001

3. Copy URL from ngrok output
   Example: https://abc123def456.ngrok.io

4. Test it:
   curl https://abc123def456.ngrok.io/

5. Use it in your app:
   Replace http://localhost:8001 
   with https://your-ngrok-url.ngrok.io

6. Monitor requests:
   http://localhost:4040
```

---

## Keyboard Shortcuts in ngrok

| Key | Action |
|-----|--------|
| `Ctrl + C` | Stop ngrok |
| `q` | Quit (same as Ctrl+C) |
| Click on Web UI | View request details |

---

## Authentication Header Examples

```powershell
# Bearer Token
-H "Authorization: Bearer YOUR_TOKEN_HERE"

# Basic Auth
-H "Authorization: Basic BASE64_ENCODED"

# API Key
-H "X-API-Key: YOUR_API_KEY"

# Custom Header
-H "X-Custom-Header: value"
```

---

## Testing All GoCart Endpoints via ngrok

```powershell
# Set variables
$URL = "https://YOUR-NGROK-URL"
$TOKEN = "YOUR_TOKEN"

# Test Auth
curl "$URL/api/auth/login" ...

# Test Products
curl "$URL/api/products" -H "Authorization: Bearer $TOKEN"

# Test Cart
curl "$URL/api/cart" -H "Authorization: Bearer $TOKEN"

# Test SMS
curl "$URL/api/sms/send" -H "Authorization: Bearer $TOKEN" ...

# Test Queue
curl "$URL/api/sms/queue/status" -H "Authorization: Bearer $TOKEN"
```

---

## Pro Tips

1. **Keep ngrok running** - Don't close the window while testing
2. **Watch the inspector** - http://localhost:4040 shows all requests
3. **Test locally first** - Always test on http://localhost:8001 before ngrok
4. **Monitor bandwidth** - Large uploads/downloads can be slow over ngrok
5. **Use meaningful subdomains** - Makes URLs easier to remember (paid feature)
6. **Log everything** - Add `-v` flag for detailed logs
7. **Check rate limits** - ngrok has connection limits per minute
8. **Security first** - Never share ngrok URLs publicly

---

Last Updated: April 17, 2026
For latest info: https://ngrok.com/docs
