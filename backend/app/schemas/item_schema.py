from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    image_url: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True


class ItemSearchRequest(BaseModel):
    name: Optional[str] = None
    names: Optional[list[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price: Optional[float] = None
    price_operator: Optional[str] = None  # <, >, =
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    stock: Optional[int] = None
    stock_operator: Optional[str] = None  # <, >, =
