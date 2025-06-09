import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

# Для предотвращения циклических импортов
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client


class SecurityEventBase(SQLModel):
    event_type: str = Field(index=True, max_length=100) # e.g., "login_failure", "sql_injection_attempt"
    severity: str = Field(index=True, max_length=50)    # e.g., "low", "medium", "high", "critical"
    source_ip: Optional[str] = Field(default=None, max_length=45)
    details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON)) # Хранение произвольных JSON данных
    db_name_target: Optional[str] = Field(default=None, max_length=255)


class SecurityEvent(SecurityEventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    
    client_id: uuid.UUID = Field(foreign_key="client.id", index=True, nullable=False)
    client: Optional["Client"] = Relationship(back_populates="events")


class SecurityEventCreate(SecurityEventBase):
    # client_id будет взят из аутентифицированного клиента (его API ключа)
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityEventRead(SecurityEventBase):
    id: uuid.UUID
    timestamp: datetime
    client_id: uuid.UUID