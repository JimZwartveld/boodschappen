"""Session schemas."""
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.item import Store
from app.models.session import ClosePolicy, SessionItemState


class SessionItemResponse(BaseModel):
    """Session item response."""

    item_id: str
    item_name: str
    qty_at_export: float
    unit_at_export: str | None
    checked_at: datetime | None
    state: SessionItemState

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Session response."""

    id: str
    store: Store | None
    started_at: datetime
    closed_at: datetime | None
    close_policy: ClosePolicy | None
    item_count: int = 0
    checked_count: int = 0

    class Config:
        from_attributes = True


class SessionStartRequest(BaseModel):
    """Request to start a session."""

    store: Store | None = Field(default=None, description="Store: AH, Jumbo, or null for generic")


class SessionCloseRequest(BaseModel):
    """Request to close a session."""

    policy: ClosePolicy = Field(default=ClosePolicy.KEEP_OPEN)
    snooze_days: int = Field(default=7, description="Days to snooze if policy is snooze_leftovers")
