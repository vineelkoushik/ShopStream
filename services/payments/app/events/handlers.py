
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.payment_service import process_payment
from app.schemas import PaymentCreate
from app.events.envelope import build_event
from app.events.producer import publish
from app.models import ProcessedEvent


def handle_inventory_reserved(event: dict):
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
        amount = event["data"].get("total", 0.0)

        try:
            payment_in = PaymentCreate(
                order_id=order_id,
                amount=amount
            )

            process_payment(db, payment_in)

        except Exception as e:
            db.rollback()

            event_data = {
                "order_id": order_id,
                "reason": str(e)
            }

            new_event = build_event(
                "payment.failed",
                order_id,
                event_data
            )

            publish("payment.failed", order_id, new_event)

            print(
                f"Payment failed for order {order_id}: {e}",
                flush=True
            )
            return

        db.add(ProcessedEvent(event_id=event_id))
        db.commit()

        event_data = {
            "order_id": order_id,
            "status": "completed"
        }

        new_event = build_event(
            "payment.completed",
            order_id,
            event_data
        )

        publish("payment.completed", order_id, new_event)

        print(
            f"Payment completed for order {order_id}",
            flush=True
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
