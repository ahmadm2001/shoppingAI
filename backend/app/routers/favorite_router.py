from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.services.favorite_service import get_user_favorites, add_to_favorites, remove_from_favorites

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/")
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all favorite items for the current user."""
    return get_user_favorites(db, current_user.id)


@router.post("/{item_id}")
def add_favorite(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an item to favorites."""
    return add_to_favorites(db, current_user.id, item_id)


@router.delete("/{item_id}")
def remove_favorite(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an item from favorites."""
    return remove_from_favorites(db, current_user.id, item_id)
