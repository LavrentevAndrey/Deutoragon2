from typing import Generator, Annotated, Optional
from fastapi import Header, HTTPException, Depends, status
from sqlmodel import Session

from app.db.database import get_session as get_db_session_gen
from app.models.client import Client
from app.core.security import verify_api_key
from app.crud import crud_client

def get_db() -> Generator[Session, None, None]:
    yield from get_db_session_gen()

DBSession = Annotated[Session, Depends(get_db)]


async def get_current_client(
    session: DBSession, 
    x_api_key: Annotated[str | None, Header()] = None,
) -> Client:
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: API Key is missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    clients = crud_client.get_clients(session, limit=10000) # Осторожно с лимитом в проде
    authenticated_client: Optional[Client] = None
    for client_record in clients:
        if verify_api_key(x_api_key, client_record.api_key_hash):
            authenticated_client = client_record
            break
            
    if authenticated_client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if authenticated_client.status != "active":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client is not active",
        )
        
    return authenticated_client

AuthenticatedClient = Annotated[Client, Depends(get_current_client)]