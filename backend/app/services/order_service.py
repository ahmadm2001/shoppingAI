from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.order import Order, OrderItem
from app.models.item import Item
from app.models.user import User
from app.utils.enums import OrderStatus
from app.services.item_service import invalidate_items_cache


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    """Get all orders for a user, TEMP orders first."""
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(
            # TEMP orders first
            Order.status.desc(),
            Order.order_date.desc(),
        )
        .all()
    )


def get_order_with_items(db: Session, order_id: int, user_id: int) -> dict:
    """Get a single order with full item details."""
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    items_details = []
    for oi in order.items:
        item = db.query(Item).filter(Item.id == oi.item_id).first()
        items_details.append({
            "id": oi.id,
            "item_id": oi.item_id,
            "item_name": item.name if item else "Unknown",
            "quantity": oi.quantity,
            "price_at_order": oi.price_at_order,
        })

    return {
        "id": order.id,
        "user_id": order.user_id,
        "order_date": order.order_date,
        "shipping_address": order.shipping_address,
        "total_price": order.total_price,
        "status": order.status.value if isinstance(order.status, OrderStatus) else order.status,
        "items": items_details,
    }


def get_temp_order(db: Session, user_id: int) -> Optional[Order]:
    """Get the user's current TEMP order, if any."""
    return (
        db.query(Order)
        .filter(Order.user_id == user_id, Order.status == OrderStatus.TEMP)
        .first()
    )


def add_item_to_order(db: Session, user_id: int, item_id: int, quantity: int = 1) -> dict:
    """Add an item to the user's TEMP order. Creates a new order if none exists."""
    # Validate item
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if item.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Only {item.stock} items available.",
        )

    if item.stock == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This item is out of stock and cannot be added to your order.",
        )

    # Get or create TEMP order
    order = get_temp_order(db, user_id)
    if not order:
        user = db.query(User).filter(User.id == user_id).first()
        address = ""
        if user and (user.city or user.country):
            address = f"{user.city or ''}, {user.country or ''}".strip(", ")
        order = Order(
            user_id=user_id,
            status=OrderStatus.TEMP,
            shipping_address=address,
            order_date=datetime.now(timezone.utc),
        )
        db.add(order)
        db.flush()

    # Check if item already in order
    existing_oi = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id, OrderItem.item_id == item_id)
        .first()
    )

    if existing_oi:
        new_qty = existing_oi.quantity + quantity
        if new_qty > item.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Only {item.stock} items in stock, you already have {existing_oi.quantity} in your order.",
            )
        existing_oi.quantity = new_qty
    else:
        oi = OrderItem(
            order_id=order.id,
            item_id=item_id,
            quantity=quantity,
            price_at_order=item.price,
        )
        db.add(oi)

    # Recalculate total
    db.flush()
    _recalculate_total(db, order)
    db.commit()
    return {"message": f"Item '{item.name}' added to order", "order_id": order.id}


def remove_item_from_order(db: Session, user_id: int, item_id: int) -> dict:
    """Remove an item from the user's TEMP order."""
    order = get_temp_order(db, user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending order found",
        )

    oi = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id, OrderItem.item_id == item_id)
        .first()
    )
    if not oi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in order",
        )

    db.delete(oi)
    db.flush()

    # If no items left, delete the order
    remaining = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
    if remaining == 0:
        db.delete(order)
        db.commit()
        return {"message": "Item removed. Order deleted because it has no items."}

    _recalculate_total(db, order)
    db.commit()
    return {"message": "Item removed from order"}


def update_item_quantity(db: Session, user_id: int, item_id: int, quantity: int) -> dict:
    """Update the quantity of an item in the TEMP order."""
    order = get_temp_order(db, user_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending order found")

    oi = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id, OrderItem.item_id == item_id)
        .first()
    )
    if not oi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in order")

    item = db.query(Item).filter(Item.id == item_id).first()
    if quantity > item.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Only {item.stock} available.",
        )

    if quantity <= 0:
        return remove_item_from_order(db, user_id, item_id)

    oi.quantity = quantity
    _recalculate_total(db, order)
    db.commit()
    return {"message": "Quantity updated"}


def update_shipping_address(db: Session, user_id: int, address: str) -> dict:
    """Update shipping address on the TEMP order."""
    order = get_temp_order(db, user_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending order found")
    order.shipping_address = address
    db.commit()
    return {"message": "Shipping address updated"}


def purchase_order(db: Session, user_id: int) -> dict:
    """Purchase (close) the TEMP order, updating stock quantities."""
    order = get_temp_order(db, user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending order found",
        )

    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot purchase an empty order",
        )

    if not order.shipping_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set a shipping address before purchasing",
        )

    # Update stock for each item
    for oi in order.items:
        item = db.query(Item).filter(Item.id == oi.item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with id {oi.item_id} no longer exists",
            )
        if item.stock < oi.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for '{item.name}'. Only {item.stock} available.",
            )
        item.stock -= oi.quantity

    order.status = OrderStatus.CLOSE
    order.order_date = datetime.now(timezone.utc)
    db.commit()

    # Invalidate items cache since stock changed
    invalidate_items_cache()

    return {"message": "Order purchased successfully!", "order_id": order.id}


def delete_order(db: Session, user_id: int) -> dict:
    """Delete the user's TEMP order entirely."""
    order = get_temp_order(db, user_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending order found",
        )
    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}


def _recalculate_total(db: Session, order: Order):
    """Recalculate the total price of an order."""
    total = 0.0
    for oi in db.query(OrderItem).filter(OrderItem.order_id == order.id).all():
        total += oi.price_at_order * oi.quantity
    order.total_price = round(total, 2)
