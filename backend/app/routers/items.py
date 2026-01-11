"""Items API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import ItemStatus
from app.schemas.item import ItemResponse, ItemsAddRequest, ItemsAddResponse, ItemUpdateRequest
from app.services.items import ItemService

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("", response_model=list[ItemResponse])
async def list_items(
    status: ItemStatus | None = None,
    category_id: str | None = None,
    include_snoozed: bool = False,
    db: Session = Depends(get_db),
):
    """List items with optional filters."""
    service = ItemService(db)
    items = service.get_items(
        status=status,
        category_id=category_id,
        include_snoozed=include_snoozed,
    )
    return items


@router.post(":add", response_model=ItemsAddResponse)
async def add_items(request: ItemsAddRequest, db: Session = Depends(get_db)):
    """Add items from text input."""
    service = ItemService(db)
    result = service.add_items(request)
    return result


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get a single item."""
    service = ItemService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item niet gevonden")
    return item


@router.post("/{item_id}:check", response_model=ItemResponse)
async def check_item(item_id: str, db: Session = Depends(get_db)):
    """Mark an item as checked."""
    service = ItemService(db)
    item = service.check_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item niet gevonden")
    return item


@router.post("/{item_id}:uncheck", response_model=ItemResponse)
async def uncheck_item(item_id: str, db: Session = Depends(get_db)):
    """Mark an item as open (unchecked)."""
    service = ItemService(db)
    item = service.uncheck_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item niet gevonden")
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    request: ItemUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update an item."""
    service = ItemService(db)
    item = service.update_item(item_id, request)
    if not item:
        raise HTTPException(status_code=404, detail="Item niet gevonden")
    return item


@router.delete("/{item_id}")
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Delete an item."""
    service = ItemService(db)
    if not service.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item niet gevonden")
    return {"message": "Item verwijderd"}
