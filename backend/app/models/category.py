"""Category model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """Grocery category."""

    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    name_nl = Column(String(100), nullable=False)
    icon = Column(String(10), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name_nl}>"


# Default categories to seed
DEFAULT_CATEGORIES = [
    {"name": "produce", "name_nl": "Groente & Fruit", "icon": "\U0001F96C", "sort_order": 1},
    {"name": "dairy", "name_nl": "Zuivel", "icon": "\U0001F95B", "sort_order": 2},
    {"name": "meat", "name_nl": "Vlees & Vis", "icon": "\U0001F969", "sort_order": 3},
    {"name": "bakery", "name_nl": "Brood & Gebak", "icon": "\U0001F35E", "sort_order": 4},
    {"name": "frozen", "name_nl": "Diepvries", "icon": "\U0001F9CA", "sort_order": 5},
    {"name": "pantry", "name_nl": "Voorraadkast", "icon": "\U0001F96B", "sort_order": 6},
    {"name": "beverages", "name_nl": "Dranken", "icon": "\U0001F964", "sort_order": 7},
    {"name": "snacks", "name_nl": "Snacks & Snoep", "icon": "\U0001F37F", "sort_order": 8},
    {"name": "household", "name_nl": "Huishouden", "icon": "\U0001F9F9", "sort_order": 9},
    {"name": "personal_care", "name_nl": "Verzorging", "icon": "\U0001F9F4", "sort_order": 10},
    {"name": "other", "name_nl": "Overig", "icon": "\U0001F4E6", "sort_order": 99},
]
