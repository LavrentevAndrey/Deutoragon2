from typing import List, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.models.event import SecurityEventCreate, SecurityEventRead
from app.crud import crud_event
from app.api.deps import DBSession, AuthenticatedClient

router = APIRouter()

@router.post("/events", response_model=List[SecurityEventRead], status_code=status.HTTP_201_CREATED)
def submit_security_events(
    *,
    session: DBSession,
    events_in: List[SecurityEventCreate], # Клиент может отправить пачку событий
    current_client: AuthenticatedClient,
) -> Any:
    if not events_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No events provided."
        )
    created_events = crud_event.create_multiple_events(session=session, events_in=events_in, client=current_client)
    return created_events


# --- Admin-like Endpoints (пока без явной админской аутентификации) ---

@router.get("/admin/events", response_model=List[SecurityEventRead])
def read_security_events_log(
    session: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    client_id: Optional[UUID] = Query(None),
    event_type: Optional[str] = Query(None, max_length=100),
    severity: Optional[str] = Query(None, max_length=50),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering (ISO format)"),
) -> Any:
    events = crud_event.get_events(
        session=session,
        skip=skip,
        limit=limit,
        client_id=client_id,
        event_type=event_type,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
    )
    return events
