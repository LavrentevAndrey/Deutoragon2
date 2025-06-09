from typing import List, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status, Query

from app.models.command import CommandCreate, CommandRead, CommandUpdateByClient, CommandUpdateByAdmin
from app.crud import crud_command, crud_client # Добавляем crud_client для проверки существования
from app.api.deps import DBSession, AuthenticatedClient

router = APIRouter()

# --- Admin-like Endpoints ---

@router.post("/admin/commands", response_model=CommandRead, status_code=status.HTTP_201_CREATED)
def create_new_command_for_client(
    *,
    session: DBSession,
    command_in: CommandCreate, # В command_in должен быть client_id
) -> Any:
    """
    Администратор создает новую команду для указанного клиента.
    `command_in` должен содержать `client_id`.
    """
    # Проверяем, существует ли клиент
    client = crud_client.get_client(session=session, client_id=command_in.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {command_in.client_id} not found. Cannot create command."
        )
    
    # Проверяем, активен ли клиент перед отправкой команды (опционально)
    if client.status != "active":
        # Можно либо выдавать ошибку, либо создавать команду, но она не будет получена
        # пока клиент не станет активным. Для начала, будем создавать.
        pass # log a warning maybe? "Client is not active, command will be pending."

    command = crud_command.create_command(session=session, command_in=command_in, client_id=command_in.client_id)
    return command


@router.get("/admin/commands", response_model=List[CommandRead])
def read_all_system_commands(
    session: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    client_id: Optional[UUID] = Query(None, description="Filter by Client ID"),
    status: Optional[str] = Query(None, description="Filter by command status"),
) -> Any:
    """
    Получает список всех команд в системе с возможностью фильтрации.
    """
    commands = crud_command.get_all_commands(
        session=session, skip=skip, limit=limit, client_id=client_id, status=status
    )
    return commands


@router.get("/admin/commands/{command_id}", response_model=CommandRead)
def read_specific_command_by_id(
    command_id: UUID,
    session: DBSession,
) -> Any:
    """
    Получает детали конкретной команды по ее ID.
    """
    command = crud_command.get_command(session=session, command_id=command_id)
    if not command:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Command not found")
    return command

@router.get("/commands", response_model=List[CommandRead])
def fetch_pending_commands_for_client(
    current_client: AuthenticatedClient, # Аутентифицированный клиент
    session: DBSession,
    limit: int = Query(10, ge=1, le=50, description="Max number of commands to fetch")
) -> Any:
    """
    Клиент запрашивает новые команды, ожидающие выполнения (`pending_dispatch`).
    Сервер возвращает команды и меняет их статус на `dispatched`.
    Требует валидный X-API-Key.
    """
    pending_commands = crud_command.get_commands_for_client(
        session=session, client_id=current_client.id, status="pending_dispatch", limit=limit
    )
    
    if not pending_commands:
        return [] # Возвращаем пустой список, если нет команд

    # Меняем статус команд на 'dispatched'
    dispatched_commands = crud_command.mark_commands_as_dispatched(session=session, commands=pending_commands)
    
    return dispatched_commands


@router.patch("/commands/{command_id}", response_model=CommandRead)
def update_command_status_by_client_agent(
    command_id: UUID,
    command_update_data: CommandUpdateByClient, # Статус и результат
    current_client: AuthenticatedClient,
    session: DBSession,
) -> Any:
    """
    Клиент обновляет статус выполнения команды (e.g., acknowledged, in_progress, completed, failed).
    Требует валидный X-API-Key.
    """
    db_command = crud_command.get_command(session=session, command_id=command_id)
    if not db_command:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Command not found")

    # Убедимся, что команда принадлежит этому клиенту
    if db_command.client_id != current_client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this command"
        )
    
    if db_command.status == "completed" or db_command.status == "failed":
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Command is already in a final state: {db_command.status}"
        )

    updated_command = crud_command.update_command_status_by_client(
        session=session, db_command=db_command, command_update_data=command_update_data
    )
    return updated_command