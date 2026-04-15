# GoCart Authentication Flow & Architecture

## Complete Authentication Sequence Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         REGISTRATION FLOW                                 │
└──────────────────────────────────────────────────────────────────────────┘

User (Flet)                              API Server                    Database
    │                                        │                             │
    │ 1. POST /api/auth/register           │                             │
    │    {username, email, password}        │                             │
    ├───────────────────────────────────────>                             │
    │                                        │ 2. Validate inputs         │
    │                                        │    - Check format          │
    │                                        │    - Verify no duplicates  │
    │                                        ├────────────────────────────>
    │                                        │                   SELECT * │
    │                                        │<────────────────────────────
    │                                        │                             │
    │                                        │ 3. Hash password (bcrypt)  │
    │                                        │    rounds=12               │
    │                                        │                             │
    │                                        │ 4. INSERT user             │
    │                                        │    with hashed password    │
    │                                        ├────────────────────────────>
    │                                        │             INSERT user_id │
    │                                        │<────────────────────────────
    │                                        │                             │
    │ 5. 201 Created                         │                             │
    │    {user_id, username, email, role}   │                             │
    │<───────────────────────────────────────┤                             │
    │                                        │                             │


┌──────────────────────────────────────────────────────────────────────────┐
│                            LOGIN FLOW                                     │
└──────────────────────────────────────────────────────────────────────────┘

User Input                   API Server                        Database
    │                            │                                 │
    │1. POST /api/auth/login    │                                 │
    │   {username, password}     │                                 │
    │───────────────────────────>│                                 │
    │                            │2. SELECT user                  │
    │                            │   WHERE username=? OR email=?  │
    │                            │─────────────────────────────────>
    │                            │              {user_data}        │
    │                            │<─────────────────────────────────
    │                            │                                 │
    │                            │3. bcrypt.verify(password)      │
    │                            │   ✓ Match                       │
    │                            │                                 │
    │                            │4. Generate Tokens              │
    │                            │   - JWT access token (30 min)   │
    │                            │   - JWT refresh token (7 days)  │
    │                            │                                 │
    │                            │5. INSERT session record        │
    │                            │   (refresh_token, user_id)     │
    │                            │─────────────────────────────────>
    │                            │                        {OK}     │
    │                            │<─────────────────────────────────
    │                            │                                 │
    │                            │6. UPDATE last_login           │
    │                            │   Reset failed_attempts        │
    │                            │─────────────────────────────────>
    │                            │<─────────────────────────────────
    │                            │                                 │
    │200 OK                      │                                 │
    │{access_token,              │                                 │
    │ refresh_token,             │                                 │
    │ expires_in: 1800}          │                                 │
    │<───────────────────────────┤                                 │
    │                            │                                 │


┌──────────────────────────────────────────────────────────────────────────┐
│                    PROTECTED API CALL FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

Flet Client                Middleware              Service Layer          DB
    │                          │                       │                  │
    │1. GET /api/auth/me      │                       │                  │
    │   Authorization: Bearer  │                       │                  │
    │   {access_token}         │                       │                  │
    ├─────────────────────────>│                       │                  │
    │                          │2. Extract token      │                  │
    │                          │   from header        │                  │
    │                          │                       │                  │
    │                          │3. JWT decode & verify│                  │
    │                          │   - Signature check  │                  │
    │                          │   - Expiration check │                  │
    │                          │   - Payload extract  │                  │
    │                          │                       │                  │
    │                          │4. Pass user info     │                  │
    │                          │   to endpoint        │                  │
    │                          ├──────────────────────>                  │
    │                          │                       │5. Query user    │
    │                          │                       │   by user_id    │
    │                          │                       ├─────────────────>
    │                          │                       │        {data}   │
    │                          │                       │<─────────────────
    │                          │                       │                  │
    │200 OK                    │                       │                  │
    │{user_id, username,       │                       │                  │
    │ email, role, ...}        │                       │                  │
    │<─────────────────────────┤                       │                  │
    │                          │                       │                  │


┌──────────────────────────────────────────────────────────────────────────┐
│                      TOKEN REFRESH FLOW                                   │
└──────────────────────────────────────────────────────────────────────────┘

