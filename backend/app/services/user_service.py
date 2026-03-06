from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.favorite import Favorite
from app.models.order import Order, OrderItem
from app.schemas.user_schema import UserCreate
from app.utils.security import hash_password, verify_password, create_access_token


def create_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user."""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        country=user_data.country,
        city=user_data.city,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def login_user(db: Session, username: str, password: str) -> dict:
    """Login a user and return a JWT token."""
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"user_id": user.id, "username": user.username})
    return {"access_token": token, "token_type": "bearer", "user": user}


def delete_user(db: Session, user: User) -> dict:
    """Delete a user and all associated data (favorites, orders)."""
    # Delete favorites
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    # Delete order items for user's orders
    user_orders = db.query(Order).filter(Order.user_id == user.id).all()
    for order in user_orders:
        db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    # Delete orders
    db.query(Order).filter(Order.user_id == user.id).delete()
    # Delete user
    db.delete(user)
    db.commit()
    return {"message": "User and all associated data deleted successfully"}
