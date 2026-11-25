
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Order, ProcessedEvent
from app.events.envelope import build_event
from app.events.producer import publish


def handle_inventory_rejected(event: dict):
    db: Session = SessionLocal()

    try:
        event_id = event["event_id"]

        existing_event = (
            db.query(ProcessedEvent)
            .filter(ProcessedEvent.event_id == event_id)
            .first()
        )

        if existing_event:
            print(
                f"Event {event_id} already processed. Skipping.",
                flush=True
            )
            return

        order_id = event["order_id"]

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if order and order.status == "PENDING":
            order.status = "CANCELLED"
            order.cancel_reason = "Out of stock"

            print(
                f"Order {order_id} cancelled (out of stock)",
                flush=True
            )

            cancelled_event = build_event(
                "order.cancelled",
                order_id,
                {"reason": "out_of_stock"}
            )

            publish("order.cancelled", order_id, cancelled_event)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def handle_payment_completed(event: dict):
    db: Session = SessionLocal()

    try:
        event_id = event["event_id"]

        existing_event = (
            db.query(ProcessedEvent)
            .filter(ProcessedEvent.event_id == event_id)
            .first()
        )

        if existing_event:
            print(
                f"Event {event_id} already processed. Skipping.",
                flush=True
            )
            return

        order_id = event["order_id"]

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if order and order.status == "PENDING":
            order.status = "CONFIRMED"

            print(
                f"Order {order_id} confirmed (payment completed)",
                flush=True
            )

            confirmed_event = build_event(
                "order.confirmed",
                order_id,
                {"status": "confirmed"}
            )

            publish("order.confirmed", order_id, confirmed_event)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def handle_payment_failed(event: dict):
    db: Session = SessionLocal()

    try:
        event_id = event["event_id"]

        existing_event = (
            db.query(ProcessedEvent)
            .filter(ProcessedEvent.event_id == event_id)
            .first()
        )

        if existing_event:
            print(
                f"Event {event_id} already processed. Skipping.",
                flush=True
            )
            return

        order_id = event["order_id"]

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if order and order.status == "PENDING":
            order.status = "CANCELLED"
            order.cancel_reason = "Payment failed"

            print(
                f"Order {order_id} cancelled (payment failed)",
                flush=True
            )

            cancelled_event = build_event(
                "order.cancelled",
                order_id,
                {"reason": "payment_failed"}
            )

            publish("order.cancelled", order_id, cancelled_event)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

    except Exception:
        db.rollback()
        raise

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
