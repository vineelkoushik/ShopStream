
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.payment_service import process_payment
from app.schemas import PaymentCreate
from app.events.envelope import build_event
from app.events.producer import publish


def handle_inventory_reserved(event: dict):
    db: Session = SessionLocal()

    try:
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

    finally:
        db.close()
