from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.models.client import Client, ClientCreate
from app.core.security import generate_api_key, hash_api_key

def create_client_with_api_key(session: Session, *, client_in: ClientCreate) -> tuple[Client, str]:
    """
    Создает нового клиента, генерирует для него API ключ, хеширует ключ и сохраняет в БД.
    Возвращает созданного клиента и НЕХЕШИРОВАННЫЙ API ключ.
    """
    plain_api_key = generate_api_key()
    hashed_api_key = hash_api_key(plain_api_key)

    db_client = Client(
        client_name=client_in.client_name,
        ip_address=client_in.ip_address,
        os_info=client_in.os_info,
        status="active", # При регистрации клиент сразу активен
        api_key_hash=hashed_api_key,
        registered_at=datetime.now(timezone.utc)
    )
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client, plain_api_key

def get_client(session: Session, client_id: UUID) -> Optional[Client]:
    """Получает клиента по его ID."""
    return session.get(Client, client_id)

def get_client_by_name(session: Session, client_name: str) -> Optional[Client]:
    """Получает клиента по его имени."""
    statement = select(Client).where(Client.client_name == client_name)
    return session.exec(statement).first()

def get_clients(session: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """Получает список клиентов с пагинацией."""
    statement = select(Client).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_client_heartbeat(session: Session, client: Client) -> Client:
    """Обновляет время последнего heartbeat для клиента."""
    client.last_heartbeat = datetime.now(timezone.utc)
    client.status = "active" # Если пришел heartbeat, значит активен
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

def get_client_by_hashed_api_key(session: Session, hashed_api_key: str) -> Optional[Client]:
    """Получает клиента по хешированному API ключу. Внутренняя функция."""
    statement = select(Client).where(Client.api_key_hash == hashed_api_key)
    return session.exec(statement).first()