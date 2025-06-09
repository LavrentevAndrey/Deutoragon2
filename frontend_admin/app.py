import streamlit as st
from dotenv import load_dotenv

# Загружаем переменные окружения, если они есть (например, URL бэкенда)
load_dotenv()

st.set_page_config(
    page_title="Security Platform Admin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Меню навигации")
# Streamlit автоматически создаст навигацию на основе файлов в папке `pages`

st.title("🛡️ Панель администратора Платформы Безопасности")
st.write("Добро пожаловать в панель администратора. Используйте меню слева для навигации по разделам.")

# Можно добавить немного общей информации или дашборд прямо здесь,
# но основная функциональность будет на отдельных страницах.

st.markdown("---")
st.subheader("О приложении")
st.info(
    """
    Эта панель позволяет управлять клиентами, просматривать события безопасности
    и отправлять команды на зарегистрированные клиентские устройства.
    """
)


import requests
from utils.api_client import BACKEND_URL
try:
    response = requests.get(f"{BACKEND_URL}/") # Проверяем корневой эндпоинт FastAPI
    if response.status_code == 200:
        st.sidebar.success("Backend: Connected")
    else:
        st.sidebar.error(f"Backend: Error ({response.status_code})")
except requests.exceptions.ConnectionError:
    st.sidebar.error("Backend: Connection Failed")