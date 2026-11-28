
import httpx
from langchain_core.tools import tool

from app.config import settings
from app.database import SessionLocal
from app.rag.retriever import search_products_by_similarity


@tool
def search_products(query: str) -> str:
    """Search the ShopStream product catalog using semantic similarity."""

    db = SessionLocal()

    try:
        results = search_products_by_similarity(
            db,
            query,
            top_k=5
        )

        if not results:
            return "No relevant products found."

        output = "Here are the most relevant products:\n"

        for product in results:
            output += (
                f"- Product ID: {product['product_id']}\n"
                f"  Details: {product['content']}\n"
                f"  Distance: {product['distance']:.3f}\n"
            )

        return output

    except Exception:
        return "Product search failed."

    finally:
        db.close()


def create_get_my_orders_tool(access_token: str):
    """Create an order tool for the authenticated user."""

    @tool
    def get_my_orders() -> str:
        """Fetch the authenticated user's orders from ShopStream."""

        url = f"{settings.ORDER_SERVICE_URL.rstrip('/')}/orders/"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

            orders = response.json()

            if not orders:
                return "You have no orders."

            output = "Here are your orders:\n"

            for order in orders:
                output += (
                    f"- Order #{order['id']}\n"
                    f"  Status: {order['status']}\n"
                    f"  Total: {order['total']}\n"
                    f"  Items: {len(order.get('items', []))}\n"
                )

            return output

        except httpx.HTTPStatusError as exc:
            return f"Order service returned HTTP {exc.response.status_code}."

        except httpx.RequestError:
            return "Unable to connect to the Order service."

        except (ValueError, KeyError):
            return "Unable to process the Order service response."

    return get_my_orders
