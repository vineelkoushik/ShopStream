
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ProductDoc
from app.rag.search import search_products
from app.rag.recommend import recommend_products
from app.routers.assistant import router as assistant_router
app = FastAPI(title="ShopStream AI Assistant")
app.include_router(assistant_router)
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/products/search")
def semantic_product_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    try:
        results = search_products(db, q, limit)
        return {
            "query": q,
            "count": len(results),
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Product search failed"
        ) from error


@app.get("/products/{product_id}/recommendations")
def product_recommendations(
    product_id: int,
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    try:
        product = db.get(ProductDoc, product_id)

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found in recommendation index"
            )

        results = recommend_products(db, product_id, limit)

        return {
            "product_id": product_id,
            "count": len(results),
            "recommendations": results
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Product recommendation failed"
        ) from error
