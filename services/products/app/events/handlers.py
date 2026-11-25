
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.product_service import (
    reserve_stock,
    commit_reservation,
    release_stock
)
from app.events.envelope import build_event
from app.events.producer import publish
from app.models import ProcessedEvent


def handle_order_created(event: dict):
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
        items = event["data"]["items"]

        success = reserve_stock(db, order_id, items)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

        if success:
            event_data = {
                "order_id": order_id,
                "status": "reserved",
                "total": event["data"]["total"],
                "user_id": event["data"]["user_id"]
            }

            new_event = build_event(
                "inventory.reserved",
                order_id,
                event_data
            )

            publish("inventory.reserved", order_id, new_event)

            print(
                f"Stock reserved for order {order_id}",
                flush=True
            )

        else:
            event_data = {
                "order_id": order_id,
                "reason": "out_of_stock"
            }

            new_event = build_event(
                "inventory.rejected",
                order_id,
                event_data
            )

            publish("inventory.rejected", order_id, new_event)

            print(
                f"Stock rejected for order {order_id}",
                flush=True
            )

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

        commit_reservation(db, order_id)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

        print(
            f"Reservation committed for order {order_id}",
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

        release_stock(db, order_id)

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

        print(
            f"Reservation released for order {order_id}",
            flush=True
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def route_event(event: dict):
    event_type = event.get("event_type")

    if event_type == "order.created":
        handle_order_created(event)

    elif event_type == "payment.completed":
        handle_payment_completed(event)

    elif event_type == "order.cancelled":
        handle_order_cancelled(event)
