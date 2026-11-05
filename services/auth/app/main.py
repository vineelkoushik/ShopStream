from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="ShopStream Auth Service")

app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}