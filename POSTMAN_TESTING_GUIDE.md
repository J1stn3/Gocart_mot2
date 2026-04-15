# GoCart API - Postman Testing Guide

## Step 1: Download & Import Postman Collection

### Option A: Import from File
1. Open **Postman** (download from [postman.com](https://www.postman.com/downloads/) if needed)
2. Click **Import** → **File**
3. Navigate to: `C:\Users\USER\GoCart\gocart_system\tests\GoCart_API.postman_collection.json`
4. Click **Import**

### Option B: Manual Setup
If import fails, manually create requests as shown below.

---

## Step 2: Set Up Environment Variables

1. Click **Environments** (left sidebar)
2. Click **Create New** (+ button)
3. Name it: `GoCart Local`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://127.0.0.1:8001` | `http://127.0.0.1:8001` |
| `access_token` | *(leave empty)* | *(will be filled after login)* |
| `refresh_token` | *(leave empty)* | *(will be filled after login)* |

5. Click **Save**
6. Select the `GoCart Local` environment from dropdown (top right)

---

## Step 3: Get Access Token (Login Flow)

### 1️⃣ **Register a New User** (if needed)

**Method:** `POST`  
**URL:** `http://127.0.0.1:8001/api/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body (Raw JSON):**
```json
{
  "username": "testuser123",
  "email": "test@example.com",
  "password": "TestPass123@"
}
```

**Response:** `201 Created`
```json
{
  "user_id": 1,
  "username": "testuser123",
  "email": "test@example.com",
  "role": "user",
  "is_active": true,
  "message": "User registered successfully"
}
```

---

### 2️⃣ **Login to Get Tokens**

**Method:** `POST`  
**URL:** `http://127.0.0.1:8001/api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (Raw JSON):**
```json
{
  "username": "jus@gmail.com",
  "password": "PassWord123@"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxMzE4OTQwMn0.xxxxxxxxxxxx",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNzEzNzk0MjAyfQ.xxxxxxxxxxxx",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": 1,
    "username": "jus@gmail.com",
    "email": "jus@gmail.com",
    "role": "user"
  }
}
```

---

### 3️⃣ **Save Tokens to Environment**

After successful login:

1. Copy the `access_token` value
2. Go to **Environments** → Select `GoCart Local`
3. Paste into `access_token` Current Value
4. Copy the `refresh_token` value
5. Paste into `refresh_token` Current Value
6. Click **Save**

**OR**, use Postman's automatic token capture:

In the **Tests** tab of Login request, add:
```javascript
if (pm.response.code === 200) {
    pm.environment.set("access_token", pm.response.json().access_token);
    pm.environment.set("refresh_token", pm.response.json().refresh_token);
}
```

---

## Step 4: Use Authorization Header in Requests

### ✅ Template for Protected Endpoints

**Method:** `GET`  
**URL:** `http://127.0.0.1:8001/api/auth/me`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

**Key Point:** Replace `{{access_token}}` with your variable name. Postman will automatically substitute it.

---

## Step 5: API Endpoints to Test

### Authentication Endpoints

#### 1. Register User
```
POST /api/auth/register
Body: {
  "username": "newuser",
  "email": "new@example.com",
  "password": "SecurePass123@"
}
```

#### 2. Login
```
POST /api/auth/login
Body: {
  "username": "jus@gmail.com",
  "password": "PassWord123@"
}
Response → Copy tokens
```

#### 3. Get Current User (Protected)
```
GET /api/auth/me
Header: Authorization: Bearer {{access_token}}
```

#### 4. Refresh Token
```
POST /api/auth/refresh
Body: {
  "refresh_token": "{{refresh_token}}"
}
Response → Updates {{access_token}}
```

#### 5. Logout
```
POST /api/auth/logout
Header: Authorization: Bearer {{access_token}}
```

#### 6. Get All Users (Admin Only)
```
GET /api/auth/admin/users
Header: Authorization: Bearer {{access_token}}
```
*Only works if your user has "admin" role*

---

### Shopping/Cart Endpoints

#### 1. Get All Products
```
GET /api/products
Header: Authorization: Bearer {{access_token}}
```

#### 2. Add Product to Cart (Admin Only)
```
POST /api/products
Header: Authorization: Bearer {{access_token}}
Body: {
  "name": "Laptop",
  "price": 999.99,
  "quantity": 5
}
```

#### 3. Get Cart Items
```
GET /api/cart
Header: Authorization: Bearer {{access_token}}
```

#### 4. Add Item to Cart
```
POST /api/cart/add
Header: Authorization: Bearer {{access_token}}
Body: {
  "product_name": "nayskabert",
  "quantity": 2
}
```

#### 5. Remove from Cart
```
DELETE /api/cart/remove
Header: Authorization: Bearer {{access_token}}
Body: {
  "product_name": "nayskabert"
}
```

#### 6. Complete Order
```
POST /api/cart/complete
Header: Authorization: Bearer {{access_token}}
```

#### 7. View Orders
```
GET /api/orders
Header: Authorization: Bearer {{access_token}}
```

#### 8. Clear Orders
```
DELETE /api/orders
Header: Authorization: Bearer {{access_token}}
```

---

## Step 6: Test Different HTTP Methods

### GET (Retrieve Data)
```
GET /api/auth/me
Authorization: Bearer {{access_token}}
Response: 200 OK with user data
```

### POST (Create Data)
```
POST /api/auth/login
Body: {"username": "user", "password": "pass"}
Response: 200 OK with tokens
```

### PUT (Update Entire Resource)
```
PUT /api/products/1
Authorization: Bearer {{access_token}}
Body: {
  "name": "Updated Name",
  "price": 599.99,
  "quantity": 10
}
```

### PATCH (Partial Update)
```
PATCH /api/products/1
Authorization: Bearer {{access_token}}
Body: {
  "price": 699.99
}
```

### DELETE (Remove Data)
```
DELETE /api/cart/remove
Authorization: Bearer {{access_token}}
Body: {
  "product_name": "nayskabert"
}
```

---

## Step 7: Common Issues & Solutions

### ❌ Error: `401 Unauthorized`
**Cause:** Invalid or missing token
**Solution:** 
- Re-login to get new token
- Copy token to environment variable
- Check Authorization header format: `Bearer <token>`

### ❌ Error: `403 Forbidden`
**Cause:** Insufficient permissions (need admin role)
**Solution:**
- Contact admin to upgrade your role
- Or test with admin account

### ❌ Error: `400 Bad Request`
**Cause:** Invalid request body
**Solution:**
- Check JSON syntax (use Postman's formatter)
- Verify all required fields are present
- Match expected data types

### ❌ Error: `422 Unprocessable Entity`
**Cause:** Validation failed (weak password, duplicate user, etc.)
**Solution:**
- Use strong password: Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
- Example: `TestPass123@`

---

## Step 8: Token Refresh Flow

### When Token Expires

1. Access token valid for **30 minutes**
2. Refresh token valid for **7 days**
3. When access token expires (401 error), call refresh:

```
POST /api/auth/refresh
Body: {
  "refresh_token": "{{refresh_token}}"
}
```

4. Get new access token from response
5. Update environment variable
6. Continue using API

---

## Quick Summary

| Task | Method | URL | Auth Required |
|------|--------|-----|---|
| Register | POST | `/api/auth/register` | ❌ No |
| Login | POST | `/api/auth/login` | ❌ No |
| Get User | GET | `/api/auth/me` | ✅ Yes |
| Logout | POST | `/api/auth/logout` | ✅ Yes |
| Get Products | GET | `/api/products` | ✅ Yes |
| Add to Cart | POST | `/api/cart/add` | ✅ Yes |
| Checkout | POST | `/api/cart/complete` | ✅ Yes |
| View Orders | GET | `/api/orders` | ✅ Yes |

---

## Test Credentials

**Regular User:**
- Username: `jus@gmail.com`
- Password: `PassWord123@`

**To Get Admin Token:**
- Contact system admin or create new admin account with proper role assignment

---

## Pro Tips

1. **Use Postman Collections** - Save time by grouping related requests
2. **Environment Variables** - Keep `{{base_url}}` and `{{access_token}}` dynamic
3. **Pre-request Scripts** - Automatically refresh tokens before requests
4. **Tests Tab** - Auto-save responses to variables
5. **Documentation** - Right-click request → Describe to add notes

Enjoy testing! 🚀
