from pydantic import BaseModel, Field
from typing import Optional

class CustomerCreateModel(BaseModel):
    user_id: str = Field(..., max_length=50, description="ID of the user creating the customer")
    customer_name: str = Field(..., min_length=1, max_length=100, description="Name of the customer")
    phone_number: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    contact_info: Optional[str] = Field(None, max_length=100, description="Additional contact information")
    address: Optional[str] = Field(None, description="Customer address")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "customer_name": "Jane Smith",
                "phone_number": "987-654-3210",
                "contact_info": "jane.smith@example.com",
                "address": "456 Oak St, Springfield"
            }
        }

class CustomerUpdateModel(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the customer")
    phone_number: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    contact_info: Optional[str] = Field(None, max_length=100, description="Additional contact information")
    address: Optional[str] = Field(None, description="Customer address")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Jane Smith Updated",
                "phone_number": "555-555-5555",
                "address": "789 Pine St, Springfield"
            }
        }


