import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.controllers.database_controller import DatabaseController
from app.models.response_model import ResponseModel
from app.models.payment_model import PaymentCreateModel, PaymentUpdateModel
from threading import Lock
from app.utils.utility_manager import UtilityManager
from datetime import date
from typing import Optional


class PaymentRouter(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: PaymentRouters:-----")
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(PaymentRouter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"):  # Prevent reinitialization
            self.payment_manager = DatabaseController()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routes()


    def setup_routes(self):
        # GET /payments/{payment_id} - Retrieve a specific payment
        @self.router.get(RoutePaths.PAYMENT_WITH_ID, tags=[RouteTags.PAYMENT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_payment(payment_id: str, user_id: str):
            """Retrieve a payment by ID"""
            payment = self.payment_manager.get_payment(
                payment_id=payment_id,
                user_id=user_id,
                return_json=True
            )
            return ResponseModel(
                message="Payment Retrieved Successfully",
                data=payment
            )
        
    # GET /invoices/{invoice_id}/payments - Retrieve all payments for an invoice
        @self.router.get(RoutePaths.PAYMENT_BY_INVOICE, tags=[RouteTags.PAYMENT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_payments_by_invoice(invoice_id: str, user_id: str):
            """Retrieve all payments for an invoice"""
            payments = self.payment_manager.get_payments_by_invoice(
                invoice_id=invoice_id,
                user_id=user_id,
                return_json=True
            )
            return ResponseModel(
                message="Payments Retrieved Successfully",
                data=payments
            )
        

        # POST /invoices/{invoice_id}/payments - Create a new payment
        @self.router.post(RoutePaths.PAYMENT_BY_INVOICE, tags=[RouteTags.PAYMENT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_payment(invoice_id: str, user_id: str, payment: PaymentCreateModel):
            """Add a payment to an invoice"""
            payment_data = self.payment_manager.create_payment(
                user_id=user_id,
                invoice_id=invoice_id,
                amount=payment.amount,
                payment_method=payment.payment_method,
                note=payment.note,
                return_json=True
            )
            return ResponseModel(
                message="Payment Added Successfully",
                data=payment_data
            )
        
        # PUT /payments/{payment_id} - Update an existing payment
        @self.router.put(RoutePaths.PAYMENT_WITH_ID, tags=[RouteTags.PAYMENT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def update_payment(payment_id: str, user_id: str, payment: PaymentUpdateModel):
            """Update a payment"""
            updated_payment = self.payment_manager.update_payment(
                payment_id=payment_id,
                user_id=user_id,
                amount=payment.amount,
                payment_method=payment.payment_method,
                note=payment.note,
                return_json=True
            )
            return ResponseModel(
                message="Payment Updated Successfully",
                data=updated_payment
            )
        
        # DELETE /payments/{payment_id} - Delete a payment
        @self.router.delete(RoutePaths.PAYMENT_WITH_ID, tags=[RouteTags.PAYMENT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def delete_payment(payment_id: str, user_id: str):
            """Delete a payment"""
            self.payment_manager.delete_payment(
                payment_id=payment_id,
                user_id=user_id,
                return_json=True
            )
            return ResponseModel(
                message="Payment Deleted Successfully",
                data={"payment_id": payment_id}
            )