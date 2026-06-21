from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────

class UserCreate(BaseModel):
    """Used when someone registers"""
    full_name: str
    email: EmailStr        # automatically validates email format
    password: str

class UserLogin(BaseModel):
    """Used when someone logs in"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """What we send back — notice no password!"""
    id: int
    full_name: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from database objects


# ─────────────────────────────────────────
# TOKEN SCHEMAS
# ─────────────────────────────────────────

class Token(BaseModel):
    """Returned after successful login"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data stored inside the JWT token"""
    email: Optional[str] = None


# ─────────────────────────────────────────
# PRODUCT SCHEMAS
# ─────────────────────────────────────────

class ProductCreate(BaseModel):
    """Used when adding a new product"""
    name: str
    brand: str
    category: str
    description: str
    price: float
    old_price: Optional[float] = None
    image_url: Optional[str] = None
    stock: int
    rating: Optional[float] = 0.0
    is_featured: Optional[bool] = False

class ProductResponse(BaseModel):
    """What we send back for a product"""
    id: int
    name: str
    brand: str
    category: str
    description: str
    price: float
    old_price: Optional[float] = None
    image_url: Optional[str] = None
    stock: int
    rating: float
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# ORDER SCHEMAS
# ─────────────────────────────────────────

class OrderItemCreate(BaseModel):
    """One item inside an order"""
    product_id: int = Field(gt=0, description="Valid product ID")
    quantity: int = Field(gt=0, description="Must be at least 1")

class OrderCreate(BaseModel):
    """Used when placing an order"""
    address: str = Field(min_length=1, description="Delivery address")
    items: List[OrderItemCreate]  # list of products being ordered

class OrderItemResponse(BaseModel):
    """One item returned in order response"""
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductResponse

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    """Full order details returned to user"""
    id: int
    total_amount: float
    status: str
    address: str
    created_at: datetime
    order_items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# CHAT SCHEMAS
# ─────────────────────────────────────────

class ChatMessage(BaseModel):
    """Message sent to AI chatbot"""
    message: str

class ChatResponse(BaseModel):
    """Response from AI chatbot"""
    reply: str