from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn
import logging
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Import existing services
from .services.product_services import ProductServices
from .services.auth_service import AuthenticationService
from .services.auth_logger import auth_logger
from .services.cart_db_service import CartDbService
from .services.auth_middleware import verify_jwt_token
from .controllers.auth_controller import router as auth_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests
class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductUpdate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class CartAdd(BaseModel):
    product_id: int
    quantity: int

class ApiPayload(BaseModel):
    name: str
    price: float
    quantity: int

# FastAPI app instance
app = FastAPI(
    title="GoCart Secure API",
    description="Secure API for GoCart shopping system with JWT authentication",
    version="1.0.0"
)

# Get allowed origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
environment = os.getenv("ENVIRONMENT", "development")

# Add Security Middleware
# Trust proxy headers (X-Forwarded-For, X-Forwarded-Proto) in production
if environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[host.split("://")[-1].split(":")[0] for host in allowed_origins]
    )

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if environment != "production" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # 10 minutes
)

# Initialize services
product_service = ProductServices()
cart_service = CartDbService()

# Create API router for /api/* routes
api_router = APIRouter(prefix="/api", tags=["api"])

# Products endpoints (under /api prefix)
@api_router.get("/products")
def get_api_products(user: dict = Depends(verify_jwt_token)):
    """Get all products from the database."""
    try:
        products = product_service.get_products()
        return {"products": [p.to_dict() for p in products]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products")
def create_api_product(product: ProductCreate, user: dict = Depends(verify_jwt_token)):
    """Create a new product."""
    try:
        product_service.create_product(product.name, product.price, product.quantity)
        return {
            "message": "Product created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.put("/products/{product_id}")
def update_api_product(product_id: int, product: ProductUpdate, user: dict = Depends(verify_jwt_token)):
    """Update an existing product by id."""
    try:
        # ProductServices updates by index; map id -> index for backward compatibility.
        products = product_service.get_products()
        idx = next((i for i, p in enumerate(products) if p.id == product_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Product not found")
        product_service.update_product(idx, product.name, product.price, product.quantity)
        return {"message": "Product updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.patch("/products/{product_id}")
def patch_api_product(product_id: int, patch: ProductPatch, user: dict = Depends(verify_jwt_token)):
    """Partially update a product by id."""
    try:
        products = product_service.get_products()
        existing = next((p for p in products if p.id == product_id), None)
        if existing is None:
            raise HTTPException(status_code=404, detail="Product not found")

        name = patch.name if patch.name is not None else existing.name
        price = patch.price if patch.price is not None else existing.price
        quantity = patch.quantity if patch.quantity is not None else existing.quantity

        idx = next((i for i, p in enumerate(products) if p.id == product_id), None)
        product_service.update_product(idx, name, price, quantity)
        return {"message": "Product patched successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/products/{product_id}")
def delete_api_product(product_id: int, user: dict = Depends(verify_jwt_token)):
    """Delete a product by id."""
    try:
        products = product_service.get_products()
        idx = next((i for i, p in enumerate(products) if p.id == product_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Product not found")
        product_service.delete_product(idx)
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Optional legacy endpoints: index-based update/delete (supports /api/products/0 style workflows)
@api_router.put("/products/index/{index}")
def update_api_product_by_index(index: int, product: ProductUpdate, user: dict = Depends(verify_jwt_token)):
    """Update a product by index (legacy)."""
    try:
        product_service.update_product(index, product.name, product.price, product.quantity)
        return {"message": "Product updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/products/index/{index}")
def delete_api_product_by_index(index: int, user: dict = Depends(verify_jwt_token)):
    """Delete a product by index (legacy)."""
    try:
        product_service.delete_product(index)
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Cart endpoints (under /api prefix)
@api_router.post("/cart/add")
def api_add_to_cart(cart_item: CartAdd, user: dict = Depends(verify_jwt_token)):
    """Add item to cart."""
    try:
        cart_service.add_to_cart(int(user["user_id"]), cart_item.product_id, cart_item.quantity)
        return {"message": "Added to cart", "success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/cart")
def api_get_cart(user: dict = Depends(verify_jwt_token)):
    """Get cart items and total price."""
    try:
        items, total = cart_service.get_cart(int(user["user_id"]))
        return {
            "cart_items": [item.to_api_dict() for item in items],
            "total_price": float(total)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/cart/{product_id}")
def api_remove_from_cart(product_id: int, user: dict = Depends(verify_jwt_token)):
    """Remove item from cart by product id."""
    try:
        cart_service.remove_from_cart(int(user["user_id"]), product_id)
        return {"message": "Removed from cart"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/cart/clear")
def api_clear_cart(user: dict = Depends(verify_jwt_token)):
    """Clear all items from cart."""
    try:
        cart_service.clear_cart(int(user["user_id"]))
        return {"message": "Cart cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cart/complete")
def api_complete_order(user: dict = Depends(verify_jwt_token)):
    """Complete the order."""
    try:
        order = cart_service.checkout(int(user["user_id"]))
        return {"message": "Order completed", "order": order}
    except Exception as e:
        logger.exception("Checkout failed")
        raise HTTPException(status_code=400, detail=str(e))

# Orders endpoints (under /api prefix)
@api_router.get("/orders")
def api_get_orders(user: dict = Depends(verify_jwt_token)):
    """Get completed orders."""
    try:
        orders = cart_service.list_orders(int(user["user_id"]))
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/orders/clear")
def api_clear_orders(user: dict = Depends(verify_jwt_token)):
    """Clear all completed orders."""
    try:
        cart_service.clear_orders(int(user["user_id"]))
        return {"message": "All orders cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the Authentication router
app.include_router(auth_router)

# Include the API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint to confirm API is running."""
    return {"message": "GoCart API is running", "status": "active"}

# 404 handler for unknown /api/* routes - returns JSON, not HTML
@app.exception_handler(404)
async def api_404_handler(request, exc):
    """Return JSON 404 for API routes, not HTML."""
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"detail": f"API endpoint '{request.url.path}' not found"}
        )
    # For non-API routes, re-raise the exception (default behavior)
    raise exc

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "61471"))
    display_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"Starting GoCart API on http://{display_host}:{port}")
    uvicorn.run(app, host=host, port=port)