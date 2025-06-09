from fastapi import APIRouter

from app.api.v1.endpoints import clients
from app.api.v1.endpoints import events
from app.api.v1.endpoints import commands

api_router = APIRouter()

api_router.include_router(clients.router, tags=["Clients"])
api_router.include_router(events.router, tags=["Security Events"])
api_router.include_router(commands.router, tags=["Commands"])