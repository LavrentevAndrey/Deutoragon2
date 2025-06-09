# backend/app/crud/crud_command.py
from typing import List, Optional, Any
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.models.command import Command, CommandCreate, CommandUpdateByClient, CommandUpdateByAdmin
from app.models.client import Client # Для type hinting

def create_command(session: Session, *, command_in: CommandCreate, client_id: UUID) -> Command:
    db_command = Command.model_validate(command_in) # Используем model_validate
    db_command.client_id = client_id # Убеждаемся, что client_id установлен
    db_command.created_at = datetime.now(timezone.utc)
    db_command.updated_at = datetime.now(timezone.utc)
    # status по умолчанию "pending_dispatch" из модели
    
    session.add(db_command)
    session.commit()
    session.refresh(db_command)
    return db_command

def get_command(session: Session, command_id: UUID) -> Optional[Command]:
    return session.get(Command, command_id)

def get_commands_for_client(
    session: Session,
    client_id: UUID,
    status: Optional[str] = "pending_dispatch", # По умолчанию ищем команды, ожидающие отправки
    skip: int = 0,
    limit: int = 100
) -> List[Command]:
    statement = select(Command).where(Command.client_id == client_id)
    if status:
        statement = statement.where(Command.status == status)
    
    statement = statement.order_by(Command.created_at.asc()).offset(skip).limit(limit) # Сначала старые
    commands = session.exec(statement).all()
    return commands

def get_all_commands(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> List[Command]:
    statement = select(Command).order_by(Command.created_at.desc()) # Сначала новые

    if client_id:
        statement = statement.where(Command.client_id == client_id)
    if status:
        statement = statement.where(Command.status == status)
    
    commands = session.exec(statement.offset(skip).limit(limit)).all()
    return commands

def update_command_status_by_client(
    session: Session,
    *,
    db_command: Command,
    command_update_data: CommandUpdateByClient
) -> Command:
    db_command.status = command_update_data.status
    if command_update_data.execution_result is not None:
        db_command.execution_result = command_update_data.execution_result
    db_command.updated_at = datetime.now(timezone.utc)
    
    session.add(db_command)
    session.commit()
    session.refresh(db_command)
    return db_command

def update_command_by_admin( # Если админу нужно будет что-то менять в существующей команде
    session: Session,
    *,
    db_command: Command,
    command_update_data: CommandUpdateByAdmin
) -> Command:
    update_data = command_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_command, key, value)
    db_command.updated_at = datetime.now(timezone.utc)
    
    session.add(db_command)
    session.commit()
    session.refresh(db_command)
    return db_command

def mark_commands_as_dispatched(session: Session, commands: List[Command]) -> List[Command]:
    updated_commands = []
    for command in commands:
        if command.status == "pending_dispatch":
            command.status = "dispatched"
            command.updated_at = datetime.now(timezone.utc)
            session.add(command)
            updated_commands.append(command)
    if updated_commands: # Коммитим только если были изменения
        session.commit()
        for cmd in updated_commands: # Обновляем для получения актуальных данных
            session.refresh(cmd)
    return updated_commands