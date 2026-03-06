from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.schemas.order_schema import OrderItemAdd, OrderUpdateAddress, OrderItemUpdate
from app.services.order_service import (
    get_user_orders,
    get_order_with_items,
    get_temp_order,
    add_item_to_order,
    remove_item_from_order,
    update_item_quantity,
    update_shipping_address,
    purchase_order,
    delete_order,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all orders for the current user."""
    orders = get_user_orders(db, current_user.id)
    result = []
    for order in orders:
        result.append(get_order_with_items(db, order.id, current_user.id))
    return result


@router.get("/pending")
def get_pending_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current pending (TEMP) order."""
    order = get_temp_order(db, current_user.id)
    if not order:
        return {"message": "No pending order", "order": None}
    return get_order_with_items(db, order.id, current_user.id)


@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific order by ID."""
    return get_order_with_items(db, order_id, current_user.id)


@router.post("/items")
def add_item(
    item_data: OrderItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an item to the pending order."""
    return add_item_to_order(db, current_user.id, item_data.item_id, item_data.quantity)


@router.delete("/items/{item_id}")
def remove_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an item from the pending order."""
    return remove_item_from_order(db, current_user.id, item_id)


@router.put("/items")
def update_quantity(
    update_data: OrderItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the quantity of an item in the pending order."""
    return update_item_quantity(db, current_user.id, update_data.item_id, update_data.quantity)


@router.put("/address")
def update_address(
    address_data: OrderUpdateAddress,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the shipping address on the pending order."""
    return update_shipping_address(db, current_user.id, address_data.shipping_address)


@router.post("/purchase")
def purchase(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Purchase (close) the pending order."""
    return purchase_order(db, current_user.id)


@router.delete("/")
def cancel_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the pending order entirely."""
    return delete_order(db, current_user.id)
