"""Session service for shopping sessions."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.item import Item, ItemStatus, Store
from app.models.session import ShoppingSession, SessionItem, ClosePolicy, SessionItemState
from app.schemas.session import SessionStartRequest, SessionCloseRequest


class SessionService:
    """Service for shopping session operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_sessions(self, limit: int = 20) -> list[ShoppingSession]:
        """Get recent sessions."""
        return (
            self.db.query(ShoppingSession)
            .order_by(ShoppingSession.started_at.desc())
            .limit(limit)
            .all()
        )

    def get_session(self, session_id: str) -> ShoppingSession | None:
        """Get a single session by ID."""
        return (
            self.db.query(ShoppingSession)
            .filter(ShoppingSession.id == session_id)
            .first()
        )

    def start_session(self, request: SessionStartRequest) -> ShoppingSession:
        """Start a new shopping session."""
        # Create the session
        session = ShoppingSession(store=request.store)
        self.db.add(session)
        self.db.flush()

        # Get open items (respecting store preference)
        query = self.db.query(Item).filter(Item.status == ItemStatus.OPEN)

        # Exclude snoozed items
        query = query.filter(
            (Item.snooze_until.is_(None)) | (Item.snooze_until <= datetime.utcnow())
        )

        # Filter by store preference if specified
        if request.store:
            query = query.filter(
                (Item.preferred_store.is_(None)) | (Item.preferred_store == request.store)
            )

        items = query.all()

        # Create session items snapshot
        for item in items:
            session_item = SessionItem(
                session_id=session.id,
                item_id=item.id,
                qty_at_export=item.qty,
                unit_at_export=item.unit,
                state=SessionItemState.EXPORTED,
            )
            self.db.add(session_item)

        self.db.commit()
        return session

    def close_session(
        self, session_id: str, request: SessionCloseRequest
    ) -> ShoppingSession | None:
        """Close a session with the specified policy."""
        session = self.get_session(session_id)
        if not session:
            return None

        if session.closed_at:
            # Already closed
            return session

        # Apply policy to leftover items
        leftover_items = (
            self.db.query(SessionItem)
            .filter(SessionItem.session_id == session_id)
            .filter(SessionItem.state == SessionItemState.EXPORTED)
            .all()
        )

        for session_item in leftover_items:
            session_item.state = SessionItemState.LEFTOVER

            if request.policy == ClosePolicy.SNOOZE_LEFTOVERS:
                # Snooze the actual item
                item = self.db.query(Item).filter(Item.id == session_item.item_id).first()
                if item:
                    item.snooze_until = datetime.utcnow() + timedelta(days=request.snooze_days)
                    item.updated_at = datetime.utcnow()

            elif request.policy == ClosePolicy.REMOVE_LEFTOVERS:
                # Remove the actual item
                item = self.db.query(Item).filter(Item.id == session_item.item_id).first()
                if item:
                    item.status = ItemStatus.REMOVED
                    item.updated_at = datetime.utcnow()

        # Close the session
        session.closed_at = datetime.utcnow()
        session.close_policy = request.policy
        self.db.commit()

        return session

    def check_session_item(self, session_id: str, item_id: str) -> SessionItem | None:
        """Mark an item as checked within a session."""
        session_item = (
            self.db.query(SessionItem)
            .filter(SessionItem.session_id == session_id)
            .filter(SessionItem.item_id == item_id)
            .first()
        )

        if session_item:
            session_item.state = SessionItemState.CHECKED
            session_item.checked_at = datetime.utcnow()

            # Also check the actual item
            item = self.db.query(Item).filter(Item.id == item_id).first()
            if item:
                item.status = ItemStatus.CHECKED
                item.updated_at = datetime.utcnow()

            self.db.commit()

        return session_item

    def get_session_stats(self, session: ShoppingSession) -> dict:
        """Get statistics for a session."""
        total = (
            self.db.query(SessionItem)
            .filter(SessionItem.session_id == session.id)
            .count()
        )
        checked = (
            self.db.query(SessionItem)
            .filter(SessionItem.session_id == session.id)
            .filter(SessionItem.state == SessionItemState.CHECKED)
            .count()
        )
        return {"item_count": total, "checked_count": checked}
