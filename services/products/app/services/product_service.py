from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def list_products(db: Session, q: str | None = None, skip: int = 0, limit: int = 100):
    query = db.query(Product)
    
    if q:
        search_filter = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Product.description.ilike(search_filter)
            )
        )
        
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total, "skip": skip, "limit": limit}

def create_product(db: Session, product_in: ProductCreate) -> Product:
    new_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        reserved=0
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def update_product(db: Session, product_id: int, product_in: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()