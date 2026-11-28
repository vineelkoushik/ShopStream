from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import ProductDoc


model = SentenceTransformer(settings.EMBEDDING_MODEL)


def search_products_by_similarity(
    db: Session,
    query: str,
    top_k: int = 5
) -> list[dict]:
    query_vector = model.encode(query).tolist()

    distance = ProductDoc.embedding.cosine_distance(
        query_vector
    ).label("distance")

    results = (
        db.query(
            ProductDoc.product_id,
            ProductDoc.content,
            distance
        )
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    return [
        {
            "product_id": r.product_id,
            "content": r.content,
            "distance": r.distance
        }
        for r in results
    ]