Flet Client              API Server                      Database
    │                        │                               │
    │1. POST /api/auth/    │                               │
    │   refresh             │                               │
    │   {refresh_token}     │                               │
    ├───────────────────────>                               │
    │                        │2. Decode refresh_token      │
    │                        │   JWT decode & verify      │
    │                        │                               │
    │                        │3. SELECT from sessions     │
    │                        │   WHERE token = ?          │
    │                        │   AND expires_at > NOW()   │
    │                        ├──────────────────────────────>
    │                        │                   {session}  │
    │                        │<──────────────────────────────
    │                        │                               │
    │                        │4. Generate new access token │
    │                        │   (same user, 30 min exp)   │
    │                        │                               │
    │200 OK                  │                               │
    │{access_token,          │                               │
    │ expires_in: 1800}      │                               │
    │<───────────────────────┤                               │
    │                        │                               │


┌──────────────────────────────────────────────────────────────────────────┐
│                    FAILED LOGIN PROTECTION                                │
└──────────────────────────────────────────────────────────────────────────┘

Login Attempt 1           Login Attempt 2-4        Login Attempt 5
(Invalid Password)        (Invalid Passwords)      (Max Attempts)
    │                            │                        │
    ├──────────────────┐        │                         │
    │Increment         │        ├──────────────┐          │
    │failures = 1      │        │failed = 4    │          │
    │                  │        │              │          │
    └──────────────────┤        └──────────────┤          │
                       │                       │          │
                       V                       V          V
                    UPDATE users          UPDATE users
                    failed_login_attempts = 5
                    is_locked = TRUE
                    locked_until = NOW() + 15min

                       ↓

            SUBSEQUENT ATTEMPTS BLOCKED
            Error: "Account locked due to too many
                    login attempts. Try again in 15 min"

                       ↓ (After 15 minutes)

            is_locked = FALSE
            failed_login_attempts = 0
            Account Unlocked ✓


┌──────────────────────────────────────────────────────────────────────────┐
│                   ROLE-BASED ACCESS CONTROL (RBAC)                        │
└──────────────────────────────────────────────────────────────────────────┘

Endpoint Request (Admin Only)
    │
    ├─> Verify JWT Token
    │   ├─ Valid? → Continue
    │   └─ Invalid? → 401 Unauthorized
    │
    ├─> Extract Role from Token
    │   (decoded_token["role"])
    │
    ├─> Check Role Permission
    │   ├─ Role == "admin"? → 200 OK
    │   ├─ Role == "staff"? → 403 Forbidden
    │   └─ Role == "user"?  → 403 Forbidden
    │
    └─> Return Response


ROLE HIERARCHY:
    admin  ──> Can access: admin, staff, user endpoints
    staff  ──> Can access: staff, user endpoints
    user   ──> Can access: user endpoints only


┌──────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                                  │
└──────────────────────────────────────────────────────────────────────────┘

Layer 1: CORS Middleware
    ↓ Validates request origin
    ├─> Allowed origin? → Pass
    └─> Not allowed? → 403 Forbidden

Layer 2: Authentication Middleware
    ↓ Verifies JWT token in Authorization header
    ├─> Valid token? → Extract user info
    └─> Invalid? → 401 Unauthorized

Layer 3: RBAC Authorization
    ↓ Checks user role against requirements
    ├─> Required role? → Process request
    └─> Insufficient permission? → 403 Forbidden

Layer 4: Input Validation
    ↓ Sanitizes and validates request data
    ├─> Valid input? → Process
    └─> Invalid? → 400 Bad Request

Layer 5: Business Logic
    ↓ Processes validated request
    ├─> Operation succeeds → 200 OK
    └─> Operation fails → 500 Internal Error


┌──────────────────────────────────────────────────────────────────────────┐
│                       TOKEN STRUCTURE (JWT)                               │
└──────────────────────────────────────────────────────────────────────────┘

JWT Format: HEADER.PAYLOAD.SIGNATURE

HEADER:
{
  "alg": "HS256",           ← Signing algorithm
  "typ": "JWT"              ← Token type
}

