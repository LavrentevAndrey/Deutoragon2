FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код агента
COPY ./client.py /app/client.py

CMD ["python", "client.py"]