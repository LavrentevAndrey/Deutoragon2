from sqlmodel import create_engine, SQLModel, Session
from typing import Generator

from app.core.config import settings

# Строка подключения к базе данных из настроек
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True) 


def create_db_and_tables():
    import app.models.client
    import app.models.event
    import app.models.command

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session