from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ProductCreateModel(BaseModel):
    user_id: str = Field(..., max_length=50, description="ID of the user creating the product")
    product: str = Field(..., min_length=1, max_length=100, description="Product name")
    selling_price: float = Field(..., gt=0, description="Selling price of the product")
    mrp: float = Field(..., gt=0, description="Maximum retail price")
    quantity: int = Field(..., ge=0, description="Initial quantity in stock")
    weight: Optional[str] = Field(None, max_length=50, description="Weight of the product")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch number")
    expiry_date: Optional[date] = Field(None, description="Expiry date of the product")
    distributer_landing: Optional[float] = Field(None, ge=0, description="Distributor landing price")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "product": "Widget A",
                "selling_price": 25.99,
                "mrp": 29.99,
                "quantity": 100,
                "weight": "500g",
                "batch_number": "B12345",
                "expiry_date": "2025-12-31",
                "distributer_landing": 20.50
            }
        }

class ProductUpdateModel(BaseModel):
    product: Optional[str] = Field(None, min_length=1, max_length=100, description="Product name")
    weight: Optional[str] = Field(None, max_length=50, description="Weight of the product")
    batch_number: Optional[str] = Field(None, max_length=50, description="Batch number")
    expiry_date: Optional[date] = Field(None, description="Expiry date of the product")
    quantity: Optional[int] = Field(None, ge=0, description="Quantity in stock")
    mrp: Optional[float] = Field(None, gt=0, description="Maximum retail price")
    distributer_landing: Optional[float] = Field(None, ge=0, description="Distributor landing price")
    selling_price: Optional[float] = Field(None, gt=0, description="Selling price of the product")

    class Config:
        json_schema_extra = {
            "example": {
                "product": "Widget A Updated",
                "selling_price": 27.99,
                "quantity": 150
            }
        }