FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей pip
# Копируем только requirements.txt для кеширования этого слоя Docker
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего остального кода приложения
COPY . /app
