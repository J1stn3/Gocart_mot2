# 🚀 GOCART SYSTEM - Futuristic Shopping Cart Application

A sophisticated **Python-based shopping cart management system** built with the **Flet GUI framework**, following strict **Object-Oriented Programming (OOP)** principles and the **MVC (Model–View–Controller)** architecture.

## 🎨 Features

### ✨ Futuristic Design
- **Dark Theme**: Modern dark background with neon cyan, purple, and pink accents
- **Responsive Layout**: Clean, organized sections for products and cart
- **Visual Feedback**: Real-time status messages with emoji indicators
- **Smooth Interactions**: Futuristic-styled buttons and text fields

### 📦 CRUD Operations

#### ➕ **CREATE PRODUCT**
- Add new products with name, price, and quantity
- Input validation ensures numeric prices and quantities
- Success feedback with emoji indicators

#### 📖 **READ PRODUCTS**
- View all products in a modern card-based layout
- Display product name, price, and current stock
- Real-time updates when products are modified

#### ✏️ **UPDATE PRODUCT**
- Select a product and modify its details
- Click "UPDATE" button to save changes
- Confirmation feedback with product name

#### 🗑️ **DELETE PRODUCT**
- Remove products from the inventory
- Automatic stock restoration when items are removed from cart
- Clear visual feedback on deletion

### 🛒 CART MANAGEMENT

#### Add to Cart
- Select a product and specify quantity
- Stock is automatically deducted
- Status message confirms addition
- Supports multiple quantities of the same product

#### View Cart
- Display all cart items in futuristic cards
- Show quantity and per-item price
- Calculate and display **total price** in real-time

#### Remove from Cart
- Delete individual items from cart
- Stock is automatically restored

### 🛍️ SHOPPING PAGE (NEW!)

#### Browse Products
- Dedicated shopping interface for browsing all products
- Click **🛍️ GO SHOPPING** button to access
- Modern product cards showing name, price, and stock
- Real-time stock updates while shopping

#### Search Products
- **Real-time search** as you type
- Filter by product name (case-insensitive)
- Filter by price values
- Supports partial name matching
- Shows no results message when nothing matches

#### Quick Add to Cart
- Select any product with **SELECT & ADD** button
- Set quantity before adding
- Stock validation prevents over-purchasing
- Immediate feedback on successful addition
- **Seamless navigation** back to main cart manager
- Cart syncs between shopping and main pages
- Delete button with icon for easy access

#### Cart Summary
- **Live total price calculation**
- Item count tracking
- Clear cart option

## 🏗️ Architecture

### **MVC Pattern**

#### **Models** (`models/`)
- **Product**: Encapsulates product data with private attributes
  - Properties: `name`, `price`, `quantity`
  - Methods: Getters/setters with @property decorators
  
- **CartItem**: Represents an item in the shopping cart
  - Properties: `product`, `quantity`
  - Methods: Calculate total price per item
  
- **Cart**: Manages the collection of cart items
  - Methods: Add, remove, and clear items
  - Calculate total cart value

#### **Controllers** (`controllers/`)
- **ProductController**: Handles CRUD operations for products
  - create_product()
  - get_products()
  - update_product()
  - delete_product()
  
- **CartController**: Manages cart interactions
  - add_to_cart()
  - remove_from_cart()
  - get_cart_items()
  - get_total_price()
  - clear_cart()

#### **Views** (`views/`)
- **MainView**: Flet-based GUI implementation
  - Futuristic UI components
  - Event handlers for all user interactions
  - Real-time updates and visual feedback

#### **Services** (`services/`)
- **StorageService**: In-memory storage (Singleton pattern)
  - Product persistence during session
  - Find products by name
  - Access products list

### **OOP Principles Demonstrated**

1. **Encapsulation**: Private attributes with public properties
   ```python
   self.__name = name  # Private attribute
   @property
   def name(self):     # Public getter
       return self.__name
   ```

2. **Abstraction**: Hide implementation details in models
   - Business logic separated from UI
   - Controllers abstract model operations

3. **Inheritance**: (Built-in for future extensions)
   - Singleton pattern in StorageService
   - Extensible controller architecture

4. **Polymorphism**: Flexible method implementations
   - Cart can handle items of any product
   - Controllers provide unified interfaces

## 📁 Project Structure

