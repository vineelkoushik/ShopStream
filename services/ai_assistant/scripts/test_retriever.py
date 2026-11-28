from app.database import SessionLocal
from app.rag.retriever import search_products_by_similarity

db = SessionLocal()

try:
    results = search_products_by_similarity(
        db,
        "wireless headphones",
        top_k=3
    )

    for r in results:
        print(
            f"Product {r['product_id']}: "
            f"{r['content']} "
            f"(Distance: {r['distance']:.3f})"
        )
finally:
    db.close()
