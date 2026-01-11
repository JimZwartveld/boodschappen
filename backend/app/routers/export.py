"""Export API endpoints."""
from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item, ItemStatus, Store
from app.models.category import Category

router = APIRouter(prefix="/api/v1/export", tags=["export"])


class ExportFormat(str, Enum):
    PLAINTEXT = "plaintext"
    JSON = "json"


def format_item_line(item: Item) -> str:
    """Format a single item for plaintext export."""
    qty_str = ""
    if item.qty != 1:
        if item.qty == int(item.qty):
            qty_str = f"{int(item.qty)}x "
        else:
            qty_str = f"{item.qty}x "

    unit_str = ""
    if item.unit:
        unit_str = f" ({item.unit})"

    return f"- {qty_str}{item.name_raw}{unit_str}"


@router.get("/{store}")
async def export_items(
    store: str,
    format: ExportFormat = Query(default=ExportFormat.PLAINTEXT),
    include_checked: bool = Query(default=False),
    include_snoozed: bool = Query(default=False),
    simple: bool = Query(default=False, description="Simple list without headers (for Siri)"),
    db: Session = Depends(get_db),
):
    """Export items for a specific store."""
    # Parse store
    store_enum = None
    if store.upper() == "AH":
        store_enum = Store.AH
    elif store.upper() == "JUMBO":
        store_enum = Store.JUMBO
    # else: generic export

    # Build query
    query = db.query(Item)

    # Filter by status
    if include_checked:
        query = query.filter(Item.status.in_([ItemStatus.OPEN, ItemStatus.CHECKED]))
    else:
        query = query.filter(Item.status == ItemStatus.OPEN)

    # Filter snoozed
    if not include_snoozed:
        query = query.filter(
            (Item.snooze_until.is_(None)) | (Item.snooze_until <= datetime.utcnow())
        )

    # Filter by store preference
    if store_enum:
        query = query.filter(
            (Item.preferred_store.is_(None)) | (Item.preferred_store == store_enum)
        )

    # Order by category, then name
    query = query.outerjoin(Category).order_by(
        Category.sort_order.nulls_last(),
        Item.name_norm,
    )

    items = query.all()

    if format == ExportFormat.JSON:
        return {
            "store": store,
            "exported_at": datetime.utcnow().isoformat(),
            "count": len(items),
            "items": [
                {
                    "id": item.id,
                    "name": item.name_raw,
                    "qty": item.qty,
                    "unit": item.unit,
                    "category": item.category.name_nl if item.category else None,
                    "status": item.status.value,
                }
                for item in items
            ],
        }

    # Simple format for Siri - just item names
    if simple:
        if not items:
            return PlainTextResponse("Je boodschappenlijst is leeg.")

        item_names = []
        for item in items:
            if item.qty != 1:
                qty = int(item.qty) if item.qty == int(item.qty) else item.qty
                item_names.append(f"{qty} {item.name_raw}")
            else:
                item_names.append(item.name_raw)

        return PlainTextResponse(", ".join(item_names))

    # Plaintext format - group by category
    lines = []
    current_category = None

    for item in items:
        category_name = item.category.name_nl if item.category else "Overig"

        if category_name != current_category:
            if current_category is not None:
                lines.append("")  # Empty line between categories
            lines.append(f"## {category_name}")
            current_category = category_name

        lines.append(format_item_line(item))

    # Add header
    store_name = store.upper() if store.upper() in ["AH", "JUMBO"] else "Boodschappen"
    header = f"# {store_name} ({len(items)} items)\n"

    return PlainTextResponse(header + "\n".join(lines))
