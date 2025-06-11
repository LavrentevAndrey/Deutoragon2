import streamlit as st
import pandas as pd
from utils import api_client
from datetime import datetime, timedelta

st.set_page_config(page_title="Events Log", layout="wide")

st.title("Лог Событий Безопасности")
st.markdown("Просмотр событий безопасности, зарегистрированных клиентами.")

# --- Фильтры ---
st.sidebar.header("Фильтры событий")
clients_list_for_filter = api_client.get_clients(limit=1000) # Получаем всех клиентов для фильтра
client_options = {client['client_name']: client['id'] for client in clients_list_for_filter}
client_options["Все клиенты"] = None # Опция для отсутствия фильтра по клиенту

selected_client_name = st.sidebar.selectbox(
    "Клиент:",
    options=list(client_options.keys()),
    index=0 # По умолчанию "Все клиенты"
)
filter_client_id = client_options[selected_client_name]

filter_event_type = st.sidebar.text_input("Тип события (e.g., login_failure):")
filter_severity = st.sidebar.selectbox(
    "Уровень серьезности:",
    options=["", "low", "medium", "high", "critical"], # Пустая строка для отсутствия фильтра
    index=0
)

# Фильтр по дате
st.sidebar.subheader("Период")
date_range_options = {
    "Все время": (None, None),
    "Сегодня": (datetime.now().date(), datetime.now().date()),
    "Последние 7 дней": (datetime.now().date() - timedelta(days=6), datetime.now().date()),
    "Последние 30 дней": (datetime.now().date() - timedelta(days=29), datetime.now().date()),
    "Выбрать диапазон": "custom"
}
selected_date_range_key = st.sidebar.selectbox("Выберите период:", options=list(date_range_options.keys()))

filter_start_date, filter_end_date = None, None

if selected_date_range_key == "Выбрать диапазон":
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        filter_start_date = st.date_input("Дата начала", value=None)
    with col_end:
        filter_end_date = st.date_input("Дата окончания", value=None)
else:
    start_d, end_d = date_range_options[selected_date_range_key]
    filter_start_date = start_d
    filter_end_date = end_d


# Пагинация
limit_per_page = st.sidebar.slider("Событий на странице:", 10, 200, 25, key="events_limit")
if 'event_page_number' not in st.session_state:
    st.session_state.event_page_number = 0

skip = st.session_state.event_page_number * limit_per_page

# --- Загрузка и отображение событий ---
with st.spinner("Загрузка событий..."):
    events_list = api_client.get_events(
        skip=skip,
        limit=limit_per_page,
        client_id=str(filter_client_id) if filter_client_id else None,
        event_type=filter_event_type if filter_event_type else None,
        severity=filter_severity if filter_severity else None,
        start_date=filter_start_date.isoformat() if filter_start_date else None,
        # Для end_date добавляем время конца дня, чтобы включить весь день
        end_date=(datetime.combine(filter_end_date, datetime.max.time()).isoformat()) if filter_end_date else None
    )

if events_list:
    events_df = pd.DataFrame(events_list)
    # Форматирование некоторых полей для лучшего отображения
    if 'timestamp' in events_df.columns:
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Добавляем имя клиента для удобства, если есть client_id
    # Это потребует дополнительного запроса или предварительной загрузки имен клиентов
    # Для простоты пока оставим client_id
    
    columns_ordered = ['id', 'timestamp', 'client_id', 'event_type', 'severity', 'source_ip', 'db_name_target', 'details']
    display_columns = [col for col in columns_ordered if col in events_df.columns]
    
    st.dataframe(events_df[display_columns], use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.event_page_number > 0:
            if st.button("⬅️ Предыдущая страница", key="prev_events"):
                st.session_state.event_page_number -= 1
                st.rerun()
    with col2:
        if len(events_list) == limit_per_page:
            if st.button("Следующая страница ➡️", key="next_events"):
                st.session_state.event_page_number += 1
                st.rerun()
        elif not events_list and st.session_state.event_page_number > 0:
            st.info("Больше нет событий. Возможно, стоит вернуться.")

elif not events_list and st.session_state.event_page_number > 0 :
     st.info("Нет событий на этой странице. Попробуйте вернуться или изменить фильтры.")
     if st.button("⬅️ Вернуться на предыдущую (события)"):
        st.session_state.event_page_number -= 1
        st.rerun()
else:
    st.info("Событий по указанным фильтрам не найдено.")


if st.sidebar.button("Применить фильтры и обновить"):
    st.session_state.event_page_number = 0 # Сбрасываем на первую страницу при новых фильтрах
    st.rerun()