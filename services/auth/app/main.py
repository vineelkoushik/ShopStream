
from fastapi import FastAPI, Request
from app.routers import auth

app = FastAPI(title="ShopStream Auth Service")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")

    response = await call_next(request)

    if request_id:
        response.headers["X-Request-ID"] = request_id

    return response


app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}