```
gocart_system/
│
├── main.py                          # Entry point with AppManager
│
├── models/
│   ├── __init__.py
│   ├── product.py                   # Product model
│   ├── cart_item.py                 # CartItem model
│   └── cart.py                      # Cart model
│
├── controllers/
│   ├── __init__.py
│   ├── product_controller.py        # Product CRUD handler
│   └── cart_controller.py           # Cart operations handler
│
├── views/
│   ├── __init__.py
│   ├── main_view.py                 # Main cart manager GUI
│   └── shopping_view.py             # Shopping/browsing GUI (NEW!)
│
├── services/
│   ├── __init__.py
│   └── storage_service.py           # Data persistence service
│
├── README.md                        # Complete documentation
├── QUICK_START.md                   # Quick reference guide
├── CRUD_OPERATIONS.md               # CRUD implementation details
├── DESIGN_ARCHITECTURE.md           # MVC patterns & design
└── SHOPPING_FEATURE.md              # Shopping page guide (NEW!)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Flet framework

### Installation

1. **Install Flet**:
   ```bash
   pip install flet
   ```

2. **Navigate to project directory**:
   ```bash
   cd gocart_system
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 💻 Usage Guide

### Adding a Product
1. Enter **Product Name** in the text field
2. Enter **Price** (numeric value)
3. Enter **Quantity** (numeric value)
4. Click **➕ ADD PRODUCT** button
5. Receive confirmation message

### Selecting and Viewing Products
1. Click **SELECT** button on any product card
2. Product details populate the input fields
3. Product is highlighted with purple border
4. Ready for update or delete operations

### Updating a Product
1. Select a product (see above)
2. Modify the name, price, or quantity
3. Click **✏️ UPDATE** button
4. Confirmation message displays

### Deleting a Product
1. Select a product
2. Click **🗑️ DELETE** button
3. Product is removed from inventory
4. Confirmation message displays

### Adding to Cart
1. Select a product
2. Enter desired **Quantity** in "Add to cart" field
3. Click **🛒 ADD** button
4. If stock is available, item is added to cart
5. Stock is automatically deducted
6. Total price updates in real-time

### Removing from Cart
1. View your cart items
2. Click the **delete icon** (🗑️) on the cart item
3. Item is removed and stock is restored
4. Total price updates automatically

## 🎨 Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Cyan | `#00d4ff` | Primary interactive elements |
| Purple | `#7c3aed` | Secondary accents, selection |
| Pink | `#ff006e` | Destructive actions (delete) |
| Green | `#00ff88` | Success messages, total price |
| Dark Blue | `#0a0e27` | Main background |
| Dark Gray | `#1a1f3a` | Card backgrounds |

## 🔧 Technical Specifications

### Data Flow
```
User Input (View)
    ↓
Event Handler (Controller)
    ↓
Business Logic (Model)
    ↓
Storage Service (Persistence)
    ↓
Update Display (View)
```

### State Management
- **Selected Product Index**: Tracks currently selected product
- **Product List**: In-memory storage with reference passing
- **Cart Items**: Maintains references to original products

### Error Handling
- Input validation for numeric fields
- Stock availability checks
- User-friendly error messages
- Try-except blocks for conversion errors

## 🎯 Functional Requirements Met

- ✅ Create Product (Add with name, price, quantity)
- ✅ Read/View Products (Display list with details)
- ✅ Update Product (Edit selected product)
- ✅ Delete Product (Remove from inventory)
- ✅ Add to Cart (With stock management)
- ✅ View Cart (Display items and total)
- ✅ Remove from Cart (Item deletion and stock restoration)
- ✅ **Shopping Page** (Dedicated browsing interface)
- ✅ **Product Search** (Real-time filtering by name/price)
- ✅ **Page Navigation** (Seamless switching between views)
- ✅ MVC Architecture (Separate models, views, controllers)
- ✅ OOP Principles (Encapsulation, abstraction, modularity)
- ✅ Futuristic Design (Modern UI with neon colors)

## 🐛 Debugging Tips

### Issue: Application won't start
- Ensure Flet is installed: `pip install flet`
- Verify you're running from `gocart_system` directory
- Check Python version: `python --version` (3.7+)

### Issue: Import errors
- Verify all `__init__.py` files exist in each package
- Check file paths and spelling in imports
- Run from `gocart_system` root directory

### Issue: GUI appears but no interaction
- Verify Flet display (may open in browser window)
- Check console for error messages
- Ensure valid numeric inputs

## 📝 Code Example: Adding a Product

```python
# User enters: name="Laptop", price="999.99", quantity="5"
# Button click triggers:
controller.create_product("Laptop", "999.99", "5")

# In ProductController:
product = Product("Laptop", 999.99, 5)
storage.add_product(product)

# Product is stored with encapsulated attributes
# View updates automatically showing new product
```

## 🔮 Future Enhancements

- CSV/JSON export for cart and products
- Order history tracking
- Discount and promotion codes
- Multiple user accounts
- Product search and filtering
- Checkout and payment simulation
- Database integration (SQLite/MySQL)

## 📄 License

This project is open-source and available for educational and personal use.

## 👨‍💻 Contributing

Contributions are welcome! Feel free to fork, modify, and improve the application.

---

**Built with ❤️ using Python, Flet, and OOP Principles**
