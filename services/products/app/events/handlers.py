from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.product_service import reserve_stock
from app.events.envelope import build_event
from app.events.producer import publish

def handle_order_created(event: dict):
    db: Session = SessionLocal()
    try:
        order_id = event["order_id"]
        items = event["data"]["items"]
        
        success = reserve_stock(db, order_id, items)
        
        if success:
            event_data = {"order_id": order_id, "status": "reserved"}
            new_event = build_event("inventory.reserved", order_id, event_data)
            publish("inventory.reserved", order_id, new_event)
            print(f"Stock reserved for order {order_id}", flush=True)
        else:
            event_data = {"order_id": order_id, "reason": "out_of_stock"}
            new_event = build_event("inventory.rejected", order_id, event_data)
            publish("inventory.rejected", order_id, new_event)
            print(f"Stock rejected for order {order_id}", flush=True)
    finally:
        db.close()