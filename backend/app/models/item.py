"""Item model."""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base


class ItemStatus(str, Enum):
    """Item status."""

    OPEN = "open"
    CHECKED = "checked"
    REMOVED = "removed"


class Store(str, Enum):
    """Preferred store."""

    AH = "AH"
    JUMBO = "Jumbo"


class Item(Base):
    """Grocery item."""

    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name_raw = Column(String(255), nullable=False)
    name_norm = Column(String(255), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    qty = Column(Float, default=1.0)
    unit = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.OPEN, nullable=False)
    preferred_store = Column(SQLEnum(Store), nullable=True)
    snooze_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="items")
    session_items = relationship("SessionItem", back_populates="item")

    def __repr__(self):
        return f"<Item {self.name_raw} ({self.qty}{self.unit or ''})>"
