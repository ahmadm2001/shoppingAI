import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.item import Item
from app.config.redis import get_redis

ITEMS_CACHE_KEY = "all_items"
ITEMS_CACHE_TTL = 300  # 5 minutes


def get_all_items(db: Session) -> list[Item]:
    """Get all items, using Redis cache when available."""
    redis = get_redis()
    cached = redis.get(ITEMS_CACHE_KEY)
    if cached:
        items_data = json.loads(cached)
        return [_dict_to_item(d) for d in items_data]

    items = db.query(Item).all()
    items_data = [_item_to_dict(item) for item in items]
    redis.setex(ITEMS_CACHE_KEY, ITEMS_CACHE_TTL, json.dumps(items_data))
    return items


def get_item_by_id(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by its ID."""
    return db.query(Item).filter(Item.id == item_id).first()


def search_items(
    db: Session,
    names: Optional[list[str]] = None,
    price: Optional[float] = None,
    price_operator: Optional[str] = None,
    stock: Optional[int] = None,
    stock_operator: Optional[str] = None,
) -> list[Item]:
    """Search items by name, price and stock with operators."""
    query = db.query(Item)

    # Name search: support multiple keywords (OR logic)
    if names:
        name_filters = [Item.name.ilike(f"%{name.strip()}%") for name in names if name.strip()]
        if name_filters:
            query = query.filter(or_(*name_filters))

    # Price filter
    if price is not None and price_operator:
        if price_operator == "<":
            query = query.filter(Item.price < price)
        elif price_operator == ">":
            query = query.filter(Item.price > price)
        elif price_operator == "=":
            query = query.filter(Item.price == price)

    # Stock filter
    if stock is not None and stock_operator:
        if stock_operator == "<":
            query = query.filter(Item.stock < stock)
        elif stock_operator == ">":
            query = query.filter(Item.stock > stock)
        elif stock_operator == "=":
            query = query.filter(Item.stock == stock)

    return query.all()


def invalidate_items_cache():
    """Clear the items cache in Redis."""
    redis = get_redis()
    redis.delete(ITEMS_CACHE_KEY)


def _item_to_dict(item: Item) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "stock": item.stock,
        "category": item.category,
        "image_url": item.image_url,
    }


def _dict_to_item(d: dict) -> Item:
    item = Item()
    item.id = d["id"]
    item.name = d["name"]
    item.description = d.get("description")
    item.price = d["price"]
    item.stock = d["stock"]
    item.category = d.get("category")
    item.image_url = d.get("image_url")
    return item
