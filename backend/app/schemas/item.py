"""Item schemas."""
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.item import ItemStatus, Store
from app.schemas.category import CategoryResponse


class ItemResponse(BaseModel):
    """Item response."""

    id: str
    name_raw: str
    name_norm: str
    category: CategoryResponse | None
    qty: float
    unit: str | None
    notes: str | None
    status: ItemStatus
    preferred_store: Store | None
    snooze_until: datetime | None
    created_at: datetime
    updated_at: datetime
    last_added_at: datetime

    class Config:
        from_attributes = True


class ParsedItem(BaseModel):
    """Parsed item from text input."""

    name: str
    qty: float = 1.0
    unit: str | None = None


class ItemsAddRequest(BaseModel):
    """Request to add items."""

    text: str = Field(..., description="Text input with items (comma or newline separated)")
    source: str = Field(default="ui", description="Source: siri, chatgpt, mcp, ui")
    category: str | None = Field(default=None, description="Category name for all items")
    preferred_store: Store | None = Field(default=None, description="Preferred store")


class AddedItem(BaseModel):
    """Item that was added."""

    id: str
    name: str
    qty: float
    unit: str | None
    is_new: bool = True  # False if merged with existing


class ItemsAddResponse(BaseModel):
    """Response after adding items."""

    count: int
    items: list[AddedItem]
    message: str  # Dutch confirmation message


class ItemUpdateRequest(BaseModel):
    """Request to update an item."""

    name_raw: str | None = None
    qty: float | None = None
    unit: str | None = None
    notes: str | None = None
    category_id: str | None = None
    preferred_store: Store | None = None
    snooze_until: datetime | None = None
