
import logging

from fastapi import FastAPI
from app.routers import products


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ShopStream Product Service")

app.include_router(products.router)


@app.get("/health")
def health():
    return {"status": "ok"}
