from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

# ─────────────────────────────────────────
# USERS TABLE
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    full_name       = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin        = Column(Boolean, default=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # one user can have many orders
    orders = relationship("Order", back_populates="user")


# ─────────────────────────────────────────
# PRODUCTS TABLE
# ─────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    brand       = Column(String, nullable=False)
    category    = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price       = Column(Float, nullable=False)
    old_price   = Column(Float, nullable=True)
    image_url   = Column(String, nullable=True)
    stock       = Column(Integer, default=0)
    rating      = Column(Float, default=0.0)
    is_featured = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    # one product can appear in many order items
    order_items = relationship("OrderItem", back_populates="product")


# ─────────────────────────────────────────
# ORDERS TABLE
# ─────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status       = Column(String, default="pending")
    address      = Column(Text, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    # relationships
    user        = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


# ─────────────────────────────────────────
# ORDER ITEMS TABLE
# ─────────────────────────────────────────
class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)
    price      = Column(Float, nullable=False)

    # relationships
    order   = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")