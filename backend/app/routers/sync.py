"""Sync API endpoints for external services like Albert Heijn."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item, ItemStatus
from app.services.ah import get_ah_service, SyncResult

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncResponse(BaseModel):
    """Response from sync operation."""
    synced: int
    failed: int
    not_found: int
    details: list[dict]


@router.post("/ah", response_model=SyncResponse)
async def sync_to_ah(db: Session = Depends(get_db)):
    """Sync all open items to Albert Heijn shopping list."""
    # Get all open items
    items = (
        db.query(Item)
        .filter(Item.status == ItemStatus.OPEN)
        .filter(
            (Item.snooze_until.is_(None)) | (Item.snooze_until <= datetime.utcnow())
        )
        .all()
    )

    if not items:
        raise HTTPException(status_code=404, detail="Geen items om te synchroniseren")

    # Convert to list of dicts for sync
    items_to_sync = [
        {"name": item.name_raw, "qty": item.qty}
        for item in items
    ]

    # Sync to AH
    ah_service = get_ah_service()
    try:
        results = await ah_service.sync_items(items_to_sync)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AH sync failed: {str(e)}")

    # Count results
    synced = sum(1 for r in results if r.status == "ok")
    not_found = sum(1 for r in results if r.status == "not_found")
    failed = sum(1 for r in results if r.status == "error")

    return SyncResponse(
        synced=synced,
        failed=failed,
        not_found=not_found,
        details=[
            {
                "item": r.item_name,
                "status": r.status,
                "ah_product": r.ah_product,
                "error": r.error,
            }
            for r in results
        ],
    )


@router.post("/ah/simple", response_class=PlainTextResponse)
async def sync_to_ah_simple(db: Session = Depends(get_db)):
    """Sync to AH and return simple text response (for Siri)."""
    # Get all open items
    items = (
        db.query(Item)
        .filter(Item.status == ItemStatus.OPEN)
        .filter(
            (Item.snooze_until.is_(None)) | (Item.snooze_until <= datetime.utcnow())
        )
        .all()
    )

    if not items:
        return "Geen items om te synchroniseren."

    # Convert to list of dicts for sync
    items_to_sync = [
        {"name": item.name_raw, "qty": item.qty}
        for item in items
    ]

    # Sync to AH
    ah_service = get_ah_service()
    try:
        results = await ah_service.sync_items(items_to_sync)
    except ValueError as e:
        return f"Fout: {str(e)}"
    except Exception as e:
        return f"AH sync mislukt: {str(e)}"

    # Count results
    synced = sum(1 for r in results if r.status == "ok")
    not_found = sum(1 for r in results if r.status == "not_found")
    failed = sum(1 for r in results if r.status == "error")

    # Build response
    parts = []
    if synced > 0:
        parts.append(f"{synced} items toegevoegd aan Appie")
    if not_found > 0:
        parts.append(f"{not_found} niet gevonden")
    if failed > 0:
        parts.append(f"{failed} mislukt")

    return ". ".join(parts) + "."
