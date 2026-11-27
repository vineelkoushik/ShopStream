import redis
from fastapi import HTTPException, Depends
from app.config import settings
from app.security import get_current_user
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
def rate_limit_orders(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    key = f"rate_limit:orders:{user_id}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    if current > 5:
        raise HTTPException(status_code=429, detail="Too many orders. Please wait a minute.")