import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.controllers.database_controller import DatabaseController
from app.models.response_model import ResponseModel
from app.models.order_model import OrderCreateModel, OrderUpdateModel
from app.models.invoice_model import InvoiceWithOrdersCreateModel
from threading import Lock
from app.utils.utility_manager import UtilityManager
from datetime import date
from typing import Optional

class OrderRouter(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: OrderRouter:-----")
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(OrderRouter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"):  # Prevent reinitialization
            self.order_manager = DatabaseController()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routes()

    def setup_routes(self):
    #     @self.router.post(RoutePaths.ORDER, tags=[RouteTags.ORDER], response_model=ResponseModel)
    #     @self.catch_api_exceptions
    #     async def create_order(user_id: str, order: OrderCreateModel):
    #         """Create multiple orders in a single request"""
    #         orders_list = [order.dict() for order in order.orders]
    #         order_data = self.order_manager.create_order(
    #             user_id=user_id,
    #             customer_id=order.customer_id,
    #             orders=orders_list,
    #             created_by_name=order.created_by_name,
    #             invoice_id=order.invoice_id,
    #             return_json=True
    #         )
    #         return ResponseModel(
    #             message="Orders Created Successfully",
    #             data=order_data
    #         )

        @self.router.post(RoutePaths.ORDER, tags=[RouteTags.ORDER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_order(user_id: str, invoice: InvoiceWithOrdersCreateModel):
            """Create an invoice and associated orders in a single transaction"""
            orders_list = [order.dict() for order in invoice.orders]
            invoice_data = self.order_manager.create_order(
                user_id=user_id,
                customer_id=invoice.customer_id,
                orders=orders_list,
                invoice_number=invoice.invoice_number,
                created_by_name=invoice.created_by_name,
                return_json=True
            )
            return ResponseModel(
                message="Invoice and Orders Created Successfully",
                data=invoice_data
            )

        @self.router.get(RoutePaths.ORDER, tags=[RouteTags.ORDER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_all_orders(user_id: str):
            """Get all orders for a user"""
            orders = self.order_manager.get_all_orders(user_id=user_id, return_json=True)
            return ResponseModel(
                message="Orders Fetched Successfully",
                data=orders
            )

        @self.router.get(RoutePaths.ORDER_WITH_ID, tags=[RouteTags.ORDER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_order(order_id: str, user_id: str):
            """Get a single order by ID and user_id"""
            order = self.order_manager.get_order(order_id=order_id, user_id=user_id, return_json=True)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            return ResponseModel(
                message="Order found",
                data=order
            )

        @self.router.put(RoutePaths.ORDER_WITH_ID, tags=[RouteTags.ORDER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def update_order(order_id: str, user_id: str, order: OrderUpdateModel):
            """Update an order and adjust associated invoice if applicable"""
            updated_order = self.order_manager.update_order(
                order_id=order_id,
                user_id=user_id,
                quantity=order.quantity,
                rate=order.rate,
                customer_id=order.customer_id,
                return_json=True
            )
            return ResponseModel(
                message="Order Updated Successfully",
                data=updated_order
            )

        @self.router.delete(RoutePaths.ORDER_WITH_ID, tags=[RouteTags.ORDER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def delete_order(order_id: str, user_id: str):
            """Delete an order"""
            self.order_manager.delete_order(order_id=order_id, user_id=user_id)
            return ResponseModel(
                message="Order deleted successfully",
                data={"order_id": order_id, "user_id": user_id}
            )

        # @self.router.get(RoutePaths.ORDER_BY_CUSTOMER, tags=[RouteTags.ORDER], response_model=ResponseModel)
        # @self.catch_api_exceptions
        # async def get_orders_by_customer(customer_id: str):
        #     """Get all orders for a customer"""
        #     orders = self.order_manager.get_orders_by_customer(customer_id=customer_id, return_json=True)
        #     return ResponseModel(
        #         message="Customer Orders Fetched Successfully",
        #         data=orders
        #     )
        
       

        @self.router.get(RoutePaths.INVOICE_BY_NUMBER, tags=[RouteTags.INVOICE], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_invoice(invoice_number: str):
            """Get an invoice by invoice_number with its orders"""
            invoice = self.order_manager.get_invoice(invoice_number=invoice_number, return_json=True)
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            invoice_id = invoice["invoice_id"]
            return ResponseModel(
                message="Invoice Retrieved Successfully",
                data=invoice
            )

        @self.router.get(RoutePaths.INVOICE_ORDERS, tags=[RouteTags.INVOICE], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_invoice_orders(invoice_number: str):
            """Get all orders for an invoice by invoice_number"""
            invoice = self.order_manager.get_invoice(invoice_number=invoice_number, return_json=True)
            if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")
            invoice_id = invoice["invoice_id"]
            orders = self.order_manager.get_invoice_orders(invoice_id=invoice_id, return_json=True)
            return ResponseModel(
                message="Invoice Orders Retrieved Successfully",
                data=orders
            )
        @self.router.delete(RoutePaths.INVOICE_WITH_ID, tags=[RouteTags.INVOICE], response_model=ResponseModel)
        @self.catch_api_exceptions 
        async def delete_invoice(invoice_id: str, user_id: str):
            """Delete an invoice by invoice_number"""
            self.order_manager.delete_invoice(invoice_id=invoice_id, user_id=user_id, return_json=True)
            return ResponseModel(
                message="Invoice deleted successfully",
                data={
                    "invoice_id": invoice_id,
                    "user_id": user_id
                    }
            )