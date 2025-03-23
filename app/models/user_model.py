from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import re

class UserCreateModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Unique username")
    password: str = Field(..., min_length=1, max_length=255, description="User password")
    email: Optional[EmailStr] = Field(None, max_length=100, description="User email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="User phone number")
    company_name: str = Field(..., min_length=1, max_length=100, description="Company name")
    addressline1: str = Field(..., min_length=1, max_length=100, description="Primary address line")
    addressline2: Optional[str] = Field(None, max_length=100, description="Secondary address line")
    landmark: Optional[str] = Field(None, max_length=100, description="Nearby landmark")
    city: str = Field(..., min_length=1, max_length=50, description="City")
    state: str = Field(..., min_length=1, max_length=50, description="State")
    pincode: str = Field(..., min_length=1, max_length=10, description="Postal code")
    country: str = Field(..., min_length=1, max_length=50, description="Country")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepass123",
                "email": "john.doe@example.com",
                "phone_number": "123-456-7890",
                "company_name": "ABC Trading",
                "addressline1": "123 Main St",
                "addressline2": "Apt 4B",
                "landmark": "Near Central Park",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "country": "India"
            }
        }

class UserUpdateModel(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique username")
    password: Optional[str] = Field(None, min_length=1, max_length=255, description="User password")
    email: Optional[EmailStr] = Field(None, max_length=100, description="User email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="User phone number")
    company_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Company name")
    addressline1: Optional[str] = Field(None, min_length=1, max_length=100, description="Primary address line")
    addressline2: Optional[str] = Field(None, max_length=100, description="Secondary address line")
    landmark: Optional[str] = Field(None, max_length=100, description="Nearby landmark")
    city: Optional[str] = Field(None, min_length=1, max_length=50, description="City")
    state: Optional[str] = Field(None, min_length=1, max_length=50, description="State")
    pincode: Optional[str] = Field(None, min_length=1, max_length=10, description="Postal code")
    country: Optional[str] = Field(None, min_length=1, max_length=50, description="Country")

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "987-654-3210",
                "addressline1": "456 New St",
                "addressline2": "Apt 2C",
                "landmark": "Near Times Square",
                "city": "New York",
                "state": "New York",
                "pincode": "10001",
                "country": "United States"
            }
        }

class UserLoginRequestModel(BaseModel):
    email: str = Field(..., min_length=1, max_length=50, description="Unique email")
    password: str = Field(..., min_length=1, max_length=255, description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepass123"
            }
        }