
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Notification, ProcessedEvent


def handle_order_confirmed(event: dict):
    db: Session = SessionLocal()

    try:
        event_id = event["event_id"]

        if db.query(ProcessedEvent).filter(
            ProcessedEvent.event_id == event_id
        ).first():
            print(
                f"Event {event_id} already processed. Skipping.",
                flush=True
            )
            return

        order_id = event["order_id"]

        
        user_id = event["data"]["user_id"]

        notification = Notification(
            user_id=user_id,
            order_id=order_id,
            type="order_confirmed",
            message=f"Your order #{order_id} has been confirmed."
        )

        db.add(notification)
        db.add(ProcessedEvent(event_id=event_id))

        db.commit()

        print(
            f"Notification sent for confirmed order {order_id}, "
            f"user {user_id}",
            flush=True
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def handle_order_cancelled(event: dict):
    db: Session = SessionLocal()

    try:
        event_id = event["event_id"]

        if db.query(ProcessedEvent).filter(
            ProcessedEvent.event_id == event_id
        ).first():
            print(
                f"Event {event_id} already processed. Skipping.",
                flush=True
            )
            return

        order_id = event["order_id"]

        
        user_id = event["data"]["user_id"]

        notification = Notification(
            user_id=user_id,
            order_id=order_id,
            type="order_cancelled",
            message=f"Your order #{order_id} has been cancelled."
        )

        db.add(notification)
        db.add(ProcessedEvent(event_id=event_id))

        db.commit()

        print(
            f"Notification sent for cancelled order {order_id}, "
            f"user {user_id}",
            flush=True
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def route_event(event: dict):
    event_type = event.get("event_type")

    if event_type == "order.confirmed":
        handle_order_confirmed(event)

    elif event_type == "order.cancelled":
        handle_order_cancelled(event)
