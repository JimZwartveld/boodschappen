"""Categories API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return categories
