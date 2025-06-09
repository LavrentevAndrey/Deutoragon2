FROM python:3.11-slim

WORKDIR /app

# Копируем сначала файл зависимостей для кеширования слоя
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем остальную часть приложения
COPY . /app

# Порт, который Streamlit использует по умолчанию
EXPOSE 8501

# Команда для запуска Streamlit приложения
# Используем server.port и server.address для Docker
# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health # Типичный healthcheck для Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]