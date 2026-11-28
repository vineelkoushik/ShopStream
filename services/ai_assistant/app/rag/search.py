from sqlalchemy import text
from sqlalchemy.orm import Session

from app.rag.ingest import generate_embedding


def search_products(
    db: Session,
    query: str,
    limit: int = 5
) -> list[dict]:
    embedding = generate_embedding(query)

    statement = text("""
        SELECT
            product_id,
            content,
            1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM product_docs
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)

    results = db.execute(
        statement,
        {
            "embedding": str(embedding),
            "limit": limit
        }
    ).mappings().all()

    return [
        {
            "product_id": row["product_id"],
            "content": row["content"],
            "similarity": round(float(row["similarity"]), 4)
        }
        for row in results
    ]
