
import json
import redis

from app.config import settings


redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def get_cached_product(product_id: int) -> dict | None:
    data = redis_client.get(f"product:{product_id}")

    if data:
        return json.loads(data)

    return None


def set_cached_product(
    product_id: int,
    product_data: dict,
    ttl: int = 60
):
    redis_client.setex(
        f"product:{product_id}",
        ttl,
        json.dumps(product_data, default=str)
    )


def invalidate_product(product_id: int):
    redis_client.delete(f"product:{product_id}")
