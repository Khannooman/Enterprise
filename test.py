from app.controllers.database_controllers import DatabaseController
db = DatabaseController()

# Create a user
user = db.create_user(
    username="ayesha",
    password="password123",
    email="ayesha@kainos.com",
    phone_number="123-456-7890",
    company_name="ABC Trading",
    addressline1="123 Main St",
    city="Mumbai",
    state="Maharashtra",
    pincode="400001",
    country="India",
    return_json=True
)

# Create a product
product = db.create_product(
    user_id=user["user_id"],
    product="Widget A",
    selling_price=8.00,
    mrp=10.00,
    quantity=100,
    return_json=True
)

# Add stock
updated_product = db.add_stock_entry(
    product_id=product["product_id"],
    user_id=user["user_id"],
    quantity=50,
    return_json=True
)  # Stock increases from 100 to 150

# Create an order
order = db.create_order(
    user_id=user["user_id"],
    product_id=product["product_id"],
    customer_id="CUST001",
    created_by=user["user_id"],
    quantity=20,
    rate=8.00,
    return_json=True
)  # Stock decreases from 150 to 130