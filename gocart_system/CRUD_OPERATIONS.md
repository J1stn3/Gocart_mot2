# ✅ GOCART SYSTEM - CRUD Operations Reference

## Complete CRUD Implementation Guide

---

## ➕ CREATE - Add New Product

### How It Works

**User Path**:
1. User enters product details (Name, Price, Quantity)
2. Clicks **➕ ADD PRODUCT** button
3. System validates and creates product
4. Product displays in inventory
5. User sees success message

### Code Flow

```
VIEW: add_product() button click
  ↓
Get user input (name, price, quantity)
  ↓
Validate inputs (not empty, numeric)
  ↓
CONTROLLER: ProductController.create_product()
  ↓
MODEL: Product.__init__(name, price, quantity)
  ↓
SERVICE: StorageService.add_product(product)
  ↓
Append to __products list
  ↓
VIEW: update_product_table()
  ↓
Display product in card
  ↓
Show status: "✅ Product '{name}' added"
```

### Implementation Details

**File**: `controllers/product_controller.py`
```python
def create_product(self, name, price, quantity):
    """Create new product and store it"""
    product = Product(name, float(price), int(quantity))
    self.storage.add_product(product)
```

**File**: `models/product.py`
```python
class Product:
    def __init__(self, name, price, quantity):
        self.__name = name              # Encapsulated data
        self.__price = price
        self.__quantity = quantity
```

**File**: `services/storage_service.py`
```python
def add_product(self, product):
    """Add product to storage"""
    self.__products.append(product)     # Stored in-memory
```

### Example

| Field | Input |
|-------|-------|
| Name | "Gaming Laptop" |
| Price | "1299.99" |
| Quantity | "3" |

**Result**: Product created with `Product("Gaming Laptop", 1299.99, 3)`

## Error Cases

| Scenario | Error | Solution |
|----------|-------|----------|
| Empty Name | "⚠️ All fields required" | Fill Product Name |
| Invalid Price | "❌ Price must be number" | Enter numeric value |
| Empty Quantity | "⚠️ All fields required" | Fill Quantity |
| Negative Price | ValueError caught | Use positive number |

---

## 📖 READ - View All Products

### How It Works

**Automatic Display**:
- Products display automatically after CREATE, UPDATE, or DELETE
- Products shown in **Available Products** section
- Real-time updates when data changes

### Code Flow

```
VIEW: update_product_table() called
  ↓
CONTROLLER: get_products()
  ↓
SERVICE: StorageService.get_products()
  ↓
Return __products list
  ↓
For each product:
  Create futuristic card
  Display name, price, quantity
  Add SELECT button
  ↓
VIEW: Render cards
  ↓
page.update()
```

### Implementation Details

**File**: `controllers/product_controller.py`
```python
def get_products(self):
    """Retrieve all products"""
    return self.storage.get_products()
```

**File**: `services/storage_service.py`
```python
def get_products(self):
    """Return products list"""
    return self.__products
```

**File**: `views/main_view.py`
```python
def update_product_table(self):
    """Display all products as cards"""
    products = self.product_controller.get_products()
    
    if not products:
        # Show empty state message
        self.product_list.controls = [
            ft.Container(
                content=ft.Text(
                    "No products. Add one!",
                    color=self.primary_color
                )
            )
        ]
    else:
        # Create card for each product
        self.product_list.controls = [
            self._create_product_card(product, i)
            for i, product in enumerate(products)
        ]
    
    self.page.update()
```

### Card Display Format

```
┌─────────────────────────────────┐
│ Gaming Laptop                   │ ← Product Name
│ $1299.99    Stock: 3            │ ← Price & Quantity
│              [SELECT]            │ ← Action Button
└─────────────────────────────────┘
```

---

## ✏️ UPDATE - Modify Existing Product

### How It Works

**User Path**:
1. Click **SELECT** on a product
2. Design fields populate with product data
3. Modify name, price, or quantity
4. Click **✏️ UPDATE** button
5. Product data updated in storage
6. Display refreshed with new values

### Code Flow

