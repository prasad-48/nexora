import uuid
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.config import settings
import backend.models as models
import backend.schemas as schemas

router = APIRouter()


# ─────────────────────────────────────────
# PLACE ORDER
# ─────────────────────────────────────────
@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Place a new order
    - Checks stock availability
    - Calculates total amount
    - Creates order + order items
    - Reduces product stock
    - Clears user backend cart
    """

    if not order_data.address.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery address is required"
        )

    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )

    total_amount = 0
    order_items_to_create = []

    # Step 1: validate all products and calculate total
    for item in order_data.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each item quantity must be at least 1"
            )
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}. Available: {product.stock}"
            )

        item_total = product.price * item.quantity
        total_amount += item_total

        order_items_to_create.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price
        })

    # Generate a unique razorpay order id reference
    razorpay_order_id = f"order_{uuid.uuid4().hex[:14]}"

    # Step 2: create the order
    new_order = models.Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        address=order_data.address,
        payment_method=order_data.payment_method or "razorpay",
        payment_status="pending",
        razorpay_order_id=razorpay_order_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Step 3: create order items and reduce stock
    for item in order_items_to_create:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(order_item)
        item["product"].stock -= item["quantity"]

    # Step 4: clear user's cart
    db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).delete()

    db.commit()
    db.refresh(new_order)

    return new_order


# ─────────────────────────────────────────
# RAZORPAY PAYMENT VERIFICATION
# ─────────────────────────────────────────
@router.post("/verify-payment")
def verify_payment(
    verify_data: schemas.RazorpayVerifyRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Verifies Razorpay payment signature and marks order as paid
    """
    order = db.query(models.Order).filter(
        models.Order.id == verify_data.order_id,
        models.Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # In sandbox/dummy key mode or test verification, we validate signature if key secret is non-dummy
    # or accept mock test signatures
    if settings.RAZORPAY_KEY_SECRET != "nexora_dummy_secret":
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{verify_data.razorpay_order_id}|{verify_data.razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != verify_data.razorpay_signature:
            order.payment_status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Razorpay signature"
            )

    order.payment_status = "paid"
    order.razorpay_payment_id = verify_data.razorpay_payment_id
    if verify_data.razorpay_order_id:
        order.razorpay_order_id = verify_data.razorpay_order_id
    order.status = "processing"

    db.commit()
    db.refresh(order)

    return {
        "success": True,
        "message": "Payment verified successfully",
        "order_id": order.id,
        "payment_status": order.payment_status,
        "order_status": order.status
    }


# ─────────────────────────────────────────
# GET MY ORDERS
# ─────────────────────────────────────────
@router.get("/me", response_model=List[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all orders for the logged in user"""
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()

    return orders


# ─────────────────────────────────────────
# GET SINGLE ORDER
# ─────────────────────────────────────────
@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a single order — only if it belongs to the logged in user or admin"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this order"
        )

    return order


# ─────────────────────────────────────────
# UPDATE ORDER STATUS (admin only)
# ─────────────────────────────────────────
@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update order status — admin only. Valid: pending, processing, shipped, delivered, cancelled"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order.status = new_status
    db.commit()

    return {"message": f"Order {order_id} status updated to {new_status}"}