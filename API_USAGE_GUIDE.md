# GoCart API Usage Guide - PUT Requests & Authentication

## Server Status
✅ **The API server is now running on http://127.0.0.1:8001**

## Authentication Flow

All PUT, PATCH, DELETE, and POST requests (except `/api/auth/register` and `/api/auth/login`) require **JWT token authentication**.

### Step 1: Register a User
**POST** `http://127.0.0.1:8001/api/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### Step 2: Login to Get Access Token
**POST** `http://127.0.0.1:8001/api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Step 3: Use Token for Protected Requests

**IMPORTANT**: Copy the `access_token` from the login response and use it in all subsequent requests.

#### Example: Update SMS Status (PUT Request)

**PUT** `http://127.0.0.1:8001/api/sms/1`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

Replace `<YOUR_ACCESS_TOKEN>` with the actual token from Step 2.

**Body:**
```json
{
  "status": "SENT"
}
```

**Response:**
```json
{
  "message": "SMS status updated",
  "sms": {
    "id": 1,
    "status": "SENT"
  }
}
```

## Available Protected Endpoints

### Products
- **GET** `/api/products` - Get all products
- **POST** `/api/products` - Create product
- **PUT** `/api/products/{product_id}` - Update product
- **PATCH** `/api/products/{product_id}` - Partially update product
- **DELETE** `/api/products/{product_id}` - Delete product

### Cart
- **GET** `/api/cart` - Get cart items
- **POST** `/api/cart/add` - Add to cart
- **DELETE** `/api/cart/{product_id}` - Remove from cart
- **POST** `/api/cart/clear` - Clear cart
- **POST** `/api/cart/complete` - Complete order

### SMS
- **GET** `/api/sms` - Get your SMS messages
- **GET** `/api/sms/list` - Get all SMS messages (admin only)
- **GET** `/api/sms/{sms_id}` - Get specific SMS
- **PUT** `/api/sms/{sms_id}` - Update SMS status
- **POST** `/api/sms/{sms_id}/job` - Create async job to update SMS

### Orders
- **GET** `/api/orders` - Get your orders
- **POST** `/api/orders/clear` - Clear orders

## Postman Setup

1. **Create collection** with base URL: `http://127.0.0.1:8001`

2. **Collection variables** (Settings → Variables):
   - `access_token` - Leave empty initially

3. **Register request**:
   - Method: POST
   - URL: `{{base_url}}/api/auth/register`
   - Body (JSON): Register credentials

4. **Login request**:
   - Method: POST
   - URL: `{{base_url}}/api/auth/login`
   - Body (JSON): Login credentials
   - **Tests tab** (auto-save token):
   ```javascript
   if (pm.response.code === 200) {
     var jsonData = pm.response.json();
     pm.collectionVariables.set("access_token", jsonData.data.access_token);
   }
   ```

5. **Any Protected Request** (e.g., PUT /api/sms/{id}):
   - Headers → Add: `Authorization` = `Bearer {{access_token}}`
   - This will use the token from Step 4

## Common Issues & Solutions

### Error: "Missing authentication token"
- **Cause**: Missing Authorization header
- **Fix**: Add `Authorization: Bearer <token>` to request headers

### Error: "Invalid token"
- **Cause**: Token is expired or malformed
- **Fix**: Login again to get a fresh token

### Error: "ECONNREFUSED"
- **Cause**: API server not running
- **Fix**: Start the server with: `python -m gocart_system.api`

### Error: "Product not found" / "SMS not found"
- **Cause**: Invalid ID
- **Fix**: Verify the resource exists with GET request first

## Token Expiration
- **Access token**: 30 minutes (default)
- **Refresh token**: 7 days (default)

Use `/api/auth/refresh` with your refresh token to get a new access token without logging in again.

