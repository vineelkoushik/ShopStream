from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total: Decimal
    cancel_reason: str | None
    created_at: datetime
    items: list[OrderItemOut]

    class Config:
        from_attributes = True