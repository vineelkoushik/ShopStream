import httpx
from app.config import settings

class PaymentFailedError(Exception):
    pass

class PaymentServiceUnavailableError(Exception):
    pass

def process_payment(order_id: int, amount: float, token: str) -> dict:
    url = f"{settings.PAYMENT_SERVICE_URL}/payments/charge"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"order_id": order_id, "amount": amount}
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, json=payload, headers=headers)
            
            if response.status_code == 402:
                raise PaymentFailedError("Payment was declined")
                
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError:
        raise PaymentServiceUnavailableError("Payment service is down")