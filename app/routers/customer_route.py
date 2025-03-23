import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.controllers.database_controller import DatabaseController
from app.models.response_model import ResponseModel
from app.models.customer_model import CustomerCreateModel, CustomerUpdateModel 
from threading import Lock
from app.utils.utility_manager import UtilityManager

class CustomerRouter(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: CustomerRouter:-----")
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(CustomerRouter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"):  # Prevent reinitialization
            self.customer_manager = DatabaseController()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routes()

    def setup_routes(self):
        @self.router.post(RoutePaths.CUSTOMER, tags=[RouteTags.CUSTOMER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_customer(customer: CustomerCreateModel):
            """Create a new customer"""
            customer_data = self.customer_manager.create_customer(
                user_id=customer.user_id,
                customer_name=customer.customer_name,
                phone_number=customer.phone_number,
                contact_info=customer.contact_info,
                address=customer.address,
                return_json=True
            )
            return ResponseModel(
                message="Customer Created Successfully",
                data=customer_data
            )

        @self.router.get(RoutePaths.CUSTOMER, tags=[RouteTags.CUSTOMER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_all_customers(user_id: str):
            """Get all customers for a user"""
            customers = self.customer_manager.get_all_customers(user_id=user_id, return_json=True)
            return ResponseModel(
                message="Customers Fetched Successfully",
                data=customers
            )

        @self.router.get(RoutePaths.CUSTOMER_WITH_ID, tags=[RouteTags.CUSTOMER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_customer(customer_id: str):
            """Get a single customer by ID"""
            customer = self.customer_manager.get_customer(customer_id=customer_id, return_json=True)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            return ResponseModel(
                message="Customer found",
                data=customer
            )

        @self.router.put(RoutePaths.CUSTOMER_WITH_ID, tags=[RouteTags.CUSTOMER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def update_customer(customer_id: str, customer_update: CustomerUpdateModel):
            """Update a customer"""
            updated_customer = self.customer_manager.update_customer(
                customer_id=customer_id,
                customer_name=customer_update.customer_name,
                phone_number=customer_update.phone_number,
                contact_info=customer_update.contact_info,
                address=customer_update.address,
                return_json=True
            )
            return ResponseModel(
                message="Customer updated successfully",
                data={
                    "customer_id": customer_id,
                    "response": updated_customer
                }
            )

        @self.router.delete(RoutePaths.CUSTOMER_WITH_ID, tags=[RouteTags.CUSTOMER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def delete_customer(customer_id: str):
            """Delete a customer"""
            self.customer_manager.delete_customer(customer_id=customer_id)
            return ResponseModel(
                message="Customer deleted successfully",
                data={"customer_id": customer_id}
            )