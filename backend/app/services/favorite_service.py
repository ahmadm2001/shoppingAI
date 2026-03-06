from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.favorite import Favorite
from app.models.item import Item


def get_user_favorites(db: Session, user_id: int) -> list[dict]:
    """Get all favorite items for a user with item details."""
    favorites = (
        db.query(Favorite, Item)
        .join(Item, Favorite.item_id == Item.id)
        .filter(Favorite.user_id == user_id)
        .all()
    )
    result = []
    for fav, item in favorites:
        result.append({
            "favorite_id": fav.id,
            "item_id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "stock": item.stock,
            "category": item.category,
            "image_url": item.image_url,
        })
    return result


def add_to_favorites(db: Session, user_id: int, item_id: int) -> dict:
    """Add an item to user's favorites. Each item can appear only once."""
    # Check item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Check if already in favorites
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.item_id == item_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item already in favorites",
        )

    fav = Favorite(user_id=user_id, item_id=item_id)
    db.add(fav)
    db.commit()
    return {"message": f"Item '{item.name}' added to favorites"}


def remove_from_favorites(db: Session, user_id: int, item_id: int) -> dict:
    """Remove an item from user's favorites."""
    fav = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.item_id == item_id)
        .first()
    )
    if not fav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in favorites",
        )
    db.delete(fav)
    db.commit()
    return {"message": "Item removed from favorites"}
