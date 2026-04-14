from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Import existing services
from .services.product_services import ProductServices
from .services.cart_on_services import CartOnServices

# Pydantic models for API requests
class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductUpdate(BaseModel):
    name: str
    price: float
    quantity: int

class CartAdd(BaseModel):
    product_name: str
    quantity: int

class CartRemove(BaseModel):
    product_name: str

class ApiPayload(BaseModel):
    name: str
    price: float
    quantity: int

# FastAPI app instance
app = FastAPI(title="GoCart API", description="API for GoCart shopping system")

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
product_service = ProductServices()
cart_service = CartOnServices()

# Create API router for /api/* routes
api_router = APIRouter(prefix="/api", tags=["api"])

# Products endpoints (under /api prefix)
@api_router.get("/products")
def get_api_products():
    """Get all products from the database."""
    try:
        products = product_service.get_products()
        return {"products": [p.to_dict() for p in products]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products")
def create_api_product(product: ProductCreate):
    """Create a new product."""
    try:
        product_service.create_product(product.name, product.price, product.quantity)
        return {
            "message": "Product created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.put("/products/{index}")
def update_api_product(index: int, product: ProductUpdate):
    """Update an existing product by index."""
    try:
        product_service.update_product(index, product.name, product.price, product.quantity)
        return {"message": "Product updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/products/{index}")
def delete_api_product(index: int):
    """Delete a product by index."""
    try:
        product_service.delete_product(index)
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Cart endpoints (under /api prefix)
@api_router.post("/cart/add")
def api_add_to_cart(cart_item: CartAdd):
    """Add item to cart."""
    try:
        result = cart_service.add_to_cart(cart_item.product_name, cart_item.quantity)
        return {"message": "Item added to cart", "item": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/cart")
def api_get_cart():
    """Get cart items and total price."""
    try:
        items = cart_service.get_cart_items()
        total = cart_service.get_total_price()
        return {
            "cart_items": [item.to_dict() for item in items],
            "total_price": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/cart/{product_name}")
def api_remove_from_cart(product_name: str):
    """Remove item from cart by product name."""
    try:
        cart_service.remove_from_cart(product_name)
        return {"message": f"Removed {product_name} from cart"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/cart/clear")
def api_clear_cart():
    """Clear all items from cart."""
    try:
        cart_service.clear_cart()
        return {"message": "Cart cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/cart/complete")
def api_complete_order():
    """Complete the order."""
    try:
        order = cart_service.complete_order()
        return {"message": "Order completed", "order": order}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Orders endpoints (under /api prefix)
@api_router.get("/orders")
def api_get_orders():
    """Get completed orders."""
    try:
        orders = cart_service.get_completed_orders()
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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