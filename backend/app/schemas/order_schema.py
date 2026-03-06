from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderItemAdd(BaseModel):
    item_id: int
    quantity: int = 1


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    item_name: Optional[str] = None
    quantity: int
    price_at_order: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: datetime
    shipping_address: Optional[str] = None
    total_price: float
    status: str
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderUpdateAddress(BaseModel):
    shipping_address: str


class OrderItemUpdate(BaseModel):
    item_id: int
    quantity: int
