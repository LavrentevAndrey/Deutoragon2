import secrets
import bcrypt # Импортируем bcrypt

API_KEY_LENGTH = 32 # Длина генерируемого API ключа (до хеширования)

def generate_api_key() -> str:
    """Генерирует случайный безопасный API ключ."""
    return secrets.token_urlsafe(API_KEY_LENGTH)

def hash_api_key(api_key: str) -> str:
    """Хеширует API ключ с использованием bcrypt."""
    api_key_bytes = api_key.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(api_key_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_api_key(plain_api_key: str, hashed_api_key_from_db: str) -> bool:
    """
    Проверяет обычный API ключ путем сравнения с его хешем, хранящимся в БД.
    """
    plain_api_key_bytes = plain_api_key.encode('utf-8')
    hashed_api_key_from_db_bytes = hashed_api_key_from_db.encode('utf-8')

    try:
        return bcrypt.checkpw(plain_api_key_bytes, hashed_api_key_from_db_bytes)
    except Exception as e:
        print(f"Error during bcrypt.checkpw: {e}")
        return False