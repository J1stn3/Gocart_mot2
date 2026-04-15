# GoCart Secure System - Quick Start Guide

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- A modern web browser or Flet-capable environment

## Installation

### 1. Install Dependencies

```bash
cd c:\Users\USER\GoCart
pip install -r requirements.txt
```

**Required packages**:
- fastapi >= 0.100.0
- uvicorn >= 0.23.0
- pydantic >= 2.0.0
- jwt >= 1.3.0
- bcrypt >= 4.0.0
- flet >= 0.10.0
- requests >= 2.31.0
- pytest >= 7.0.0 (for testing)

### 2. Create requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
PyJWT==2.8.1
bcrypt==4.1.1
flet==0.20.0
requests==2.31.0
pytest==7.4.3
python-multipart==0.0.6
starlette>=0.27.0
```

## Configuration

### 1. Update .env File

The `.env` file is already configured with default values. For production, update:

```bash
# Change the JWT secret key
JWT_SECRET_KEY=your-super-secret-key-generate-with-secrets-token

# Update CORS for production
ALLOWED_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
```

To generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Database Setup

The system uses SQLite by default. Tables are created automatically on first run.

For SQLite (default):
```bash
# No additional setup needed, database file will be created as gocart.db
```

For MySQL/PostgreSQL (production):
1. Update `services/auth_service.py` to use your database
2. Create database manually
3. Run schema scripts

## Running the System

### Option 1: Automatic (Flet with API Server)

```bash
python -m flet gocart_system.main
```

This will:
- Start the API server on port 8000 (background thread)
- Launch the Flet UI
- Display the login screen

### Option 2: Manual (Separate Services)

**Terminal 1 - Start API Server**:
```bash
python -c "from gocart_system.api import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000)"
```

**Terminal 2 - Launch Flet Client**:
```bash
python -m flet gocart_system.main
```

### Option 3: Development Server (with auto-reload)

```bash
python -c "import uvicorn; uvicorn.run('gocart_system.api:app', host='127.0.0.1', port=8000, reload=True)"
```

## First Time Use

### 1. Register a New Account

- Launch the application
- You'll see the login screen
- Click "Don't have an account? Register here"
- Fill in:
  - **Username**: 3-50 characters, alphanumeric with underscore/hyphen
  - **Email**: Valid email address
  - **Password**: Min 8 chars with uppercase, lowercase, digit, special char
  - Example password: `SecurePass123@`
- Click "REGISTER"

### 2. Login

- Enter username (or email)
- Enter password
- Click "LOGIN"
- You'll see the shopping system interface

### 3. Use the System

- **Shopping**: Browse products and add to cart
- **Cart**:  View and manage cart items
- **Orders**: View completed orders
- **Logout**: Click logout to return to login screen

## Testing the API

### Using Postman

1. Open Postman
2. Import `gocart_system/tests/GoCart_API.postman_collection.json`
3. Set variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (obtained after login)
   - `refresh_token`: (obtained after login)
4. Run requests in sequence

### Using curl

**Register**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123@"
  }'
```

**Login**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123@"
  }'
```

**Get Current User**:
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://127.0.0.1:8000/api/auth/login",
    json={"username": "testuser", "password": "SecurePass123@"}
)

tokens = response.json()["data"]
access_token = tokens["access_token"]

# Get current user
response = requests.get(
    "http://127.0.0.1:8000/api/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)

print(response.json())
```

## Running Tests

### Run All Tests

```bash
pytest gocart_system/tests/test_auth.py -v
```

### Run Specific Test

```bash
pytest gocart_system/tests/test_auth.py::TestAuthentication::test_01_register_valid_user -v
```

### Run with Coverage

```bash
pytest gocart_system/tests/test_auth.py --cov=gocart_system --cov-report=html
```

## Monitoring

### View Audit Logs

```bash
# Check SQLite database
sqlite3 gocart.db "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 20;"
```

### View Application Logs

```bash
# Check log files
tail -f logs/auth_events.log
```

## Common Issues

### 1. "Connection refused" on first login

**Solution**: Ensure the API server is running and listening on port 8000
```bash
# Check if port is open
netstat -an | grep 8000
```

### 2. Password doesn't meet requirements

**Requirements**:
- ✓ Minimum 8 characters
- ✓ One uppercase letter (A-Z)
- ✓ One lowercase letter (a-z)
- ✓ One digit (0-9)
- ✓ One special character (!@#$%^&*...)

**Example valid password**: `MyPassword123!`

### 3. Account locked after multiple failed logins

**Solution**: Wait 15 minutes (default lockout duration) or contact administrator

### 4. "Invalid token" error

**Solution**: Token may be expired. Login again to get a new token.

### 5. Port 8000 is already in use

**Solution**: Change port in `.env`
```bash
API_PORT=8001
```

## Development Tips

### To add a new protected endpoint:

```python
from fastapi import APIRouter, Depends
from .services.auth_middleware import verify_jwt_token

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(user: dict = Depends(verify_jwt_token)):
    return {"user": user}
```

### To require specific roles:

```python
from .services.auth_middleware import verify_rbac_role

@router.get("/admin-only")
async def admin_endpoint(admin: dict = Depends(verify_rbac_role("admin"))):
    return {"admin": admin}
```

### To access user info in views:

```python
class MyView:
    def __init__(self, auth_manager, **kwargs):
        self.auth_manager = auth_manager
        
    def build(self):
        username = self.auth_manager.user.get("username")
        role = self.auth_manager.user.get("role")
        # Use user info...
```

## Production Deployment

See `SECURITY_DOCUMENTATION.md` for:
- Security checklist
- Production configuration
- HTTPS setup
- Database migration
- Monitoring setup

## Need Help?

1. **Review Documentation**: Check `SECURITY_DOCUMENTATION.md`
2. **Check Logs**: Review `logs/auth_events.log`
3. **Run Tests**: Execute test suite to identify issues
4. **API Status**: Visit `http://127.0.0.1:8000/docs` for Swagger UI

## What's Next?

1. ✓ Set up and run the system
2. ✓ Test login/registration
3. ✓ Explore shopping features
4. ✓ Review security documentation
5. → Deploy to production with security checklist

Enjoy using GoCart Secure System! 🛒🔐
