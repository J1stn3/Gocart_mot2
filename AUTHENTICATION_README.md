# GoCart Secure Authentication System

A production-ready, comprehensive authentication and authorization system for GoCart e-commerce platform with Flet frontend and FastAPI backend.

## 🔐 Features

### Authentication
- ✅ User registration with email validation
- ✅ Secure login with JWT tokens
- ✅ Refresh token mechanism for session extension
- ✅ Logout with token invalidation
- ✅ Account lockout after failed attempts
- ✅ Automatic session management

### Security
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ Strong password validation requirements
- ✅ Input sanitization and validation
- ✅ JWT token verification and expiration
- ✅ CORS configuration for controlled access
- ✅ SQL injection prevention via parameterized queries
- ✅ XSS protection via input validation

### Authorization
- ✅ Role-Based Access Control (RBAC)
- ✅ Three-tier role system: admin, staff, user
- ✅ Endpoint-level permission enforcement
- ✅ User role hierarchy

### Monitoring & Logging
- ✅ Comprehensive audit logging
- ✅ Security event tracking
- ✅ Failed login attempt logging
- ✅ Account lockout monitoring
- ✅ Unauthorized access tracking
- ✅ Token refresh logging

### User Interface
- ✅ Modern Flet-based login/registration UI
- ✅ Secure token storage
- ✅ Automatic token refresh
- ✅ User profile display
- ✅ Role-based UI controls

## 📋 Project Structure

```
gocart_system/
├── models/
│   ├── user.py                    # User model with roles
│   ├── cart.py                    # Cart model
│   ├── product.py                 # Product model
│   └── cart_item.py               # Cart item model
├── services/
│   ├── auth_service.py            # Authentication business logic
│   ├── jwt_service.py             # JWT token management
│   ├── security_service.py        # Password hashing & validation
│   ├── auth_middleware.py         # JWT validation & RBAC
│   ├── auth_logger.py             # Audit logging
│   ├── cart_on_services.py        # Cart operations
│   ├── product_services.py        # Product operations
│   └── database_connection.py     # Database utilities
├── controllers/
│   ├── auth_controller.py         # Authentication endpoints
│   ├── cart_controller.py         # Cart controller
│   └── product_controller.py      # Product controller
├── requests/
│   ├── auth_requests.py           # Auth request/response models
│   ├── base_request.py            # Base request model
│   ├── cart_requests.py           # Cart request models
│   └── product_requests.py        # Product request models
├── views/
│   ├── auth_view.py               # Login/registration UI
│   ├── main_view.py               # Main shopping view
│   ├── shopping_view.py           # Shopping view
│   ├── cart_view.py               # Cart view
│   └── orders_view.py             # Orders view
├── tests/
│   ├── test_auth.py               # Integration tests
│   └── GoCart_API.postman_collection.json
├── api.py                         # FastAPI application
├── main.py                        # Application entry point
├── AUTHENTICATION_FLOW.md         # Authentication flow diagrams
├── SECURITY_DOCUMENTATION.md      # Security implementation details
└── __init__.py

.env                               # Environment configuration
requirements.txt                   # Python dependencies
QUICKSTART.md                      # Quick start guide
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Update `.env` with your settings (or use defaults for development):
```bash
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Run the System
```bash
python -m flet gocart_system.main
```

The system will:
- Start the API server on `http://127.0.0.1:8000`
- Launch the Flet UI with login screen
- Show shopping interface after successful authentication

## 📚 Documentation

