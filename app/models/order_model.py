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
                "customer_id": "cust-456",
                "quantity": 10,
                "rate": 25.99
            }
        }

class OrderCreateModel(BaseModel):
    orders: List[SingleOrderCreateModel] = Field(..., min_items=1, description="List of orders to create")
    created_by_name: Optional[str] = Field(None, max_length=100, description="Name of the person creating the orders")
    invoice_id: Optional[str] = Field(None, max_length=50, description="ID of the associated invoice")
    customer_id: str = Field(..., max_length=50, description="ID of the customer")

    class Config:
        json_schema_extra = {
            "example": {
                "orders": [
                    {
                        "product_id": "prod-123",
                        "quantity": 10,
                        "rate": 25.99
                    },
                    {
                        "product_id": "prod-456",
                        "quantity": 5,
                        "rate": 19.99
                    }
                ],
                "created_by_name": "John Doe",
                "invoice_id": "inv-789",
                "customer_id": "cust-456"
            }
        }

class OrderUpdateModel(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, description="Updated quantity ordered")
    rate: Optional[float] = Field(None, gt=0, description="Updated rate per unit")
    customer_id: Optional[str] = Field(None, max_length=50, description="Updated customer ID")

    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 15,
                "rate": 27.99,
                "customer_id": "cust-789"
            }
        }

