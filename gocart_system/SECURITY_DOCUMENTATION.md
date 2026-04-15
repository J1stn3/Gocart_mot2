# GoCart Secure Authentication System - Documentation

## Overview

This is a comprehensive, production-ready authentication and authorization system for GoCart, featuring:

- **JWT-based Authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** for authorization
- **Secure Password Hashing** using bcrypt
- **Input Validation & Sanitization** to prevent injection attacks
- **Token Management** with expiration and refresh mechanisms
- **Account Lockout Protection** against brute-force attacks
- **Audit Logging** for security events
- **CORS Configuration** for controlled API access
- **Flet Frontend Integration** with secure token handling

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flet Frontend                             │
│  - Login/Registration UI                                    │
│  - Token Storage & Management                               │
│  - Header Injection (Authorization: Bearer)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
├─────────────────────────────────────────────────────────────┤
│ Authentication Controller                                   │
│  - /api/auth/register (POST)                                │
│  - /api/auth/login (POST)                                   │
│  - /api/auth/refresh (POST)                                 │
│  - /api/auth/logout (POST)                                  │
│  - /api/auth/me (GET)                                       │
│  - /api/auth/admin/users (GET)                              │
├─────────────────────────────────────────────────────────────┤
│ Middleware Layer                                            │
│  - JWT Bearer Token Validation                              │
│  - RBAC Role Verification                                   │
│  - CORS Handling                                            │
├─────────────────────────────────────────────────────────────┤
│ Service Layer                                               │
│  - Authentication Service                                   │
│  - JWT Service                                              │
│  - Security Service (Password, Input Validation)            │
│  - Auth Logger                                              │
├─────────────────────────────────────────────────────────────┤
│ Data Layer                                                  │
│  - SQLite Database (user, sessions, audit_logs)             │
└─────────────────────────────────────────────────────────────┘
```

## Security Features

### 1. Password Security
- **Hashing Algorithm**: bcrypt with 12 rounds
- **Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character (!@#$%^&*...)

### 2. JWT Token Management
- **Access Token**: 30-minute expiration
- **Refresh Token**: 7-day expiration
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Claims**:
  - `user_id`: Unique user identifier
  - `username`: User's username
  - `email`: User's email
  - `role`: User's role (admin, staff, user)
  - `token_type`: Token type (access or refresh)
  - `iat`: Issued at timestamp
  - `exp`: Expiration timestamp

### 3. Account Protection
- **Failed Login Tracking**: Maximum 5 failed attempts
- **Account Lockout**: 15-minute lockout after exceeded attempts
- **Attack Prevention**: Rate limiting through lockout mechanism

### 4. Role-Based Access Control (RBAC)
```
Role Hierarchy:
├── admin (full access)
├── staff (limited access)
└── user (basic access)
```

### 5. Input Validation
- Username: 3-50 characters, alphanumeric with underscore/hyphen
- Email: RFC-compliant validation
- Password: Length and character composition checks
- All inputs sanitized to prevent injection attacks

### 6. Audit Logging
Tracks all security events:
- User registration attempts
- Login attempts (success/failure)
- Token refresh operations
- Unauthorized access attempts
- Account lockouts
- Logout events
   
## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME,
    last_login DATETIME,
    failed_login_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_until DATETIME
)
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    session_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    refresh_token TEXT UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME,
    is_valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY,
    event_type VARCHAR(50),
    user_id INTEGER,
    username VARCHAR(50),
    action VARCHAR(100),
    status VARCHAR(20),
    ip_address VARCHAR(45),
    timestamp DATETIME,
    details TEXT
)
```

## Environment Configuration

`.env` file settings:
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-long!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=development

# Security
PASSWORD_MIN_LENGTH=8
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# CORS
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Important: Production Setup

For production deployment:

