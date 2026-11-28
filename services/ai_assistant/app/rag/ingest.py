
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import ProductDoc


embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def create_product_content(product: dict) -> str:
    name = product.get("name", "")
    description = product.get("description") or ""
    price = product.get("price", "")

    return (
        f"Product: {name}\n"
        f"Description: {description}\n"
        f"Price: {price}"
    )


def generate_embedding(content: str) -> list[float]:
    embedding = embedding_model.encode(
        content,
        normalize_embeddings=True
    )

    return embedding.tolist()


def upsert_product_doc(db: Session, product: dict) -> None:
    product_id = product["id"]
    content = create_product_content(product)
    embedding = generate_embedding(content)

    statement = insert(ProductDoc).values(
        product_id=product_id,
        content=content,
        embedding=embedding,
        updated_at=datetime.now(timezone.utc)
    )

    statement = statement.on_conflict_do_update(
        index_elements=[ProductDoc.product_id],
        set_={
            "content": statement.excluded.content,
            "embedding": statement.excluded.embedding,
            "updated_at": func.now()
        }
    )

    db.execute(statement)


def delete_product_doc(db: Session, product_id: int) -> None:
    statement = delete(ProductDoc).where(
        ProductDoc.product_id == product_id
    )

    db.execute(statement)
