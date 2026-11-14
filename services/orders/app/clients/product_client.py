import httpx
from app.config import settings

class ProductNotFoundError(Exception):
    pass

class ProductServiceUnavailableError(Exception):
    pass

def get_product(product_id: int, token: str) -> dict:
    url = f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(url, headers=headers)
            
            if response.status_code == 404:
                raise ProductNotFoundError(f"Product {product_id} not found")
                
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError:
        raise ProductServiceUnavailableError("Product service is down")