
import logging

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductCreate, ProductUpdate, ProductOut, ProductList
from app.services import product_service
from app.security import get_current_user, require_admin
from app.cache import (
    get_cached_product,
    set_cached_product,
    invalidate_product
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductList)
def read_products(
    q: str | None = Query(None, description="Search by name or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return product_service.list_products(db, q, skip, limit)


@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    cached = get_cached_product(product_id)

    if cached:
        logger.info("CACHE HIT: product:%s", product_id)
        return cached

    logger.info("CACHE MISS: product:%s", product_id)

    product = product_service.get_product(db, product_id)

    product_data = ProductOut.model_validate(product).model_dump()
    set_cached_product(product_id, product_data)

    logger.info("CACHE SET: product:%s", product_id)

    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    return product_service.create_product(db, product_in)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    product = product_service.update_product(db, product_id, product_in)

    invalidate_product(product_id)
    logger.info("CACHE INVALIDATED: product:%s", product_id)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    product_service.delete_product(db, product_id)

    invalidate_product(product_id)
    logger.info("CACHE INVALIDATED: product:%s", product_id)
