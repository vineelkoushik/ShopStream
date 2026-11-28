import time
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import OutboxEvent
from app.events.producer import producer


def relay():
    print("Product Outbox Relay started. Polling every 1 second...", flush=True)

    while True:
        db: Session = SessionLocal()

        try:
            stmt = (
                select(OutboxEvent)
                .where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.id)
                .limit(10)
                .with_for_update(skip_locked=True)
            )

            events = db.execute(stmt).scalars().all()

            if not events:
                db.rollback()
                time.sleep(1)
                continue

            delivery_results = {
                event.id: False for event in events
            }

            for event in events:
                producer.produce(
                    event.topic,
                    key=event.key,
                    value=json.dumps(event.payload),
                    on_delivery=lambda err, msg, event_id=event.id: delivery_results.update(
                        {event_id: err is None}
                    )
                )

            remaining = producer.flush(10)

            if remaining > 0:
                raise RuntimeError(
                    f"{remaining} Kafka messages are still pending delivery"
                )

            if not all(delivery_results.values()):
                raise RuntimeError("One or more Kafka messages failed delivery")

            for event in events:
                event.published_at = datetime.now(timezone.utc)

            db.commit()

            print(
                f"Published {len(events)} product events from outbox",
                flush=True
            )

        except Exception as e:
            print(f"Product Outbox Relay error: {e}", flush=True)
            db.rollback()

        finally:
            db.close()

        time.sleep(1)


if __name__ == "__main__":
    relay()

