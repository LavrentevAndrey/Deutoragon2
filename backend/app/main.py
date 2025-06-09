from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import create_db_and_tables
# В будущем здесь будут импорты роутеров API
# from app.api.v1.api_v1 import api_router as api_v1_router


# Контекстный менеджер для выполнения действий при запуске и остановке приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняемый при запуске приложения
    print("Application startup...")
    print("Creating database and tables if they don't exist...")
    create_db_and_tables() # Создаем таблицы
    print("Database and tables should be ready.")
    yield
    # Код, выполняемый при остановке приложения
    print("Application shutdown...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan # Используем lifespan для событий запуска/остановки
)

# Подключение роутеров API (пока закомментировано)
# app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Если вы хотите иметь отдельный скрипт для инициализации БД,
# то создайте backend/app/db/init_db.py:
#
# # backend/app/db/init_db.py
# from app.db.database import create_db_and_tables, engine
# from sqlmodel import Session
#
# def init_db():
#     print("Attempting to create database and tables...")
#     # Попытка подключиться для проверки доступности БД перед созданием таблиц
#     try:
#         with Session(engine) as session:
#             session.execute("SELECT 1") # Простой запрос для проверки
#         print("Database connection successful.")
#         create_db_and_tables()
#         print("Tables created successfully (if they didn't exist).")
#     except Exception as e:
#         print(f"Error connecting to database or creating tables: {e}")
#
# if __name__ == "__main__":
# init_db()
#
# И запускайте его отдельно: python -m app.db.init_db
# Но для Docker-окружения, автоматическое создание при старте FastAPI часто удобнее.