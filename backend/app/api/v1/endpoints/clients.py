from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status, Body

from app.models.client import ClientCreate, ClientRead, ClientReadWithApiKey, ClientUpdate
from app.crud import crud_client
from app.api.deps import DBSession, AuthenticatedClient # Используем типизированные зависимости

router = APIRouter()

@router.post("/admin/clients", response_model=ClientReadWithApiKey, status_code=status.HTTP_201_CREATED)
def register_new_client(
    *,
    session: DBSession,
    client_in: ClientCreate,
) -> Any:
    existing_client = crud_client.get_client_by_name(session, client_name=client_in.client_name)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this name already exists.",
        )
    
    db_client, plain_api_key = crud_client.create_client_with_api_key(session=session, client_in=client_in)
    
    # Собираем ответ, включая нехешированный API ключ
    response_data = ClientRead.model_validate(db_client).model_dump()
    response_data["api_key"] = plain_api_key
    
    return ClientReadWithApiKey(**response_data)


@router.get("/admin/clients", response_model=List[ClientRead])
def read_clients_list(
    session: DBSession,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    clients = crud_client.get_clients(session=session, skip=skip, limit=limit)
    return clients


@router.get("/admin/clients/{client_id}", response_model=ClientRead)
def read_client_by_id(
    client_id: UUID,
    session: DBSession,
) -> Any:
    client = crud_client.get_client(session=session, client_id=client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

@router.post("/clients/heartbeat", response_model=ClientRead)
def client_heartbeat(
    current_client: AuthenticatedClient, # Зависимость для аутентификации клиента
    session: DBSession,
) -> Any:
    updated_client = crud_client.update_client_heartbeat(session=session, client=current_client)
    return updated_client

# Эндпоинт для обновления информации о клиенте (пока не требуется, но может пригодиться)
# @router.patch("/clients/me", response_model=ClientRead)
# def update_client_info(
#     *,
#     session: DBSession,
#     client_update_data: ClientUpdate,
#     current_client: AuthenticatedClient,
# ) -> Any:
#     """
#     Клиент обновляет информацию о себе (например, IP или OS).
#     """
#     # ... логика обновления ...
#     pass