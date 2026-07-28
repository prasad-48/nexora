from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.dependencies import get_current_user
import backend.models as models
import backend.schemas as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all items in current user's backend cart"""
    items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()
    return items


@router.post("/items", response_model=schemas.CartItemResponse)
def add_or_update_cart_item(
    cart_item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a product to cart or update quantity if it already exists"""
    product = db.query(models.Product).filter(
        models.Product.id == cart_item.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == cart_item.product_id
    ).first()

    if existing_item:
        existing_item.quantity = cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        new_item = models.CartItem(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item


@router.delete("/items/{product_id}")
def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove item from cart by product ID"""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in cart"
        )

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Clear all items from current user's cart"""
    db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "Cart cleared"}