1. **Change JWT_SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update ALLOWED_ORIGINS** to your production domain:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ENVIRONMENT=production
   ```

3. **Use HTTPS**: Ensure all traffic is encrypted

4. **Secure Database**: Use PostgreSQL or MySQL in production instead of SQLite

## API Endpoints

### Authentication Endpoints

#### 1. Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123@"
}

Response (201):
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "role": "user"
  }
}
```

#### 2. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123@"
}

Response (200):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### 3. Refresh Access Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### 4. Get Current User
```http
GET /api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response (200):
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-04-14T10:30:00",
    "last_login": "2024-04-14T11:00:00"
  }
}
```

#### 5. Logout
```http
POST /api/auth/logout
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
  "success": true,
  "message": "Logout successful"
}
```

#### 6. Get All Users (Admin Only)
```http
GET /api/auth/admin/users
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc... (admin token)

Response (200):
{
  "success": true,
  "data": [
    {
      "user_id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      ...
    }
  ]
}

Error (403):
{
  "detail": "Insufficient permissions. Required roles: ['admin']"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Username or email already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid username or password"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions. Required roles: ['admin']"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error fetching users"
}
```

## Using Protected Endpoints

All protected endpoints require the Authorization header with Bearer token:

```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    "http://127.0.0.1:8000/api/auth/me",
    headers=headers
)
```

## Testing

### Run Integration Tests
```bash
cd gocart_system/tests
pytest test_auth.py -v
```

### Use Postman Collection
1. Import `GoCart_API.postman_collection.json` in Postman
2. Set the `base_url` variable to `http://127.0.0.1:8000`
3. Run tests in sequence

### Manual Testing with curl

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123@"}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123@"}'

# Get Current User
curl -X GET http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Security Best Practices

1. **Secret Key Management**:
   - Use a strong, randomly generated secret key
   - Store in environment variables, never in code
   - Rotate periodically in production

2. **HTTPS in Production**:
   - Always use HTTPS for authentication endpoints
   - Enforce HSTS (HTTP Strict-Transport-Security)

3. **Token Storage (Frontend)**:
   - Store access token in memory (most secure)
   - Store refresh token in secure/httpOnly cookie
   - Never store in localStorage (vulnerable to XSS)

4. **Token Expiration**:
   - Keep access token expiration short (30 min)
   - Use refresh tokens for longer sessions (7 days)

5. **Rate Limiting**:
   - Implement rate limiting on login endpoint
   - Use account lockout mechanism (implemented)

6. **Audit Logging**:
   - Monitor all authentication events
   - Review audit logs regularly
   - Set up alerts for suspicious activity

7. **Database Security**:
   - Use parameterized queries (implemented)
   - Encrypt sensitive data at rest
   - Regular backups

8. **Input Validation**:
   - Validate all user inputs
   - Sanitize before processing
   - Reject suspicious patterns

## Deployment Checklist

- [ ] Update `.env` with secure secret key
- [ ] Change `ALLOWED_ORIGINS` to production domain
- [ ] Set `ENVIRONMENT=production`
- [ ] Use HTTPS instead of HTTP
- [ ] Set up database backups
- [ ] Configure email notifications for security events
- [ ] Enable audit log monitoring
- [ ] Test all endpoints with Postman
- [ ] Run integration tests
- [ ] Set up health check endpoint
- [ ] Configure logging aggregation (e.g., ELK stack)
- [ ] Implement rate limiting proxy (e.g., nginx)

## Troubleshooting

### "Connection refused"
- Ensure API server is running: `python -m gocart_system.api`
- Check if port 8000 is available

### "Invalid token"
- Token may be expired, use refresh endpoint
- Ensure token is passed correctly in Authorization header

### "Account locked"
- Wait 15 minutes (default lockout duration)
- Or contact administrator

### "Insufficient permissions"
- Your user role doesn't have access to this endpoint
- Contact administrator to upgrade permissions

## Support & Contact

For issues or questions:
1. Check documentation files
2. Review audit logs for clues
3. Run integration tests to identify failures
4. Contact development team with error logs

## Version History

- **v1.0.0** (April 14, 2024): Initial release with complete authentication system
