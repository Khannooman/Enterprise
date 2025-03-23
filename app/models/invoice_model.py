from pydantic import BaseModel, Field
from typing import Optional, List

class SingleOrderCreateModel(BaseModel):
    product_id: str = Field(..., max_length=50, description="ID of the product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    rate: float = Field(..., gt=0, description="Rate per unit")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod-123",
                "quantity": 10,
                "rate": 25.99
            }
        }

class InvoiceWithOrdersCreateModel(BaseModel):
    customer_id: str = Field(..., max_length=50, description="ID of the customer")
    invoice_number: str = Field(..., max_length=50, description="Unique invoice number (e.g., ER7K9P2MX4)")
    orders: List[SingleOrderCreateModel] = Field(..., min_items=1, description="List of orders to create")
    created_by_name: Optional[str] = Field(None, max_length=100, description="Name of the person creating the invoice and orders")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust-456",
                "invoice_number": "ER7K9P2MX4",
                "orders": [
                    {"product_id": "prod-123", "quantity": 10, "rate": 25.99},
                    {"product_id": "prod-456", "quantity": 5, "rate": 19.99}
                ],
                "created_by_name": "John Doe"
            }
        }