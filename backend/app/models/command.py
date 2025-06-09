import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

# Для предотвращения циклических импортов
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client


class CommandBase(SQLModel):
    command_type: str = Field(max_length=100) # e.g., "block_ip", "run_script"
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = Field(default="pending_dispatch", index=True, max_length=50) 
    # e.g., "pending_dispatch", "dispatched", "acknowledged", "in_progress", "completed", "failed", "timeout"
    dispatch_deadline: Optional[datetime] = Field(default=None)
    


class Command(CommandBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        # sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)} # см. комментарий в base_class
        nullable=False
    )
    execution_result: Optional[str] = Field(default=None) # Краткий результат или ошибка

    client_id: uuid.UUID = Field(foreign_key="client.id", index=True, nullable=False)
    client: Optional["Client"] = Relationship(back_populates="commands")


class CommandCreate(CommandBase):
    client_id: uuid.UUID # Указывается при создании команды админом


class CommandRead(CommandBase):
    id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    execution_result: Optional[str]


class CommandUpdateByClient(SQLModel): # Схема для обновления статуса клиентом
    status: str
    execution_result: Optional[str] = None


class CommandUpdateByAdmin(SQLModel): # Схема для админа (если нужно что-то специфичное)
    status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    dispatch_deadline: Optional[datetime] = None