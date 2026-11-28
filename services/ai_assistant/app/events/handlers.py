
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.rag.ingest import upsert_product_doc, delete_product_doc


def handle_product_event(event: dict) -> None:
    event_type = event.get("event_type")
    data = event.get("data", {})

    db: Session = SessionLocal()

    try:
        if event_type in ("product.created", "product.updated"):
            product = {
                "id": data["product_id"],
                "name": data["name"],
                "description": data.get("description"),
                "price": data["price"]
            }

            upsert_product_doc(db, product)

        elif event_type == "product.deleted":
            delete_product_doc(db, data["product_id"])

        else:
            raise ValueError(f"Unsupported product event: {event_type}")

        db.commit()

        print(
            f"Successfully processed {event_type}",
            flush=True
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
