from decimal import Decimal 
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Order, OrderItem
from app.schemas import OrderCreate
from app.clients.product_client import get_product, ProductNotFoundError, ProductServiceUnavailableError
from app.clients.payment_client import process_payment, PaymentFailedError, PaymentServiceUnavailableError

def create_order(db: Session, user_id: int, order_in: OrderCreate, token: str) -> Order:
    total = Decimal("0.00")  
    order_items = []

    for item in order_in.items:
        try:
            product_data = get_product(item.product_id, token)
        except ProductNotFoundError:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        except ProductServiceUnavailableError:
            raise HTTPException(status_code=503, detail="Product service is currently unavailable")

        unit_price = Decimal(str(product_data["price"]))
        total += unit_price * item.quantity

        order_items.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price
            )
        )

    new_order = Order(
        user_id=user_id,
        status="PENDING",
        total=total,
        items=order_items
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    try:
        process_payment(new_order.id, float(total), token)
        new_order.status = "CONFIRMED"
    except PaymentFailedError:
        new_order.status = "CANCELLED"
        new_order.cancel_reason = "Payment failed"
    except PaymentServiceUnavailableError:
        new_order.status = "PENDING"
        new_order.cancel_reason = "Payment service was down, needs retry"
        
    db.commit()
    db.refresh(new_order)
    return new_order

def get_order(db: Session, user_id: int, order_id: int, is_admin: bool) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not is_admin and order.user_id != user_id:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return order

def list_orders(db: Session, user_id: int, is_admin: bool, skip: int = 0, limit: int = 100):
    query = db.query(Order)
    
    if not is_admin:
        query = query.filter(Order.user_id == user_id)
        
    total = query.count()
    items = query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

def cancel_order(db: Session, user_id: int, order_id: int, is_admin: bool) -> Order:
    order = get_order(db, user_id, order_id, is_admin)
    
    if order.status not in ["PENDING", "CONFIRMED"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order in {order.status} status")
        
    order.status = "CANCELLED"
    order.cancel_reason = "Cancelled by user"
    db.commit()
    db.refresh(order)
    
    return order