PAYLOAD:
{
  "user_id": 1,             ← User identifier
  "username": "john",       ← Username
  "email": "john@ex.com",   ← Email
  "role": "user",           ← User role
  "token_type": "access",   ← Token purpose
  "iat": 1713079200,        ← Issued at (unix timestamp)
  "exp": 1713080100         ← Expires at (unix timestamp)
}

SIGNATURE:
  HMACSHA256(
    base64UrlEncode(header) +
    "." +
    base64UrlEncode(payload),
    secret_key
  )


┌──────────────────────────────────────────────────────────────────────────┐
│                      AUDIT LOGGING                                        │
└──────────────────────────────────────────────────────────────────────────┘

All events logged to audit_logs table:

Login Success:
    event_type: "LOGIN"
    status: "SUCCESS"
    username: "john"
    timestamp: "2024-04-14 11:00:00"
    ip_address: "192.168.1.100"

Failed Login:
    event_type: "LOGIN"
    status: "FAILED"
    username: "john"
    timestamp: "2024-04-14 11:01:00"
    details: "Invalid password (attempt 1/5)"

Account Lockout:
    event_type: "ACCOUNT_LOCKED"
    status: "LOCKED"
    username: "john"
    timestamp: "2024-04-14 11:05:00"

Token Refresh:
    event_type: "TOKEN_REFRESH"
    status: "SUCCESS"
    user_id: 1
    timestamp: "2024-04-14 11:10:00"

Unauthorized Access:
    event_type: "UNAUTHORIZED_ACCESS"
    status: "DENIED"
    action: "POST /api/admin/users"
    timestamp: "2024-04-14 11:15:00"
    details: "Insufficient permissions. Required: admin"


┌──────────────────────────────────────────────────────────────────────────┐
│                      PASSWORD HASHING FLOW                                │
└──────────────────────────────────────────────────────────────────────────┘

User Input Password
        │
        ▼
    Validation
    ✓ Length >= 8
    ✓ Uppercase letter
    ✓ Lowercase letter
    ✓ Digit
    ✓ Special character
        │
        ├─ Valid? → Continue
        └─ Invalid? → Error message
        │
        ▼
    Hashing with bcrypt
    ├─ Generate salt (rounds=12)
    ├─ Apply bcrypt algorithm
    └─ Generate hash
        (e.g., $2b$12$abcd1234...)
        │
        ▼
    Store in Database
    (never store plain password)
        │
        ▼
    On Login:
    1. Fetch stored hash from DB
    2. Apply bcrypt verify with input
    3. Compare result
       ├─ Match? → Login success
       └─ No match? → Login failed
```

## Data Flow Summary

### Frontend to Backend (With Security)
1. User enters credentials in Flet UI
2. Credentials sent to API via HTTPS (production)
3. API validates and processes request
4. If successful: Returns tokens
5. Flet stores access token in memory
6. Flet stores refresh token in secure storage
7. All subsequent requests include Authorization header

### Protected Resource Access
1. Flet sends request with Authorization header
2. API middleware extracts and verifies JWT
3. Token valid? Extract user info
4. Check RBAC permissions
5. Process request if authorized
6. Return response

### Token Expiration Handling
1. Access token expires after 30 minutes
2. Flet receives 401 Unauthorized
3. Flet uses refresh token to get new access token
4. Refresh endpoint validates refresh token
5. Returns new access token (30 min expiration)
6. Retry original request with new token

## Architecture Summary

This implementation provides:
- ✓ **Authentication**: Username/password with JWT tokens
- ✓ **Authorization**: Role-based access control
- ✓ **Security**: Password hashing, input validation, token verification
- ✓ **Performance**: Token-based (no session state needed)
- ✓ **Scalability**: Stateless design allows horizontal scaling
- ✓ **Monitoring**: Comprehensive audit logging
- ✓ **Protection**: Account lockout, rate limiting, CORS
- ✓ **User Management**: Registration, login, profile access
- ✓ **Token Management**: Access tokens, refresh tokens, expiration

The system is production-ready with proper separation of concerns and security best practices.
