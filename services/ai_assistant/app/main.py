
from fastapi import FastAPI

app = FastAPI(title="ShopStream AI Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}
