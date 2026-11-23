from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Order
from app.events.envelope import build_event
from app.events.producer import publish
from datetime import datetime, timezone

def handle_inventory_rejected(event: dict):
    db: Session = SessionLocal()
    try:
        order_id = event["order_id"]
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "PENDING":
            order.status = "CANCELLED"
            order.cancel_reason = "Out of stock"
            db.commit()
            print(f"Order {order_id} cancelled (out of stock)", flush=True)
            cancelled_event = build_event("order.cancelled", order_id, {"reason": "out_of_stock"})
            publish("order.cancelled", order_id, cancelled_event)
    finally:
        db.close()

def handle_payment_completed(event: dict):
    db: Session = SessionLocal()
    try:
        order_id = event["order_id"]
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "PENDING":
            order.status = "CONFIRMED"
            db.commit()
            print(f"Order {order_id} confirmed (payment completed)", flush=True)
            confirmed_event = build_event("order.confirmed", order_id, {"status": "confirmed"})
            publish("order.confirmed", order_id, confirmed_event)
    finally:
        db.close()

def handle_payment_failed(event: dict):
    db: Session = SessionLocal()
    try:
        order_id = event["order_id"]
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "PENDING":
            order.status = "CANCELLED"
            order.cancel_reason = "Payment failed"
            db.commit()
            print(f"Order {order_id} cancelled (payment failed)", flush=True)
            cancelled_event = build_event("order.cancelled", order_id, {"reason": "payment_failed"})
            publish("order.cancelled", order_id, cancelled_event)
    finally:
        db.close()

def route_event(event: dict):
    event_type = event.get("event_type")
    if event_type == "inventory.rejected":
        handle_inventory_rejected(event)
    elif event_type == "payment.completed":
        handle_payment_completed(event)
    elif event_type == "payment.failed":
        handle_payment_failed(event)