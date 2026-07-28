from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database import get_db
from backend.dependencies import get_current_user, get_admin_user
import backend.models as models
import backend.schemas as schemas

router = APIRouter()

# ─────────────────────────────────────────
# GET ALL PRODUCTS
# ─────────────────────────────────────────
@router.get("/", response_model=List[schemas.ProductResponse])
def get_products(
    search: Optional[str] = Query(None, description="Search by name or brand"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    featured: Optional[bool] = Query(None, description="Filter featured products"),
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filters
    - Search by name or brand
    - Filter by category
    - Filter by price range
    - Filter featured products
    """
    query = db.query(models.Product)

    # search filter
    if search:
        query = query.filter(
            models.Product.name.ilike(f"%{search}%") |
            models.Product.brand.ilike(f"%{search}%")
        )

    # category filter
    if category:
        query = query.filter(
            models.Product.category.ilike(f"%{category}%")
        )

    # price filters
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    # featured filter
    if featured is not None:
        query = query.filter(models.Product.is_featured == featured)

    products = query.order_by(models.Product.created_at.desc()).all()
    return products


# ─────────────────────────────────────────
# GET SINGLE PRODUCT
# ─────────────────────────────────────────
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    return product


# ─────────────────────────────────────────
# CREATE PRODUCT (admin only)
# ─────────────────────────────────────────
@router.post("/", response_model=schemas.ProductResponse)
def create_product(
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Add a new product — admin only"""
    new_product = models.Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# ─────────────────────────────────────────
# UPDATE PRODUCT (admin only)
# ─────────────────────────────────────────
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Update a product — admin only"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    for key, value in product_data.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ─────────────────────────────────────────
# DELETE PRODUCT (admin only)
# ─────────────────────────────────────────
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Delete a product — admin only"""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}


# ─────────────────────────────────────────
# GET CATEGORIES
# ─────────────────────────────────────────
@router.get("/meta/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all unique product categories"""
    categories = db.query(models.Product.category).distinct().all()
    return {"categories": [c[0] for c in categories]}