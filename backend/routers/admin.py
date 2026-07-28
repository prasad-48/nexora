from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.dependencies import get_admin_user
import backend.models as models
import backend.schemas as schemas

router = APIRouter()


@router.get("/dashboard", response_model=schemas.AdminStatsResponse)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """Get dashboard stats for admin"""
    total_sales = db.query(func.sum(models.Order.total_amount)).filter(
        models.Order.payment_status == "paid"
    ).scalar() or 0.0

    if total_sales == 0.0:
        # Fallback sum for all non-cancelled orders if payment status wasn't tracked previously
        total_sales = db.query(func.sum(models.Order.total_amount)).filter(
            models.Order.status != "cancelled"
        ).scalar() or 0.0

    total_orders = db.query(models.Order).count()
    total_products = db.query(models.Product).count()
    total_users = db.query(models.User).count()

    low_stock_products = db.query(models.Product).filter(
        models.Product.stock <= 5
    ).all()

    recent_orders = db.query(models.Order).order_by(
        models.Order.created_at.desc()
    ).limit(10).all()

    return {
        "total_revenue": round(float(total_sales), 2),
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "low_stock_products": low_stock_products,
        "recent_orders": recent_orders
    }


@router.get("/orders", response_model=List[schemas.OrderResponse])
def get_all_orders_admin(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """Get all customer orders for management — admin only"""
    orders = db.query(models.Order).order_by(
        models.Order.created_at.desc()
    ).all()
    return orders
