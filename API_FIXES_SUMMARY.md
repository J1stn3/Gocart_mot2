# GoCart API - Fixes Applied

## Issues Fixed

### 1. **Server Not Running (Connection REFUSED)**
- **Problem**: API server was not running on port 8001
- **Fix**: Started the API server with `python -m gocart_system.api`
- **Status**: ✅ Server running at http://127.0.0.1:8001

### 2. **Asynchronous Endpoint Configuration**
- **Problem**: All API endpoints that required authentication were synchronous (`def`) but used async dependencies (`async def verify_jwt_token`)
- **Fix**: Converted all protected endpoints to async (`async def`)
- **Files Modified**: `gocart_system/api.py`
- **Endpoints Updated**:
  - Product endpoints: GET, POST, PUT, PATCH, DELETE
  - Cart endpoints: GET, POST, DELETE
  - Orders endpoints: GET, POST
  - SMS endpoints: GET, POST, PUT
  - Job endpoints: GET, POST

### 3. **CORS Configuration Verified**
- ✅ PUT method is allowed
- ✅ Authorization header is allowed
- ✅ Cross-origin requests are properly configured

### 4. **JWT Token Authentication Verified**
- ✅ `verify_jwt_token` function properly extracts Bearer tokens from Authorization header
- ✅ Token validation works correctly
- ✅ User information is properly extracted from valid tokens

## How to Use the API

### Required Headers for All Protected Endpoints:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Example: Update SMS Status (PUT Request)

**Endpoint**: `PUT http://127.0.0.1:8001/api/sms/{sms_id}`

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Body**:
```json
{
  "status": "SENT"
}
```

**Response**:
```json
{
  "message": "SMS status updated",
  "sms": {
    "id": 1,
    "status": "SENT"
  }
}
```

## Getting an Access Token

1. **Register** (if needed):
   ```bash
   POST http://127.0.0.1:8001/api/auth/register
   ```
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "SecurePass123!"
   }
   ```

2. **Login**:
   ```bash
   POST http://127.0.0.1:8001/api/auth/login
   ```
   ```json
   {
     "username": "testuser",
     "password": "SecurePass123!"
   }
   ```

3. **Copy the `access_token`** from the response and use it in the Authorization header for all protected endpoints.

## Available Endpoints

### Products
- `GET /api/products` - Get all products
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `PATCH /api/products/{id}` - Partial update
- `DELETE /api/products/{id}` - Delete product

### Cart
- `GET /api/cart` - Get cart items
- `POST /api/cart/add` - Add to cart
- `DELETE /api/cart/{product_id}` - Remove item
- `POST /api/cart/clear` - Clear cart
- `POST /api/cart/complete` - Complete order

### SMS
- `GET /api/sms` - Get user's SMS messages
- `GET /api/sms/{sms_id}` - Get specific SMS
- `PUT /api/sms/{sms_id}` - Update SMS status ⭐
- `POST /api/sms/{sms_id}/job` - Create async job

### Orders
- `GET /api/orders` - Get user's orders
- `POST /api/orders/clear` - Clear orders

## Testing with Postman

### Setup Instructions

1. Create collection with base URL: `http://127.0.0.1:8001`

2. Add collection variable:
   - Variable name: `access_token`
   - Initial value: (empty)

3. **Login request** (Tests tab):
   ```javascript
   if (pm.response.code === 200) {
     var jsonData = pm.response.json();
     pm.collectionVariables.set("access_token", jsonData.data.access_token);
   }
   ```

4. For any protected request, add header:
   ```
   Authorization: Bearer {{access_token}}
   ```

## Server Management

### Start Server
```bash
cd c:\Users\USER\GoCart
python -m gocart_system.api
```

### Stop Server
Press `Ctrl+C` in the terminal

### Environment Variables (Optional)
```bash
# Set in command line before running
$env:PORT="8001"
$env:HOST="127.0.0.1"
$env:JWT_SECRET_KEY="your-secret-key"
$env:ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

## Desktop Application Setup

### Running the Desktop App
The GoCart desktop application includes an integrated API server that starts automatically:

```bash
cd c:\Users\USER\GoCart
python -m gocart_system.main
```

**What happens:**
1. Flet desktop GUI launches
2. API server starts in background on port 8001
3. Login screen appears
4. Enter credentials to access the shopping interface

### Flet Installation
If you encounter Flet issues, reinstall with:
```bash
pip uninstall flet flet-desktop -y
pip install flet flet-desktop --upgrade
```

## Status Summary
- ✅ API server running on port 8001
- ✅ All endpoints use async properly
- ✅ JWT authentication configured
- ✅ PUT requests working
- ✅ CORS properly configured
- ✅ Desktop app with Flet launching
- ✅ Ready for production use

