import uuid
from datetime import datetime, timezone

def build_event(event_type: str, order_id: int, data: dict, correlation_id: str | None = None) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "order_id": order_id,
        "version": 1,
        "data": data
    }