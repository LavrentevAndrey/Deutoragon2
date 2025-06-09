import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# Для предотвращения циклических импортов при определении связей
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .event import SecurityEvent
    from .command import Command


class ClientBase(SQLModel):
    client_name: str = Field(unique=True, index=True, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45) # IPv4 or IPv6
    os_info: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="inactive", max_length=50) # e.g., "active", "inactive", "maintenance"


class Client(ClientBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    api_key_hash: str = Field(unique=True, nullable=False) # Хешированный API ключ
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    last_heartbeat: Optional[datetime] = Field(default=None)

    # Связи (Relationships)
    # `sa_relationship_kwargs` используется для настройки каскадного удаления
    events: List["SecurityEvent"] = Relationship(back_populates="client", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    commands: List["Command"] = Relationship(back_populates="client", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ClientCreate(ClientBase):
    # При создании клиента API ключ генерируется отдельно и хешируется
    # client_name обязателен
    pass


class ClientRead(ClientBase):
    id: uuid.UUID
    registered_at: datetime
    last_heartbeat: Optional[datetime]
    # Не отдаем api_key_hash наружу


class ClientReadWithApiKey(ClientRead): # Специальная схема для ответа после создания клиента
    api_key: str # Нехешированный ключ, который отдается клиенту ОДИН РАЗ


class ClientUpdate(SQLModel):
    client_name: Optional[str] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None
    status: Optional[str] = None
    last_heartbeat: Optional[datetime] = None