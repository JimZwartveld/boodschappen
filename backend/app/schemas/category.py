"""Category schemas."""
from datetime import datetime
from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Category response."""

    id: str
    name: str
    name_nl: str
    icon: str | None
    sort_order: int

    class Config:
        from_attributes = True
