# 🎮 GOCART SYSTEM - Quick Start Guide

## 🚀 Launch the Application

```bash
cd gocart_system
python main.py
```

The application will open in your default browser window.

---

## 📋 CRUD Operations Quick Reference

### ➕ CREATE (Add Product)
| Step | Action |
|------|--------|
| 1 | Enter **Product Name** |
| 2 | Enter **Price** (e.g., 29.99) |
| 3 | Enter **Quantity** (e.g., 10) |
| 4 | Click **➕ ADD PRODUCT** |
| ✅ | See green success message |

**Example**: Laptop, 999.99, 5

---

### 📖 READ (View Products)
- All products automatically display in **Available Products** section
- Shows: Product name, Price ($), Stock quantity
- Updated in real-time after any operation

---

### ✏️ UPDATE (Modify Product)
| Step | Action |
|------|--------|
| 1 | Click **SELECT** on a product card |
| 2 | Product details load into input fields |
| 3 | Modify name, price, or quantity |
| 4 | Click **✏️ UPDATE** |
| ✅ | See success message |

**Note**: Only works on selected products!

---

### 🗑️ DELETE (Remove Product)
| Step | Action |
|------|--------|
| 1 | Click **SELECT** on a product card |
| 2 | Click **🗑️ DELETE** |
| 3 | Product is removed |
| ✅ | Stock automatically restored to cart items |

**Warning**: Cannot undo deletion!

---

## 🛒 SHOPPING CART OPERATIONS

### Add to Cart
| Step | Action |
|------|--------|
| 1 | Click **SELECT** on a product |
| 2 | Enter quantity in **"Add to cart"** field |
| 3 | Click **🛒 ADD** |
| ✅ | Product added, stock reduced, total updated |

---

### View Cart
- **Shopping Cart** section shows all items
- Each item displays:
  - Product name (in green)
  - Quantity
  - Unit price
  - Total (name × price)

---

### Remove from Cart
- Click the **🗑️** (delete icon) on any cart item
- Item is removed
- Stock is restored to product inventory
- Total price updates automatically

---

## 🎨 UI Elements Explained

### Section Colors
| Section | Color | Meaning |
|---------|-------|---------|
| Header | Cyan | Main title & info |
| Input Area | Pink Border | Add/Update products |
| Products | Cyan Border | Available inventory |
| Cart | Green Border | Shopping items |

### Button Colors
| Button | Color | Function |
|--------|-------|----------|
| ➕ ADD | Cyan | Create product |
| ✏️ UPDATE | Purple | Modify product |
| 🗑️ DELETE | Pink | Remove product |
| 🛒 ADD | Green | Add to cart |
| SELECT | Purple/Dark | Choose product |

### Status Messages

| Message | Color | Meaning |
|---------|-------|---------|
| ✅ (Green) | Success | Operation completed |
| ❌ (Pink) | Error | Invalid input or missing data |
| ⚠️ (Pink) | Warning | Select product first |
| 📌 (Cyan) | Info | Product selected |

---

## ⚙️ Input Validation

### Product Name
- ✅ Any text (letters, numbers, symbols)
- ❌ Cannot be empty

### Price
- ✅ Numeric values (e.g., 19.99)
- ❌ Must be a valid number
- ❌ Cannot be empty

### Quantity
- ✅ Whole numbers (e.g., 5, 10, 100)
- ❌ Must be a valid number
- ❌ Cannot be empty or zero
- ❌ Cannot exceed available stock

---

## 📊 Example Usage Scenario

### Step 1: Add Products
```
Product 1: Wireless Mouse, $19.99, Qty: 20
Product 2: USB-C Cable, $9.99, Qty: 50
Product 3: Laptop Stand, $49.99, Qty: 8
```

### Step 2: Browse Products
- See all products in **Available Products** section
- Notice stock quantities

### Step 3: Build Your Cart
1. Select "Wireless Mouse" → Add 2 to cart
2. Select "USB-C Cable" → Add 5 to cart
3. Select "Laptop Stand" → Add 1 to cart

### Step 4: Calculate Total
```
2 × $19.99 = $39.98
5 × $9.99 = $49.95
1 × $49.99 = $49.99
───────────────────
Total = $139.92 💰
```

### Step 5: Manage Cart
- Remove unwanted items by clicking delete icon
- Stock is restored for future purchase

---

## 🔄 Product Lifecycle

```
CREATE → READ → SELECT → UPDATE → READ
   ↓                       ↓
 STATUS                 STATUS
   ↓                       ↓
VISIBLE IN PRODUCTS ← VISIBLE IN PRODUCTS

         ↓
      DELETE
         ↓
      REMOVED (but stock restored to cart)
```

---

## 💡 Pro Tips

1. **Efficient Updating**: Click SELECT on product → Modify → UPDATE
2. **Batch Operations**: Add multiple quantities of same product
3. **Inventory Check**: Stock reduces when adding to cart, restores on removal
4. **Clear Fields**: Fields auto-clear after successful ADD
5. **Status Feedback**: Always watch status message for operation result

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Please select a product first" | Click SELECT on a product before updating/deleting/adding to cart |
| "Invalid input..." | Use numbers for Price and Quantity fields |
| "Not enough stock" | Reduce the quantity or check available stock |
| "All fields are required" | Fill in all three fields: Name, Price, Quantity |
| Application won't start | Install Flet: `pip install flet` |
| Can't see app in browser | Check browser console; window may open in new tab |

---

## 🎯 Architecture at a Glance

```
User Clicks Button
       ↓
  View (GUI)
       ↓
 Controller
       ↓
   Model (Data)
       ↓
  Service (Storage)
       ↓
  Back to View (Update Display)
```

**Key**: Each layer has ONE job!
- **View**: Show stuff
- **Controller**: Decide what to do
- **Model**: Store & calculate
- **Service**: Keep data safe

---

## 📚 Learn More

See `README.md` for:
- ✅ Full feature documentation
- ✅ Architecture details
- ✅ OOP principles explained
- ✅ Code examples
- ✅ Future enhancements

---

**Happy Shopping with GoCart! 🚀🛒**
