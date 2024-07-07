from sqlalchemy.orm import Session
from app.models import Product, User
from app.schemas.product import ProductData
from fastapi import HTTPException
from datetime import datetime, timezone
import json


def add_product(db: Session, site: str, user: User, url: str):
    # Initiates product without data
    prev_prod = db.query(Product).filter(Product.url == url).first()
    if prev_prod:
        return prev_prod
    product_obj = Product(url=url, site=site, added_by=user.id)
    db.add(product_obj)
    db.commit()
    db.refresh(product_obj)
    return product_obj


def add_product_data(db: Session, product: Product, prod_data: ProductData):
    product.title = prod_data.title
    product.data = prod_data.model_dump_json()
    product.is_complete = True
    db.commit()
    db.refresh(product)
    return product

def get_products(db: Session):
    return db.query(Product).all()

def get_product(db: Session, pk: int):
    product = db.query(Product).filter(Product.id == pk).first()
    if not product:
        raise HTTPException(404, 'Product not found')
    return product

def get_product_data(db: Session, pk: int):
    product = get_product(db, pk)
    return json.loads(product.data) if product.data else None

def get_product_from_url(db: Session, url: str):
    product = db.query(Product).filter(Product.url == url).first()
    if not product:
        raise HTTPException(404, 'Product not found')
    return product

def get_product_data_from_url(db: Session, url: str):
    product = get_product_from_url(db, url)
    return json.loads(product.data) if product.data else None
