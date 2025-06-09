from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from app.models.event import SecurityEvent, SecurityEventCreate
from app.models.client import Client # Для type hinting

def create_event(session: Session, *, event_in: SecurityEventCreate, client: Client) -> SecurityEvent:
    """Создает новое событие безопасности, привязанное к клиенту."""
    db_event = SecurityEvent.model_validate(event_in) # Используем model_validate для Pydantic v2+
    db_event.client_id = client.id
    # db_event.timestamp устанавливается по умолчанию в модели или может быть передан в event_in
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

def create_multiple_events(session: Session, *, events_in: List[SecurityEventCreate], client: Client) -> List[SecurityEvent]:
    """Создает несколько событий безопасности для одного клиента."""
    db_events = []
    for event_in in events_in:
        db_event = SecurityEvent.model_validate(event_in)
        db_event.client_id = client.id
        session.add(db_event)
        db_events.append(db_event)
    session.commit()
    for db_event in db_events: # Обновляем каждый объект после коммита, чтобы получить ID и т.д.
        session.refresh(db_event)
    return db_events


def get_events(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[UUID] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[SecurityEvent]:
    """Получает список событий с фильтрацией и пагинацией."""
    statement = select(SecurityEvent).order_by(SecurityEvent.timestamp.desc())

    if client_id:
        statement = statement.where(SecurityEvent.client_id == client_id)
    if event_type:
        statement = statement.where(SecurityEvent.event_type == event_type)
    if severity:
        statement = statement.where(SecurityEvent.severity == severity)
    if start_date:
        statement = statement.where(SecurityEvent.timestamp >= start_date)
    if end_date:
        statement = statement.where(SecurityEvent.timestamp <= end_date)

    events = session.exec(statement.offset(skip).limit(limit)).all()
    return events