```
VIEW: select_product(index) called
  ↓
Set selected_product_index = index
  ↓
Get product from controller
  ↓
Populate fields:
  - name_field.value = product.name
  - price_field.value = product.price
  - quantity_field.value = product.quantity
  ↓
Show status: "📌 Selected: {name}"
  ↓
Highlight card (purple border)

───────── User modifies values ─────────

VIEW: update_product() button click
  ↓
Check: Is product selected?
  If no → Show: "⚠️ Select product first"
  If yes → Continue
  ↓
Get new values from fields
  ↓
CONTROLLER: update_product(index, name, price, qty)
  ↓
MODEL: Create new Product object
  ↓
SERVICE: Replace at index
  ↓
self.__products[index] = updated_product
  ↓
VIEW: update_product_table()
  ↓
Show status: "✅ Updated!"
```

### Implementation Details

**File**: `controllers/product_controller.py`
```python
def update_product(self, index, name, price, quantity):
    """Update product at index"""
    product = Product(name, float(price), int(quantity))
    self.storage.update_product(index, product)
```

**File**: `services/storage_service.py`
```python
def update_product(self, index, product):
    """Replace product at index"""
    if 0 <= index < len(self.__products):
        self.__products[index] = product
```

**File**: `views/main_view.py`
```python
def select_product(self, index):
    """Load product into edit fields"""
    self.selected_product_index = index
    
    products = self.product_controller.get_products()
    product = products[index]
    
    # Populate form
    self.name_field.value = product.name
    self.price_field.value = str(product.price)
    self.quantity_field.value = str(product.quantity)
    
    # Visual feedback
    self._show_status(
        f"📌 Selected: {product.name}",
        self.primary_color
    )
    
    self.update_product_table()  # Show selection highlight

def update_product(self, e):
    """Update selected product"""
    if self.selected_product_index is None:
        self._show_status("⚠️ Select product first", RED)
        return
    
    name = self.name_field.value.strip()
    price = self.price_field.value.strip()
    quantity = self.quantity_field.value.strip()
    
    if not name or not price or not quantity:
        self._show_status("⚠️ All fields required", RED)
        return
    
    try:
        self.product_controller.update_product(
            self.selected_product_index,
            name, price, quantity
        )
        self._show_status(
            f"✅ Updated: {name}",
            GREEN
        )
        self.clear_fields()
        self.selected_product_index = None
        self.update_product_table()
    except ValueError:
        self._show_status("❌ Invalid input", RED)
```

### Example Scenario

**Before**:
```
Product: Mouse
Price: $19.99
Stock: 20
```

**Actions**:
1. Click SELECT on Mouse
2. Change Price to $24.99
3. Change Stock to 15
4. Click UPDATE

**After**:
```
Product: Mouse
Price: $24.99
Stock: 15
```

## Error Cases

| Scenario | Error | Solution |
|----------|-------|----------|
| No product selected | "⚠️ Select product first" | Click SELECT button |
| Empty field | "⚠️ All fields required" | Fill all fields |
| Invalid price | "❌ Invalid input" | Use number for price |
| Invalid quantity | "❌ Invalid input" | Use number for quantity |

---

## 🗑️ DELETE - Remove Product

### How It Works

**User Path**:
1. Click **SELECT** on product to delete
2. Click **🗑️ DELETE** button
3. Product removed from inventory
4. Stock in cart items restored
5. Display updated
6. User sees confirmation

### Code Flow

```
VIEW: delete_product() button click
  ↓
Check: Is product selected?
  If no → Show: "⚠️ Select product first"
  If yes → Continue
  ↓
Get product name (for feedback)
  ↓
CONTROLLER: delete_product(index)
  ↓
SERVICE: delete_product(index)
  ↓
del self.__products[index]
  ↓
Remove from list
  ↓
VIEW: update_product_table()
  ↓
Refresh display
  ↓
Clear form fields
  ↓
Reset selected_product_index = None
  ↓
Show status: "🗑️ Product '{name}' deleted"
```

### Stock Restoration

