"""Shopping session models."""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.item import Store


class ClosePolicy(str, Enum):
    """Session close policy."""

    KEEP_OPEN = "keep_open"
    SNOOZE_LEFTOVERS = "snooze_leftovers"
    REMOVE_LEFTOVERS = "remove_leftovers"


class SessionItemState(str, Enum):
    """Session item state."""

    EXPORTED = "exported"
    CHECKED = "checked"
    LEFTOVER = "leftover"


class ShoppingSession(Base):
    """Shopping session."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    store = Column(SQLEnum(Store), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    close_policy = Column(SQLEnum(ClosePolicy), nullable=True)

    # Relationships
    session_items = relationship("SessionItem", back_populates="session")

    def __repr__(self):
        return f"<ShoppingSession {self.store} @ {self.started_at}>"


class SessionItem(Base):
    """Item snapshot within a shopping session."""

    __tablename__ = "session_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    item_id = Column(String(36), ForeignKey("items.id"), nullable=False)
    qty_at_export = Column(Float, nullable=False)
    unit_at_export = Column(String(50), nullable=True)
    checked_at = Column(DateTime, nullable=True)
    state = Column(SQLEnum(SessionItemState), default=SessionItemState.EXPORTED, nullable=False)

    # Relationships
    session = relationship("ShoppingSession", back_populates="session_items")
    item = relationship("Item", back_populates="session_items")

    def __repr__(self):
        return f"<SessionItem {self.item_id} in {self.session_id}>"
