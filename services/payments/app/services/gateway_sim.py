import random
from app.config import settings

class PaymentDeclinedError(Exception):
    pass

class LimitExceededError(Exception):
    pass

def charge(amount: float) -> bool:
    if amount > settings.PAYMENT_MAX_AMOUNT:
        raise LimitExceededError(f"Amount exceeds maximum limit of {settings.PAYMENT_MAX_AMOUNT}")
    
    if random.random() < settings.PAYMENT_FAIL_RATE:
        raise PaymentDeclinedError("Payment was declined by the bank")
    
    return True 