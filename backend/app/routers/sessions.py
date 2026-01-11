"""Sessions API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.session import SessionResponse, SessionStartRequest, SessionCloseRequest
from app.services.sessions import SessionService

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionResponse])
async def list_sessions(limit: int = 20, db: Session = Depends(get_db)):
    """List recent sessions."""
    service = SessionService(db)
    sessions = service.get_sessions(limit=limit)

    # Add stats to each session
    result = []
    for session in sessions:
        stats = service.get_session_stats(session)
        result.append(
            SessionResponse(
                id=session.id,
                store=session.store,
                started_at=session.started_at,
                closed_at=session.closed_at,
                close_policy=session.close_policy,
                item_count=stats["item_count"],
                checked_count=stats["checked_count"],
            )
        )
    return result


@router.post(":start", response_model=SessionResponse)
async def start_session(request: SessionStartRequest, db: Session = Depends(get_db)):
    """Start a new shopping session."""
    service = SessionService(db)
    session = service.start_session(request)
    stats = service.get_session_stats(session)
    return SessionResponse(
        id=session.id,
        store=session.store,
        started_at=session.started_at,
        closed_at=session.closed_at,
        close_policy=session.close_policy,
        item_count=stats["item_count"],
        checked_count=stats["checked_count"],
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a single session."""
    service = SessionService(db)
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessie niet gevonden")
    stats = service.get_session_stats(session)
    return SessionResponse(
        id=session.id,
        store=session.store,
        started_at=session.started_at,
        closed_at=session.closed_at,
        close_policy=session.close_policy,
        item_count=stats["item_count"],
        checked_count=stats["checked_count"],
    )


@router.post("/{session_id}:close", response_model=SessionResponse)
async def close_session(
    session_id: str,
    request: SessionCloseRequest,
    db: Session = Depends(get_db),
):
    """Close a session with the specified policy."""
    service = SessionService(db)
    session = service.close_session(session_id, request)
    if not session:
        raise HTTPException(status_code=404, detail="Sessie niet gevonden")
    stats = service.get_session_stats(session)
    return SessionResponse(
        id=session.id,
        store=session.store,
        started_at=session.started_at,
        closed_at=session.closed_at,
        close_policy=session.close_policy,
        item_count=stats["item_count"],
        checked_count=stats["checked_count"],
    )


@router.post("/{session_id}/items/{item_id}:check")
async def check_session_item(
    session_id: str,
    item_id: str,
    db: Session = Depends(get_db),
):
    """Check an item within a session."""
    service = SessionService(db)
    session_item = service.check_session_item(session_id, item_id)
    if not session_item:
        raise HTTPException(status_code=404, detail="Item niet gevonden in sessie")
    return {"message": "Item afgevinkt"}
