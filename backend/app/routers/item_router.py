from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.schemas.item_schema import ItemResponse
from app.services.item_service import get_all_items, get_item_by_id, search_items

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    """Get all available items."""
    return get_all_items(db)


@router.get("/search", response_model=list[ItemResponse])
def search(
    name: Optional[str] = Query(None, description="Search by name (comma-separated for multiple)"),
    price: Optional[float] = Query(None, description="Price value"),
    price_op: Optional[str] = Query(None, description="Price operator: <, >, ="),
    stock: Optional[int] = Query(None, description="Stock value"),
    stock_op: Optional[str] = Query(None, description="Stock operator: <, >, ="),
    db: Session = Depends(get_db),
):
    """Search items by name, price, and stock with operators."""
    names = None
    if name:
        names = [n.strip() for n in name.split(",") if n.strip()]

    results = search_items(
        db=db,
        names=names,
        price=price,
        price_operator=price_op,
        stock=stock,
        stock_operator=stock_op,
    )
    return results


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = get_item_by_id(db, item_id)
    if not item:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
