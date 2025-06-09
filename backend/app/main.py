from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import create_db_and_tables
from app.api.v1.api_v1 import api_router as api_v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    print("Creating database and tables if they don't exist...")
    create_db_and_tables()
    print("Database and tables should be ready.")
    yield
    print("Application shutdown...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # /api/v1/openapi.json
    lifespan=lifespan
)

# Подключение роутеров API
app.include_router(api_v1_router, prefix=settings.API_V1_STR) # <--- ДОБАВЛЕНО (например, /api/v1)


@app.get("/", tags=["Root"]) # Это останется как есть
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}