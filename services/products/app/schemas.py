from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    reserved: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductList(BaseModel):
    items: list[ProductOut]
    total: int
    skip: int
    limit: int