"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.models import Category, Item, ShoppingSession, SessionItem
from app.models.category import DEFAULT_CATEGORIES
from app.routers import (
    health_router,
    categories_router,
    items_router,
    sessions_router,
    export_router,
    sync_router,
)

settings = get_settings()


def seed_categories(db):
    """Seed default categories if they don't exist."""
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: create tables and seed data
    Base.metadata.create_all(bind=engine)

    # Seed categories
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()

    yield

    # Shutdown: nothing to do


app = FastAPI(
    title="Boodschappen API",
    description="Groceries list API for the Boodschappen app",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(categories_router)
app.include_router(items_router)
app.include_router(sessions_router)
app.include_router(export_router)
app.include_router(sync_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Boodschappen API",
        "version": "0.1.0",
        "docs": "/docs",
    }
