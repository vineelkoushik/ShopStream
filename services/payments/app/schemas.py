from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0)

class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True