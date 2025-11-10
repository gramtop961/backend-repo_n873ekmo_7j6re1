"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Toy selling app schemas

class Toy(BaseModel):
    """
    Toy products
    Collection name: "toy"
    """
    name: str = Field(..., description="Toy name")
    description: Optional[str] = Field(None, description="Toy description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category, e.g., Plush, Puzzles, STEM")
    image: Optional[str] = Field(None, description="Image URL")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")
    in_stock: bool = Field(True, description="Availability")

class OrderItem(BaseModel):
    toy_id: str = Field(..., description="Referenced toy _id as string")
    name: str = Field(..., description="Toy name (denormalized for convenience)")
    price: float = Field(..., ge=0, description="Unit price at purchase time")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    image: Optional[str] = None

class Order(BaseModel):
    """
    Orders collection
    Collection name: "order"
    """
    customer_name: str = Field(...)
    customer_email: EmailStr = Field(...)
    customer_address: str = Field(...)
    items: List[OrderItem] = Field(..., description="Ordered items")
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    notes: Optional[str] = None

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
