from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[schemas.MyProduct])
def get_products(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products"""
    products = db.query(models.MyProduct).offset(skip).limit(limit).all()
    return products


@router.get("/{asin}", response_model=schemas.MyProduct)
def get_product(
    asin: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ASIN"""
    product = db.query(models.MyProduct).filter(models.MyProduct.asin == asin).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/bestselling/{count}")
def get_bestselling_products(
    count: int = 10,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get top selling products"""
    products = (
        db.query(models.MyProduct)
        .order_by(models.MyProduct.sales_amount.desc())
        .limit(count)
        .all()
    )
    return [{"asin": p.asin, "title": p.title, "sales_amount": p.sales_amount} for p in products]