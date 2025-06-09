# Database Security Platform

Проект для мониторинга и управления безопасностью баз данных.

## Технологический стек
- Backend: FastAPI, Python
- ORM: SQLModel
- База данных: PostgreSQL
- Frontend (Admin Panel): Streamlit
- Контейнеризация: Docker, Docker-compose

## Структура проекта
```
database_security_platform/
├── backend/                     # Серверное приложение FastAPI
│   ├── app/                     # Основной код приложения
│   ├── tests/                   # Тесты для backend
│   ├── Dockerfile
│   └── requirements.txt
├── frontend_admin/              # Панель администратора на Streamlit
│   ├── pages/
│   ├── app.py
│   ├── utils/
│   ├── Dockerfile
│   └── requirements.txt
├── client_agent_example/        # Тестовое клиентское приложение
│   ├── client.py
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore
```

## Запуск проекта
1. Скопируйте `.env.example` в `.env` и настройте переменные окружения:
   `cp .env.example .env`
2. Соберите и запустите контейнеры:
   `docker-compose up --build -d`

После запуска:
- Backend API будет доступен по адресу: `http://localhost:8000` (или другой порт, если настроен)
- Документация API (Swagger UI): `http://localhost:8000/docs`
- Панель администратора Streamlit: `http://localhost:8501`
