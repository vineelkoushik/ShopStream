from sqlalchemy.orm import Session
from sqlalchemy import or_, update
from fastapi import HTTPException

from app.models import Product, StockReservation, OutboxEvent
from app.schemas import ProductCreate, ProductUpdate
from app.events.envelope import build_event


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


def list_products(
    db: Session,
    q: str | None = None,
    skip: int = 0,
    limit: int = 100
):
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

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }


def create_product(db: Session, product_in: ProductCreate) -> Product:
    try:
        new_product = Product(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            stock=product_in.stock,
            reserved=0
        )

        db.add(new_product)
        db.flush()

        event = build_event(
            "product.created",
            0,
            {
                "product_id": new_product.id,
                "name": new_product.name,
                "description": new_product.description,
                "price": float(new_product.price)
            }
        )

        db.add(
            OutboxEvent(
                topic="product.created",
                key=str(new_product.id),
                payload=event
            )
        )

        db.commit()
        db.refresh(new_product)

        return new_product

    except Exception:
        db.rollback()
        raise


def update_product(
    db: Session,
    product_id: int,
    product_in: ProductUpdate
) -> Product:
    try:
        product = get_product(db, product_id)

        update_data = product_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(product, key, value)

        db.flush()

        event = build_event(
            "product.updated",
            0,
            {
                "product_id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price)
            }
        )

        db.add(
            OutboxEvent(
                topic="product.updated",
                key=str(product.id),
                payload=event
            )
        )

        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        raise


def delete_product(db: Session, product_id: int):
    try:
        product = get_product(db, product_id)

        db.delete(product)
        db.flush()

        event = build_event(
            "product.deleted",
            0,
            {
                "product_id": product_id
            }
        )

        db.add(
            OutboxEvent(
                topic="product.deleted",
                key=str(product_id),
                payload=event
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


def reserve_stock(db: Session, order_id: int, items: list[dict]) -> bool:
    try:
        for item in items:
            product_id = item["product_id"]
            qty = item["quantity"]

            stmt = (
                update(Product)
                .where(
                    Product.id == product_id,
                    Product.stock - Product.reserved >= qty
                )
                .values(reserved=Product.reserved + qty)
            )

            result = db.execute(stmt)

            if result.rowcount == 0:
                db.rollback()
                return False

            reservation = StockReservation(
                order_id=order_id,
                product_id=product_id,
                quantity=qty,
                status="reserved"
            )

            db.add(reservation)

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise


def release_stock(db: Session, order_id: int) -> bool:
    reservations = db.query(StockReservation).filter(
        StockReservation.order_id == order_id,
        StockReservation.status == "reserved"
    ).all()

    if not reservations:
        return False

    try:
        for res in reservations:
            db.execute(
                update(Product)
                .where(Product.id == res.product_id)
                .values(reserved=Product.reserved - res.quantity)
            )

            res.status = "released"

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise


def commit_reservation(db: Session, order_id: int) -> bool:
    reservations = db.query(StockReservation).filter(
        StockReservation.order_id == order_id,
        StockReservation.status == "reserved"
    ).all()

    if not reservations:
        return False

    try:
        for res in reservations:
            db.execute(
                update(Product)
                .where(Product.id == res.product_id)
                .values(
                    stock=Product.stock - res.quantity,
                    reserved=Product.reserved - res.quantity
                )
            )

            res.status = "committed"

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
