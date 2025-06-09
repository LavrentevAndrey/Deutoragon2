import secrets
from passlib.context import CryptContext

# Контекст для хеширования паролей/ключей
# Используем bcrypt, он достаточно надежен
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

API_KEY_LENGTH = 32 # Длина генерируемого API ключа (до хеширования)

def generate_api_key() -> str:
    """Генерирует случайный безопасный API ключ."""
    return secrets.token_urlsafe(API_KEY_LENGTH)

def hash_api_key(api_key: str) -> str:
    """Хеширует API ключ."""
    return pwd_context.hash(api_key)

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Проверяет обычный API ключ путем сравнения с его хешем."""
    return pwd_context.verify(plain_api_key, hashed_api_key)