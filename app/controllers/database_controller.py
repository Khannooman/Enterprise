from fastapi import HTTPException
from app.databases.postgres_database_manager import PostgreSQLManager
from sqlalchemy import text
from typing import Optional
from datetime import datetime , date
import json
import logging
from typing import List, Any, Dict, Optional, Union, Tuple
from app.utils.utility_manager import UtilityManager
from app.utils.invoice_number_generator import generate_invoice_number

class DatabaseController(UtilityManager):
    def __init__(self):
        self.db = PostgreSQLManager()
        self.db.create_tables()

    # ====== User Management Methods ======

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        phone_number: str,
        company_name: str,
        addressline1: str,
        city: str,
        state: str,
        pincode: str,
        country: str,
        addressline2: Optional[str] = None,
        landmark: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Create a new user"""
        hashed_password = self.hash_password(password)
        user_id = self.generate_uuid()

        # Check for existing username or email
        check_query = "SELECT user_id FROM users WHERE username = :username OR email = :email"
        existing_user = self.db.execute_query(check_query, params={"username": username, "email": email}, fetch_one=True, return_json=return_json)
        if existing_user:
            raise HTTPException(status_code=409, detail="Username or email already exists!")

        query = """
        INSERT INTO users (
            user_id, username, password, email, phone_number, company_name,
            addressline1, addressline2, landmark, city, state, pincode, country
        )
        VALUES (
            :user_id, :username, :password, :email, :phone_number, :company_name,
            :addressline1, :addressline2, :landmark, :city, :state, :pincode, :country
        )
        RETURNING user_id, username, email, phone_number, company_name,
            addressline1, addressline2, landmark, city, state, pincode, country;
        """

        params = {
            "user_id": user_id,
            "username": username,
            "password": hashed_password,
            "email": email,
            "phone_number": phone_number,
            "company_name": company_name,
            "addressline1": addressline1,
            "addressline2": addressline2,
            "landmark": landmark,
            "city": city,
            "state": state,
            "pincode": pincode,
            "country": country
        }

        user = self.db.execute_query(query, params, fetch_one=True, return_json=return_json)
        return user

    def get_user(self, user_id: str, return_json: Optional[bool] = False) -> Dict:
        """Retrieve a user by ID"""
        query = "SELECT * FROM users WHERE user_id = :id"
        user = self.db.execute_query(query, params={"id": user_id}, fetch_one=True, return_json=return_json)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(
        self,
        user_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        company_name: Optional[str] = None,
        addressline1: Optional[str] = None,
        addressline2: Optional[str] = None,
        landmark: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        country: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Update a user's details"""
        updates = {}
        if phone_number: updates["phone_number"] = phone_number
        if company_name: updates["company_name"] = company_name
        if addressline1: updates["addressline1"] = addressline1
        if addressline2: updates["addressline2"] = addressline2
        if landmark: updates["landmark"] = landmark
        if city: updates["city"] = city
        if state: updates["state"] = state
        if pincode: updates["pincode"] = pincode
        if country: updates["country"] = country

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
        query = f"""UPDATE users SET {set_clause} WHERE user_id = :id
                    RETURNING user_id, username, email, phone_number, company_name,
                    addressline1, addressline2, landmark, city, state, pincode, country;"""
        updates["id"] = user_id

        user = self.db.execute_query(query, params=updates, fetch_one=True, return_json=return_json)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def delete_user(self, user_id: str) -> None:
        """Delete a user"""
        query = "DELETE FROM users WHERE user_id = :user_id RETURNING user_id;"
        result = self.db.execute_query(query, params={"id": user_id}, fetch_one=False)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")

    def get_all_users(self, return_json: Optional[bool] = False) -> List[Dict]:
        """Fetch all users"""
        query = "SELECT * FROM users"
        return self.db.execute_query(query, return_json=return_json)
    
    def verify_user(self, email: str, password: str, return_json: bool=False) -> Dict:
        """Verify user credentials and return user ID if successful."""
        try:
            query = "SELECT * FROM users WHERE email = :email"
            user = self.db.execute_query(query, params={"email": email}, fetch_one=True, return_json=return_json)
            if user and self.verify_password(password, user['password']):
                return user
            
            raise HTTPException(
                status_code=500,
                detail="Invalid credentials"
            )
        
        except Exception as e:
            logging.error(f"Error verifying user: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to verify user credentials: {str(e)}"
            )

    # ====== Customer Management Methods ======

    def create_customer(
        self,
        user_id: str,
        customer_name: str,
        phone_number: Optional[str] = None,
        contact_info: Optional[str] = None,
        address: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Create a new customer"""
        customer_id = self.generate_uuid()
        query = """
        INSERT INTO customers (customer_id, user_id, customer_name, phone_number, contact_info, address)
        VALUES (:customer_id, :user_id, :customer_name, :phone_number, :contact_info, :address)
        RETURNING *;
        """
        params = {
            "customer_id": customer_id,
            "user_id": user_id,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "contact_info": contact_info,
            "address": address
        }
        customer = self.db.execute_query(query, params, fetch_one=True, return_json=return_json)
        if not customer:
            raise HTTPException(status_code=400, detail="Failed to create customer")
        return customer

    def get_customer(self, customer_id: str, return_json: Optional[bool] = False) -> Dict:
        """Retrieve a customer by ID"""
        query = "SELECT * FROM customers WHERE customer_id = :customer_id"
        customer = self.db.execute_query(query, params={"customer_id": customer_id}, fetch_one=True, return_json=return_json)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    def update_customer(
        self,
        customer_id: str,
        customer_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        contact_info: Optional[str] = None,
        address: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Update a customer's details"""
        updates = {}
        if customer_name: updates["customer_name"] = customer_name
        if phone_number: updates["phone_number"] = phone_number
        if contact_info: updates["contact_info"] = contact_info
        if address: updates["address"] = address

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
        query = f"UPDATE customers SET {set_clause} WHERE customer_id = :customer_id RETURNING *;"
        updates["customer_id"] = customer_id

        customer = self.db.execute_query(query, params=updates, fetch_one=True, return_json=return_json)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    def delete_customer(self, customer_id: str) -> None:
        """Delete a customer"""
        query = "DELETE FROM customers WHERE customer_id = :customer_id  RETURNING customer_id;"
        result = self.db.execute_query(query, params={"customer_id": customer_id}, fetch_one=True)
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")

    def get_all_customers(self, user_id: str, return_json: Optional[bool] = False) -> List[Dict]:
        """Fetch all customers for a user"""
        query = "SELECT * FROM customers WHERE user_id = :user_id"
        return self.db.execute_query(query, params={"user_id": user_id}, return_json=return_json)

    # ====== Product Management Methods ======

    def create_product(
        self,
        user_id: str,
        product: str,
        selling_price: float,
        mrp: float,
        quantity: int,
        weight: Optional[str] = None,
        batch_number: Optional[str] = None,
        expiry_date: Optional[date] = None,
        distributer_landing: Optional[float] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Create a new product"""
        product_id = self.generate_uuid()
        user = self.get_user(user_id, return_json=True)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = """
        INSERT INTO products (
            product_id, user_id, product, weight, batch_number, expiry_date, quantity,
            mrp, distributer_landing, selling_price
        )
        VALUES (
            :product_id, :user_id, :product, :weight, :batch_number, :expiry_date, :quantity,
            :mrp, :distributer_landing, :selling_price
        )
        RETURNING *;
        """
        params = {
            "product_id": product_id,
            "user_id": user_id,
            "product": product,
            "weight": weight,
            "batch_number": batch_number,
            "expiry_date": expiry_date,
            "quantity": quantity,
            "mrp": mrp,
            "distributer_landing": distributer_landing,
            "selling_price": selling_price
        }
        product = self.db.execute_query(query, params, fetch_one=True, return_json=return_json)
        return product
    
    def add_stock_entry(
        self,
        product_id: str,
        user_id: str,
        quantity: int,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Add stock to a product when new stock arrives"""
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity to add must be positive")

        # Check if product exists
        product = self.get_product(product_id, user_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update stock
        query = """
        UPDATE products 
        SET quantity = quantity + :quantity 
        WHERE product_id = :product_id AND user_id = :user_id 
        RETURNING *;
        """
        params = {
            "quantity": quantity,
            "product_id": product_id,
            "user_id": user_id
        }
        updated_product = self.db.execute_query(query, params, fetch_one=True, return_json=return_json)
        if not updated_product:
            raise HTTPException(status_code=500, detail="Failed to update stock")

        return updated_product

    def get_product(self, product_id: str, user_id: str, return_json: Optional[bool] = False) -> Dict:
        """Retrieve a product by ID and user_id"""
        query = "SELECT * FROM products WHERE product_id = :product_id AND user_id = :user_id"
        product = self.db.execute_query(query, params={"product_id": product_id, "user_id": user_id}, fetch_one=True, return_json=return_json)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def update_product(
        self,
        product_id: str,
        user_id: str,
        product: Optional[str] = None,
        weight: Optional[str] = None,
        batch_number: Optional[str] = None,
        expiry_date: Optional[date] = None,
        quantity: Optional[int] = None,
        mrp: Optional[float] = None,
        distributer_landing: Optional[float] = None,
        selling_price: Optional[float] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Update a product's details"""
        updates = {}
        if product: updates["product"] = product
        if weight: updates["weight"] = weight
        if batch_number: updates["batch_number"] = batch_number
        if expiry_date: updates["expiry_date"] = expiry_date
        if quantity is not None: updates["quantity"] = quantity
        if mrp is not None: updates["mrp"] = mrp
        if distributer_landing is not None: updates["distributer_landing"] = distributer_landing
        if selling_price is not None: updates["selling_price"] = selling_price

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
        query = f"UPDATE products SET {set_clause} WHERE product_id = :product_id AND user_id = :user_id RETURNING *;"
        updates.update({"product_id": product_id, "user_id": user_id})

        product = self.db.execute_query(query, params=updates, fetch_one=True, return_json=return_json)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def delete_product(self, product_id: str, user_id: str) -> None:
        """Delete a product"""
        query = "DELETE FROM products WHERE product_id = :product_id AND user_id = :user_id RETURNING product_id;"
        result = self.db.execute_query(query, params={"product_id": product_id, "user_id": user_id}, fetch_one=False)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")

    def get_all_products(self, user_id: str, return_json: Optional[bool] = False) -> List[Dict]:
        """Fetch all products for a user"""
        query = "SELECT * FROM products WHERE user_id = :user_id"
        return self.db.execute_query(query, params={"user_id": user_id}, return_json=return_json)

    # ====== Order Management Methods ======

    # def create_order(
    #     self,
    #     user_id: str,
    #     customer_id: str,
    #     orders: List[dict],  # List of order dictionaries
    #     created_by_name: Optional[str] = None,
    #     invoice_id: Optional[str] = None,
    #     return_json: Optional[bool] = False
    # ) -> List[Dict]:
    #     """
    #     Create one or more orders and update product quantities in a single transaction.
        
    #     Args:
    #         user_id (str): The ID of the user owning the orders.
    #         customer_id (str): The ID of the customer for whom the orders are placed.
    #         orders (List[dict]): List of orders, each containing product_id, customer_id, quantity, and rate.
    #         created_by_name (Optional[str]): Name of the person creating the orders.
    #         invoice_id (Optional[str]): ID of the associated invoice.
    #         return_json (Optional[bool]): Whether to return results as JSON-compatible dictionaries.
        
    #     Returns:
    #         List[Dict]: List of created order records.
    #     """
    #     order_results = []

    #     # Use a transaction to ensure atomicity
    #     for order_data in orders:
    #         order_id = self.generate_uuid()
    #         product_id = order_data["product_id"]
    #         quantity = order_data["quantity"]
    #         rate = order_data["rate"]
    #         amount = quantity * rate

    #         # Check product availability
    #         product = self.get_product(product_id, user_id)
    #         if product["quantity"] < quantity:
    #             raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product_id}")

    #         # Insert order
    #         query = """
    #         INSERT INTO orders (
    #             order_id, product_id, user_id, customer_id, created_by_name, invoice_id, quantity, rate, amount
    #         )
    #         VALUES (
    #             :order_id, :product_id, :user_id, :customer_id, :created_by_name, :invoice_id, :quantity, :rate, :amount
    #         )
    #         RETURNING *;
    #         """
    #         params = {
    #             "order_id": order_id,
    #             "product_id": product_id,
    #             "user_id": user_id,
    #             "customer_id": customer_id,
    #             "created_by_name": created_by_name,
    #             "invoice_id": invoice_id,
    #             "quantity": quantity,
    #             "rate": rate,
    #             "amount": amount
    #         }
    #         order = self.db.execute_query(query, params, fetch_one=True, return_data=return_json)
    #         order_results.append(order)

    #         # Update product stock
    #         update_query = """
    #         UPDATE products 
    #         SET quantity = quantity - :quantity 
    #         WHERE product_id = :product_id AND user_id = :user_id
    #         """
    #         self.db.execute_query(update_query, {"quantity": quantity, "product_id": product_id, "user_id": user_id})

    #     return order_results

    def create_order(
        self,
        user_id: str,
        customer_id: str,
        orders: List[dict],
        invoice_number: str,
        created_by_name: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Create an invoice and associated orders in a single transaction"""
        invoice_id = self.generate_uuid()
        order_results = []
        total_amount = 0.0

        with self.db.engine.begin() as conn:
            # Step 1: Insert the invoice first with a temporary total_amount
            invoice_query = """
            INSERT INTO invoices (
                invoice_id, user_id, customer_id, invoice_number, total_amount, created_by_name
            )
            VALUES (
                :invoice_id, :user_id, :customer_id, :invoice_number, :total_amount, :created_by_name
            )
            RETURNING *;
            """
            invoice_params = {
                "invoice_id": invoice_id,
                "user_id": user_id,
                "customer_id": customer_id,
                "invoice_number": invoice_number,
                "total_amount": 0.0,  # Temporary value, updated later
                "created_by_name": created_by_name
            }
            invoice = conn.execute(text(invoice_query), invoice_params).fetchone()
            invoice_result = dict(invoice._mapping) if return_json else invoice

            # Step 2: Process orders
            for order_data in orders:
                order_id = self.generate_uuid()
                product_id = order_data["product_id"]
                quantity = order_data["quantity"]
                rate = order_data["rate"]
                amount = quantity * rate
                total_amount += amount

                product = self.get_product(product_id, user_id, return_json=True)
                if product["quantity"] < quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product_id}")

                order_query = """
                INSERT INTO orders (
                    order_id, product_id, user_id, customer_id, created_by_name, invoice_id, quantity, rate, amount
                )
                VALUES (
                    :order_id, :product_id, :user_id, :customer_id, :created_by_name, :invoice_id, :quantity, :rate, :amount
                )
                RETURNING *;
                """
                order_params = {
                    "order_id": order_id,
                    "product_id": product_id,
                    "user_id": user_id,
                    "customer_id": customer_id,
                    "created_by_name": created_by_name,
                    "invoice_id": invoice_id,
                    "quantity": quantity,
                    "rate": rate,
                    "amount": amount
                }
                order = conn.execute(text(order_query), order_params).fetchone()
                order_results.append(dict(order._mapping) if return_json else order)

                stock_query = """
                UPDATE products 
                SET quantity = quantity - :quantity 
                WHERE product_id = :product_id AND user_id = :user_id
                """
                conn.execute(text(stock_query), {"quantity": quantity, "product_id": product_id, "user_id": user_id})

            # Step 3: Update the invoice with the calculated total_amount
            update_invoice_query = """
            UPDATE invoices 
            SET total_amount = :total_amount 
            WHERE invoice_id = :invoice_id
            RETURNING *;
            """
            invoice_params = {
                "invoice_id": invoice_id,
                "total_amount": total_amount
            }
            invoice = conn.execute(text(update_invoice_query), invoice_params).fetchone()
            invoice_result = dict(invoice._mapping) if return_json else invoice

        invoice_result["orders"] = order_results
        return invoice_result

    
    def get_invoice(self, invoice_number: str, return_json: Optional[bool] = False) -> Dict:
        """Retrieve an invoice by invoice_number"""
        query = "SELECT * FROM invoices WHERE invoice_number = :invoice_number"
        invoice = self.db.execute_query(query, params={"invoice_number": invoice_number}, fetch_one=True, return_json=return_json)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    


    def get_invoice_orders(self, invoice_id: str, return_json: Optional[bool] = False) -> List[Dict]:
        """Retrieve all orders for an invoice by invoice_id"""
        query = "SELECT * FROM orders WHERE invoice_id = :invoice_id"
        return self.db.execute_query(query, params={"invoice_id": invoice_id}, return_json=return_json)
    

    
    def get_order(self, order_id: str, user_id: str, return_json: Optional[bool] = False) -> Dict:
        """Retrieve an order by ID and user_id"""
        query = "SELECT * FROM orders WHERE order_id = :order_id AND user_id = :user_id"
        order = self.db.execute_query(query, params={"order_id": order_id, "user_id": user_id}, fetch_one=True, return_json=return_json)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    

    def update_order(
        self,
        order_id: str,
        user_id: str,
        quantity: Optional[int] = None,
        rate: Optional[float] = None,
        customer_id: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Update an order, adjust stock if quantity changes, and update the associated invoice's total_amount"""
        # Fetch the original order
        order = self.get_order(order_id, user_id, return_json=True)
        original_quantity = order["quantity"]
        invoice_id = order.get("invoice_id")  # Check if the order is linked to an invoice

        # Build updates for the order
        updates = {}
        if quantity is not None: updates["quantity"] = quantity
        if rate is not None: updates["rate"] = rate
        if customer_id: updates["customer_id"] = customer_id

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Recalculate amount if quantity or rate changes
        if "quantity" in updates or "rate" in updates:
            updates["amount"] = (updates.get("quantity", original_quantity)) * (updates.get("rate", order["rate"]))

        # Use a transaction to ensure atomicity across orders, products, and invoices
        with self.db.engine.begin() as conn:
            # Update the order
            set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
            query = f"UPDATE orders SET {set_clause} WHERE order_id = :order_id AND user_id = :user_id RETURNING *;"
            updates.update({"order_id": order_id, "user_id": user_id})
            updated_order = conn.execute(text(query), updates).fetchone()
            if not updated_order:
                raise HTTPException(status_code=404, detail="Order not found")
            updated_order_dict = dict(updated_order._mapping) if return_json else updated_order
            # Adjust stock if quantity changed
            if quantity is not None and quantity != original_quantity:
                stock_adjustment = original_quantity - quantity  # Positive if reducing, negative if increasing
                product_query = """
                UPDATE products 
                SET quantity = quantity + :stock_adjustment 
                WHERE product_id = :product_id AND user_id = :user_id
                """
                conn.execute(text(product_query), {
                    "stock_adjustment": stock_adjustment,
                    "product_id": order["product_id"],
                    "user_id": user_id
                })

            # Update the invoice's total_amount if linked
            if invoice_id:
                # Recalculate total_amount by summing all order amounts for this invoice
                total_amount_query = """
                SELECT SUM(amount) as total_amount 
                FROM orders 
                WHERE invoice_id = :invoice_id
                """
                total_amount_result = conn.execute(text(total_amount_query), {"invoice_id": invoice_id}).fetchone()
                total_amount_result = dict(total_amount_result._mapping) if return_json else total_amount_result
                new_total_amount = total_amount_result["total_amount"] if total_amount_result else 0.0
                # Update the invoice
                invoice_query = """
                UPDATE invoices 
                SET total_amount = :total_amount 
                WHERE invoice_id = :invoice_id
                RETURNING *;
                """
                conn.execute(text(invoice_query), {
                    "total_amount": new_total_amount,
                    "invoice_id": invoice_id
                })

        return updated_order_dict
    


    def delete_order(self, order_id: str, user_id: str) -> None:
        """Delete an order and restore stock"""
        order = self.get_order(order_id, user_id, return_json=True)
        query = "DELETE FROM orders WHERE order_id = :order_id AND user_id = :user_id RETURNING order_id;"
        result = self.db.execute_query(query, params={"order_id": order_id, "user_id": user_id}, fetch_one=True, return_json=True)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Restore stock
        restore_query = """
        UPDATE products 
        SET quantity = quantity + :quantity 
        WHERE product_id = :product_id AND user_id = :user_id
        """
        self.db.execute_query(restore_query, params={
            "quantity": order["quantity"],
            "product_id": order["product_id"],
            "user_id": user_id
        })

    
    def delete_invoice(self, user_id: str, invoice_id: str, return_json: Optional[bool] = False) -> None:
        """Delete an invoice, let CASCADE delete orders, and restore stock"""
        with self.db.engine.begin() as conn:
            # Fetch orders to restore stock before deletion
            orders_query = """
            SELECT product_id, quantity 
            FROM orders 
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            """
            orders = conn.execute(text(orders_query), {"invoice_id": invoice_id, "user_id": user_id}).fetchall()
            # Delete the invoice (CASCADE will delete orders)
            delete_query = """
            DELETE FROM invoices 
            WHERE invoice_id = :invoice_id AND user_id = :user_id 
            RETURNING *;
            """
            invoice = conn.execute(text(delete_query), {"invoice_id": invoice_id, "user_id": user_id}).fetchone()
            if not invoice and not orders:
                raise HTTPException(status_code=404, detail="Invoice not found")

            # Restore stock for all affected products
            for order in orders:
                order = dict(order._mapping) if return_json else order
                restore_stock_query = """
                UPDATE products 
                SET quantity = quantity + :quantity 
                WHERE product_id = :product_id AND user_id = :user_id
                """
                conn.execute(text(restore_stock_query), {
                    "quantity": order["quantity"],
                    "product_id": order["product_id"],
                    "user_id": user_id
                })


    def get_all_orders(self, user_id: str, return_json: Optional[bool] = False) -> List[Dict]:
        """Fetch all orders for a user"""
        query = "SELECT * FROM orders WHERE user_id = :user_id"
        return self.db.execute_query(query, params={"user_id": user_id}, return_json=return_json)
    

    def create_payment(
        self,
        user_id: str,
        invoice_id: str,
        amount: float,
        payment_method: Optional[str] = None,
        note: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Add a payment to an invoice and update its status and amount paid"""
        payment_id = self.generate_uuid()

        with self.db.engine.begin() as conn:
            # Step 1: Insert the payment
            payment_query = """
            INSERT INTO payments (
                payment_id, invoice_id, user_id, amount, payment_method, note
            )
            VALUES (
                :payment_id, :invoice_id, :user_id, :amount, :payment_method, :note
            )
            RETURNING *;
            """
            payment_params = {
                "payment_id": payment_id,
                "invoice_id": invoice_id,
                "user_id": user_id,
                "amount": amount,
                "payment_method": payment_method,
                "note": note
            }
            payment = conn.execute(text(payment_query), payment_params).fetchone()
            payment_result = dict(payment._mapping) if return_json else payment

            # Step 2: Calculate total paid from payments table
            total_paid_query = """
            SELECT SUM(amount) as total_paid
            FROM payments
            WHERE invoice_id = :invoice_id
            """
            total_paid_result = conn.execute(text(total_paid_query), {"invoice_id": invoice_id}).fetchone()
            total_paid_result = dict(total_paid_result._mapping) if return_json else total_paid_result
            total_paid = total_paid_result["total_paid"] if total_paid_result["total_paid"] is not None else 0.0

            # Step 3: Fetch invoice details
            invoice_query = """
            SELECT total_amount
            FROM invoices
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            """
            invoice = conn.execute(text(invoice_query), {"invoice_id": invoice_id, "user_id": user_id}).fetchone()
            invoice = dict(invoice._mapping) if return_json else invoice
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            total_amount = invoice["total_amount"]

            # Step 4: Determine payment status
            payment_status = (
                "fully_paid" if total_paid >= total_amount else
                "partially_paid" if total_paid > 0 else
                "pending"
            )

            # Step 5: Update invoice with total paid and status
            update_invoice_query = """
            UPDATE invoices
            SET payment_status = :payment_status,
                amount_paid = :total_paid
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            RETURNING *;
            """
            updated_invoice = conn.execute(
                text(update_invoice_query),
                {"payment_status": payment_status, "total_paid": total_paid, "invoice_id": invoice_id, "user_id": user_id}
            ).fetchone()
            invoice_result = dict(updated_invoice._mapping) if return_json else updated_invoice

        # Return payment details and updated invoice
        return {
            "payment": payment_result,
            "invoice": invoice_result
        }
    
    def get_payment(
        self,
        payment_id: str,
        user_id: str,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Retrieve a payment by ID"""
        query = """
        SELECT *
        FROM payments
        WHERE payment_id = :payment_id AND user_id = :user_id
        """
        payment = self.db.execute_query(query, params={"payment_id": payment_id, "user_id": user_id}, fetch_one=True, return_json=return_json)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment


    def get_payments_by_invoice(
        self,
        invoice_id: str,
        user_id: str,
        return_json: Optional[bool] = False
    ) -> List[Dict]:
        """Retrieve all payments for an invoice"""
        query = """
        SELECT *
        FROM payments
        WHERE invoice_id = :invoice_id AND user_id = :user_id
        """
        payments = self.db.execute_query(query, params={"invoice_id": invoice_id, "user_id": user_id}, return_json=return_json)
        return payments


    def update_payment(
        self,
        payment_id: str,
        user_id: str,
        amount: Optional[float] = None,
        payment_method: Optional[str] = None,
        note: Optional[str] = None,
        return_json: Optional[bool] = False
    ) -> Dict:
        """Update a payment and adjust the associated invoice"""
        payment = self.get_payment(payment_id, user_id, return_json=True)
        invoice_id = payment["invoice_id"]

        updates = {}
        if amount is not None: updates["amount"] = amount
        if payment_method is not None: updates["payment_method"] = payment_method
        if note is not None: updates["note"] = note

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        with self.db.engine.begin() as conn:
            # Update payment
            set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
            query = f"""
            UPDATE payments
            SET {set_clause}
            WHERE payment_id = :payment_id AND user_id = :user_id
            RETURNING *;
            """
            updates.update({"payment_id": payment_id, "user_id": user_id})
            updated_payment = conn.execute(text(query), updates).fetchone()
            if not updated_payment:
                raise HTTPException(status_code=404, detail="Payment not found")
            payment_result = dict(updated_payment._mapping) if return_json else updated_payment

            # Recalculate total paid and update invoice
            total_paid_query = """
            SELECT SUM(amount) as total_paid
            FROM payments
            WHERE invoice_id = :invoice_id
            """
            total_paid_result = conn.execute(text(total_paid_query), {"invoice_id": invoice_id}).fetchone()
            total_paid_result = dict(total_paid_result._mapping) if return_json else total_paid_result
            total_paid = total_paid_result["total_paid"] if total_paid_result["total_paid"] is not None else 0.0

            invoice_query = """
            SELECT total_amount
            FROM invoices
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            """
            invoice = conn.execute(text(invoice_query), {"invoice_id": invoice_id, "user_id": user_id}).fetchone()
            invoice = dict(invoice._mapping) if return_json else invoice
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            total_amount = invoice["total_amount"]

            payment_status = (
                "fully_paid" if total_paid >= total_amount else
                "partially_paid" if total_paid > 0 else
                "pending"
            )

            update_invoice_query = """
            UPDATE invoices
            SET amount_paid = :total_paid, payment_status = :payment_status
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            RETURNING *;
            """
            conn.execute(text(update_invoice_query), {
                "total_paid": total_paid,
                "payment_status": payment_status,
                "invoice_id": invoice_id,
                "user_id": user_id
            })

        return payment_result
    
    
    def delete_payment(
        self,
        payment_id: str,
        user_id: str,
        return_json: Optional[bool] = False
    ) -> None:
        """Delete a payment and adjust the associated invoice"""
        payment = self.get_payment(payment_id, user_id, return_json=True)
        invoice_id = payment["invoice_id"]

        with self.db.engine.begin() as conn:
            # Delete payment
            delete_query = """
            DELETE FROM payments
            WHERE payment_id = :payment_id AND user_id = :user_id
            RETURNING *;
            """
            result = conn.execute(text(delete_query), {"payment_id": payment_id, "user_id": user_id}).fetchone()
            result = dict(result._mapping) if return_json else result
            if not result:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Recalculate total paid and update invoice
            total_paid_query = """
            SELECT SUM(amount) as total_paid
            FROM payments
            WHERE invoice_id = :invoice_id
            """
            total_paid_result = conn.execute(text(total_paid_query), {"invoice_id": invoice_id}).fetchone()
            total_paid_result = dict(total_paid_result._mapping) if return_json else total_paid_result
            total_paid = total_paid_result["total_paid"] if total_paid_result["total_paid"] is not None else 0.0

            invoice_query = """
            SELECT total_amount
            FROM invoices
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            """
            invoice = conn.execute(text(invoice_query), {"invoice_id": invoice_id, "user_id": user_id}).fetchone()
            invoice = dict(invoice._mapping) if return_json else invoice
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            total_amount = invoice["total_amount"]

            payment_status = (
                "fully_paid" if total_paid >= total_amount else
                "partially_paid" if total_paid > 0 else
                "pending"
            )

            update_invoice_query = """
            UPDATE invoices
            SET amount_paid = :total_paid, payment_status = :payment_status
            WHERE invoice_id = :invoice_id AND user_id = :user_id
            RETURNING *;
            """
            conn.execute(text(update_invoice_query), {
                "total_paid": total_paid,
                "payment_status": payment_status,
                "invoice_id": invoice_id,
                "user_id": user_id
            })