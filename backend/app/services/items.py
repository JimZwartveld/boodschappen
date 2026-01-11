"""Item service for business logic."""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.item import Item, ItemStatus
from app.models.category import Category
from app.services.parser import parse_items, normalize_name, ParsedItem
from app.schemas.item import ItemsAddRequest, ItemsAddResponse, AddedItem, ItemUpdateRequest


class ItemService:
    """Service for item operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_items(
        self,
        status: ItemStatus | None = None,
        category_id: str | None = None,
        include_snoozed: bool = False,
    ) -> list[Item]:
        """Get items with optional filters."""
        query = self.db.query(Item)

        if status:
            query = query.filter(Item.status == status)
        else:
            # By default, exclude removed items
            query = query.filter(Item.status != ItemStatus.REMOVED)

        if category_id:
            query = query.filter(Item.category_id == category_id)

        if not include_snoozed:
            # Exclude snoozed items (snooze_until in future)
            query = query.filter(
                (Item.snooze_until.is_(None)) | (Item.snooze_until <= datetime.utcnow())
            )

        # Order by category sort order, then by name
        query = query.outerjoin(Category).order_by(
            Category.sort_order.nulls_last(),
            Item.name_norm,
        )

        return query.all()

    def get_item(self, item_id: str) -> Item | None:
        """Get a single item by ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()

    def add_items(self, request: ItemsAddRequest) -> ItemsAddResponse:
        """Add items from text input."""
        parsed_items = parse_items(request.text)
        added_items: list[AddedItem] = []

        # Get category if specified
        category_id = None
        if request.category:
            category = (
                self.db.query(Category)
                .filter(Category.name == request.category)
                .first()
            )
            if category:
                category_id = category.id

        for parsed in parsed_items:
            name_norm = normalize_name(parsed.name)

            # Check for existing item with same normalized name
            existing = (
                self.db.query(Item)
                .filter(Item.name_norm == name_norm)
                .filter(Item.status != ItemStatus.REMOVED)
                .first()
            )

            if existing:
                # Merge: increase quantity, update last_added_at
                existing.qty += parsed.qty
                existing.last_added_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()

                # If it was checked, reopen it
                if existing.status == ItemStatus.CHECKED:
                    existing.status = ItemStatus.OPEN

                # Update category if provided and item has none
                if category_id and not existing.category_id:
                    existing.category_id = category_id

                # Update store preference if provided
                if request.preferred_store and not existing.preferred_store:
                    existing.preferred_store = request.preferred_store

                added_items.append(
                    AddedItem(
                        id=existing.id,
                        name=existing.name_raw,
                        qty=existing.qty,
                        unit=existing.unit,
                        is_new=False,
                    )
                )
            else:
                # Create new item
                item = Item(
                    name_raw=parsed.name,
                    name_norm=name_norm,
                    qty=parsed.qty,
                    unit=parsed.unit,
                    category_id=category_id,
                    preferred_store=request.preferred_store,
                    status=ItemStatus.OPEN,
                )
                self.db.add(item)
                self.db.flush()  # Get the ID

                added_items.append(
                    AddedItem(
                        id=item.id,
                        name=item.name_raw,
                        qty=item.qty,
                        unit=item.unit,
                        is_new=True,
                    )
                )

        self.db.commit()

        # Create Dutch confirmation message
        count = len(added_items)
        if count == 1:
            message = f"1 item toegevoegd: {added_items[0].name}"
        else:
            names = ", ".join(item.name for item in added_items[:3])
            if count > 3:
                names += f" en {count - 3} meer"
            message = f"{count} items toegevoegd: {names}"

        return ItemsAddResponse(
            count=count,
            items=added_items,
            message=message,
        )

    def check_item(self, item_id: str) -> Item | None:
        """Mark an item as checked."""
        item = self.get_item(item_id)
        if item:
            item.status = ItemStatus.CHECKED
            item.updated_at = datetime.utcnow()
            self.db.commit()
        return item

    def uncheck_item(self, item_id: str) -> Item | None:
        """Mark an item as open (unchecked)."""
        item = self.get_item(item_id)
        if item:
            item.status = ItemStatus.OPEN
            item.updated_at = datetime.utcnow()
            self.db.commit()
        return item

    def update_item(self, item_id: str, update: ItemUpdateRequest) -> Item | None:
        """Update an item."""
        item = self.get_item(item_id)
        if not item:
            return None

        if update.name_raw is not None:
            item.name_raw = update.name_raw
            item.name_norm = normalize_name(update.name_raw)

        if update.qty is not None:
            item.qty = update.qty

        if update.unit is not None:
            item.unit = update.unit if update.unit else None

        if update.notes is not None:
            item.notes = update.notes if update.notes else None

        if update.category_id is not None:
            item.category_id = update.category_id if update.category_id else None

        if update.preferred_store is not None:
            item.preferred_store = update.preferred_store

        if update.snooze_until is not None:
            item.snooze_until = update.snooze_until

        item.updated_at = datetime.utcnow()
        self.db.commit()
        return item

    def delete_item(self, item_id: str) -> bool:
        """Delete (mark as removed) an item."""
        item = self.get_item(item_id)
        if item:
            item.status = ItemStatus.REMOVED
            item.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
