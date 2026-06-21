from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.dependencies import get_current_user
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

    # Step 2: create the order
    new_order = models.Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        address=order_data.address
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

        # reduce stock
        item["product"].stock -= item["quantity"]

    db.commit()
    db.refresh(new_order)

    return new_order


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
    """Get a single order — only if it belongs to the logged in user"""
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
    """Update order status — admin only. Valid: pending, shipped, delivered, cancelled"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    valid_statuses = ["pending", "shipped", "delivered", "cancelled"]
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