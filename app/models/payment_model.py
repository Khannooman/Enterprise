from pydantic import BaseModel, Field
from typing import Optional


class PaymentCreateModel(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: Optional[str] = Field(None, max_length=50, description="Method of payment (e.g., cash, credit_card)")
    note: Optional[str] = Field(None, description="Additional notes about the payment")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.00,
                "payment_method": "cash",
                "note": "Initial payment"
            }
        }

class PaymentUpdateModel(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Updated payment amount")
    payment_method: Optional[str] = Field(None, max_length=50, description="Updated method of payment")
    note: Optional[str] = Field(None, max_length=255, description="Updated notes about the payment")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 150.00,
                "payment_method": "bank_transfer",
                "note": "Updated payment"
            }
        }

