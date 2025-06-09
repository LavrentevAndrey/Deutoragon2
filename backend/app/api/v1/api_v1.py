from fastapi import APIRouter

from app.api.v1.endpoints import clients, events #, commands (добавим позже)

api_router = APIRouter()

# Подключаем роутеры из отдельных файлов
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"]) # Общий префикс для клиентов
api_router.include_router(events.router, prefix="/events", tags=["Security Events"]) # Общий префикс для событий

from app.api.v1.endpoints import clients as clients_endpoints
from app.api.v1.endpoints import events as events_endpoints
# from app.api.v1.endpoints import commands as commands_endpoints # Когда будет готово

api_router = APIRouter()

# Клиентские эндпоинты
api_router.include_router(clients_endpoints.router, prefix="", tags=["Client Management"])
api_router.include_router(events_endpoints.router, prefix="", tags=["Security Events"])

