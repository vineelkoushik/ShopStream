import time
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import OutboxEvent
from app.events.producer import producer
from sqlalchemy import select, update
from datetime import datetime, timezone

def relay():
    print("Outbox Relay started. Polling every 1 second...", flush=True)
    while True:
        db: Session = SessionLocal()
        try:
            stmt = select(OutboxEvent).where(OutboxEvent.published_at.is_(None)).limit(10).with_for_update(skip_locked=True)
            events = db.execute(stmt).scalars().all()
            
            for event in events:
                producer.produce(
                    event.topic,
                    key=event.key,
                    value=json.dumps(event.payload)
                )
                event.published_at = datetime.now(timezone.utc)
            
            db.commit()
            producer.flush()
            
            if events:
                print(f"Published {len(events)} events from outbox", flush=True)
        except Exception as e:
            print(f"Relay error: {e}", flush=True)
            db.rollback()
        finally:
            db.close()
        
        time.sleep(1)

if __name__ == "__main__":
    relay()