### For Users
- **[QUICKSTART.md](QUICKSTART.md)** - Installation and basic usage
- **[Login/Registration Guide](#login--registration)** below

### For Developers
- **[AUTHENTICATION_FLOW.md](gocart_system/AUTHENTICATION_FLOW.md)** - Detailed security flows
- **[SECURITY_DOCUMENTATION.md](gocart_system/SECURITY_DOCUMENTATION.md)** - Security implementation
- **[API Endpoints](#api-endpoints)** below

### For Testers
- **[Integration Tests](#running-tests)** - Automated test suite
- **[Postman Collection](#postman)** - API testing collection

## 🔑 Authentication Endpoints

### Register a New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123@"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123@"
}

Response:
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "{refresh_token}"
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "refresh_token": "{refresh_token}"
}
```

## 🔐 Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*...)

### JWT Tokens
- **Access Token**: 30-minute expiration
- **Refresh Token**: 7-day expiration
- **Algorithm**: HS256 (HMAC-SHA256)

### Account Protection
- Maximum 5 failed login attempts
- 15-minute account lockout after max attempts
- Automatic unlock after lockout duration

### Role-Based Access
```
admin  → Full system access
staff  → Limited administrative access
user   → Regular user access
```

## 🧪 Running Tests

### Run All Tests
```bash
cd gocart_system/tests
pytest test_auth.py -v
```

### Run with Coverage
```bash
pytest test_auth.py --cov=gocart_system --cov-report=html
```

### Manual Testing with Postman
1. Import `GoCart_API.postman_collection.json`
2. Set the `base_url` variable to `http://127.0.0.1:8000`
3. Run the requests in sequence

### Manual Testing with curl
```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"testuser",
    "email":"test@example.com",
    "password":"SecurePass123@"
  }'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123@"}'
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flet Frontend                             │
│  - Login/Registration UI                                        │
│  - Token Management                                             │
│  - User Authentication                                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/HTTPS Requests
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
├─────────────────────────────────────────────────────────────────┤
│ Authentication Layer                                            │
│  - JWT Token Validation                                         │
│  - RBAC Authorization                                           │
│  - CORS Configuration                                           │
├─────────────────────────────────────────────────────────────────┤
│ API Routes                                                      │
│  - Auth endpoints (/api/auth/*)                                 │
│  - Product endpoints (/api/products)                            │
│  - Cart endpoints (/api/cart/*)                                 │
├─────────────────────────────────────────────────────────────────┤
│ Service Layer                                                   │
│  - AuthenticationService                                        │
│  - JWTService                                                   │
│  - SecurityService                                              │
│  - Business Logic Services                                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────────┐
           │   SQLite Database        │
           │                          │
           │  - users table           │
           │  - user_sessions table   │
           │  - audit_logs table      │
           │  - products table        │
           │  - cart tables           │
           └──────────────────────────┘
```

## 🛡️ Security Best Practices Implemented

1. **Password Security**
   - Bcrypt hashing with 12 rounds
   - Strong password validation
   - No plaintext password storage

2. **Token Security**
   - JWT with HMAC-SHA256
   - Configurable expiration times
   - Secure refresh token rotation
   - Token verification on every request

3. **Access Control**
   - Role-Based Access Control (RBAC)
   - Endpoint-level authorization
   - User context injection
   - Permission verification

4. **Input Protection**
   - Input validation and sanitization
   - Length and format checks
   - SQL injection prevention
   - XSS protection

5. **Session Management**
   - Stateless token-based auth
   - Refresh token invalidation
   - Logout mechanism
   - Session timeout

6. **Audit & Monitoring**
   - Comprehensive logging
   - Security event tracking
   - Failed attempt logging
   - Unauthorized access monitoring

7. **Network Security**
   - CORS configuration
   - HTTPS support ready
   - Secure headers
   - TrustedHost middleware

8. **Account Protection**
   - Account lockout mechanism
   - Failed attempt tracking
   - Configurable lockout duration
   - Automatic unlock

## 🔧 Configuration

### Environment Variables (.env)

```bash
# JWT Settings
JWT_SECRET_KEY=your-super-secret-key-min-32-chars!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=development

# Security Settings
PASSWORD_MIN_LENGTH=8
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Database
DB_CONNECTION=sqlite
DB_PATH=gocart.db
```

### Production Checklist

- [ ] Generate secure JWT_SECRET_KEY
- [ ] Update ALLOWED_ORIGINS for your domain
- [ ] Set ENVIRONMENT=production
- [ ] Enable HTTPS
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable HSTS headers
- [ ] Set up monitoring and alerts
- [ ] Review audit logs regularly

## 🐛 Troubleshooting

### "Connection refused"
**Problem**: API server not running or port in use
**Solution**: 
```bash
# Check if port 8000 is available
netstat -an | grep 8000
# Use different port if needed
API_PORT=8001
```

### "Invalid password" during login
**Problem**: Weak password during registration
**Solution**: Use password with 8+ chars, uppercase, lowercase, digit, special char

### "Account locked"
**Problem**: Too many failed login attempts
**Solution**: Wait 15 minutes (default lockout) or contact admin

### "Token expired"
**Problem**: Access token is no longer valid
**Solution**: Use refresh token to get new access token

### Tests failing on first run
**Problem**: Database needs initialization
**Solution**: Tables are created automatically; ensure gocart.db is writable

## 📈 Deployment

### Local Development
```bash
python -m flet gocart_system.main
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn gocart_system.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Support (Create Dockerfile)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV ENVIRONMENT=production
CMD ["python", "-m", "uvicorn", "gocart_system.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 API Response Examples

### Successful Authentication
```json
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

### Authentication Error (401)
```json
{
  "detail": "Invalid username or password"
}
```

### Authorization Error (403)
```json
{
  "detail": "Insufficient permissions. Required roles: ['admin']"
}
```

### Validation Error (400)
```json
{
  "detail": "Password must contain at least one special character"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new features
5. Run test suite
6. Submit pull request

## 📄 License

This project is confidential and proprietary. All rights reserved.

## 🆘 Support

For issues or questions:
1. Check [SECURITY_DOCUMENTATION.md](gocart_system/SECURITY_DOCUMENTATION.md)
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Run the integration test suite
4. Check audit logs in `logs/auth_events.log`
5. Contact the development team

## ✨ Key Components

### Authentication Service (`auth_service.py`)
- User registration with validation
- Secure login with JWT generation
- Token refresh mechanism
- Account lockout protection
- User data retrieval

### JWT Service (`jwt_service.py`)
- Token creation (access & refresh)
- Token verification and decoding
- Signature validation
- Expiration checking
- Secure key management

### Security Service (`security_service.py`)
- Password hashing with bcrypt
- Password validation rules
- Input validation and sanitization
- Attack prevention utilities

### Auth Middleware (`auth_middleware.py`)
- JWT token extraction
- Bearer scheme validation
- Token expiration checking
- RBAC role verification
- User context injection

### Auth Logger (`auth_logger.py`)
- Login attempt tracking
- Registration monitoring
- Token refresh logging
- Unauthorized access tracking
- Account lockout events

## 🎯 Next Steps

1. ✅ Set up the system
2. ✅ Register and login
3. ✅ Test all endpoints
4. ✅ Review security documentation
5. → Connect additional services
6. → Extend with business logic
7. → Deploy to production

---

**Last Updated**: April 14, 2026
**Version**: 1.0.0
**Status**: Production Ready 🚀
