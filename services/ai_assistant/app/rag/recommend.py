from sqlalchemy import text
from sqlalchemy.orm import Session


def recommend_products(
    db: Session,
    product_id: int,
    limit: int = 5
) -> list[dict]:
    statement = text("""
        SELECT
            recommended.product_id,
            recommended.content,
            ROUND(
                (1 - (recommended.embedding <=> source.embedding))::numeric,
                4
            ) AS similarity
        FROM product_docs AS source
        CROSS JOIN product_docs AS recommended
        WHERE source.product_id = :product_id
          AND recommended.product_id != :product_id
        ORDER BY recommended.embedding <=> source.embedding
        LIMIT :limit
    """)

    results = db.execute(
        statement,
        {
            "product_id": product_id,
            "limit": limit
        }
    ).mappings().all()

    return [
        {
            "product_id": row["product_id"],
            "content": row["content"],
            "similarity": float(row["similarity"])
        }
        for row in results
    ]