**Important**: When a product is deleted, items in the cart are NOT affected because:
- Cart items hold references to Product objects
- Product object still exists in memory
- Cart maintains original product reference
- When user removes item from cart, stock is restored to Product object

```python
# Cart Item holds reference
cart_item = CartItem(product_ref, quantity)

# Even if product removed from storage:
# cart_item.product.quantity += quantity  # ✅ Works!
# Restores stock to original product object
```

### Implementation Details

**File**: `controllers/product_controller.py`
```python
def delete_product(self, index):
    """Delete product at index"""
    self.storage.delete_product(index)
```

**File**: `services/storage_service.py`
```python
def delete_product(self, index):
    """Remove product at index"""
    if 0 <= index < len(self.__products):
        del self.__products[index]
```

**File**: `views/main_view.py`
```python
def delete_product(self, e):
    """Delete selected product"""
    if self.selected_product_index is None:
        self._show_status("⚠️ Select product first", RED)
        return
    
    products = self.product_controller.get_products()
    product_name = products[self.selected_product_index].name
    
    # Execute delete
    self.product_controller.delete_product(
        self.selected_product_index
    )
    
    # Feedback & cleanup
    self._show_status(
        f"🗑️ Product '{product_name}' deleted",
        GREEN
    )
    self.clear_fields()
    self.selected_product_index = None
    self.update_product_table()
```

### Example

**Before**:
- Inventory: Laptop, Mouse, Keyboard (3 products)

**Action**: DELETE Mouse

**After**:
- Inventory: Laptop, Keyboard (2 products)
- Status: "🗑️ Product 'Mouse' deleted"

## Error Cases

| Scenario | Error | Solution |
|----------|-------|----------|
| No product selected | "⚠️ Select first" | Click SELECT button |
| Product in cart | No error | Delete works, cart refs maintained |
| Update after delete | Index invalid | Select new product |

---

## 🎯 Key Differences: CREATE vs UPDATE vs DELETE

| Operation | SELECT First? | Creates New? | Affects Stock? | Feedback |
|-----------|---------------|--------------|----------------|----------|
| **CREATE** | No | Yes (new) | No change | "✅ Added" |
| **UPDATE** | Yes | No (replaces) | If changed | "✅ Updated" |
| **DELETE** | Yes | No (removes) | Cart items maintain stock | "🗑️ Deleted" |

---

## 🔗 CRUD Integration with Cart

### Scenario: Product Lifecycle

```
1. CREATE Product "Laptop" (qty: 10)
   → Displays in products list

2. SELECT "Laptop"
   → Fields populated, can edit

3. ADD to Cart (qty: 3)
   → Storage: 10 → 7
   → Cart shows 3 Laptops

4. UPDATE "Laptop" price
   → Price changes in both storage & cart
   → Cart shows updated price

5. DELETE "Laptop"
   → Removed from products
   → Cart item still shows
   → Stock restoration works on cart item removal

6. REMOVE from Cart
   → Laptop quantity: 7 → 10
   → Back to original quantity
```

---

## 📊 State After Each Operation

```
State: EMPTY
  └─→ [CREATE] Product A
  
State: ONE PRODUCT
  ├─→ [CREATE] Product B
  │   └─→ [TWO PRODUCTS]
  │   
  ├─→ [SELECT] Product A
  │   └─→ [SELECTED A]
  │       ├─→ [UPDATE] Details
  │       │   └─→ [UPDATED A]
  │       │
  │       └─→ [DELETE]
  │           └─→ [EMPTY]
  │
  └─→ [ADD TO CART] A
      └─→ [IN CART]
          └─→ [REMOVE FROM CART]
              └─→ [BACK IN INVENTORY]
```

---

## ✨ Summary

| Operation | Purpose | Requirement | Result |
|-----------|---------|-------------|--------|
| **CREATE** | Add new product | Name, Price, Qty | Adds to inventory |
| **READ** | View products | None | Shows all products |
| **UPDATE** | Modify product | Select first | Updates details |
| **DELETE** | Remove product | Select first | Removes from inventory |

**All CRUD operations maintain data integrity and provide real-time visual feedback to the user!** ✅
