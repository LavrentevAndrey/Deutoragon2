from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache # Для кэширования настроек

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Database Security Platform API"

    # PostgreSQL Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Собираем DATABASE_URL из отдельных переменных
    # SQLModel / SQLAlchemy используют DATABASE_URL для подключения
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # Ключ для создания/проверки API-ключей клиентов или JWT токенов
    SECRET_KEY: str = "your_super_secret_key_which_should_be_long_and_random"
    # Алгоритм для JWT токенов, если будем использовать
    ALGORITHM: str = "HS256"
    # Время жизни токена доступа (например, для админки)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache() # Кэшируем результат функции, чтобы настройки читались один раз
def get_settings() -> Settings:
    return Settings()

settings = get_settings()