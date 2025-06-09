import streamlit as st
import pandas as pd
from utils import api_client # Используем наш api_client

st.set_page_config(page_title="Clients Dashboard", layout="wide")

st.title("Клиенты")
st.markdown("Управление зарегистрированными клиентами и их API-ключами.")

# --- Секция регистрации нового клиента ---
with st.expander("Регистрация нового клиента", expanded=False):
    with st.form("new_client_form"):
        client_name = st.text_input("Имя клиента (уникальное)", key="nc_name")
        os_info = st.text_input("Информация об ОС (например, 'Windows 10 Pro')", key="nc_os")
        ip_address = st.text_input("IP-адрес (опционально)", key="nc_ip")
        
        submitted = st.form_submit_button("Зарегистрировать клиента")
        if submitted:
            if not client_name:
                st.error("Имя клиента обязательно для заполнения.")
            else:
                with st.spinner("Регистрация клиента..."):
                    client_data = api_client.register_client(client_name, ip_address if ip_address else None, os_info if os_info else None)
                if client_data and "api_key" in client_data:
                    st.success(f"Клиент '{client_data.get('client_name')}' успешно зарегистрирован!")
                    st.info(f"ID клиента: {client_data.get('id')}")
                    st.warning(f"ВАЖНО: Сохраните этот API ключ. Он отображается только один раз: `{client_data.get('api_key')}`")
                    # Очищаем поля формы (Streamlit не делает это автоматически для text_input внутри form после успеха)
                    # Можно использовать session_state для сброса, но для простоты пока оставим так.
                    # st.session_state.nc_name = ""
                    # st.session_state.nc_os = ""
                    # st.session_state.nc_ip = ""
                    st.experimental_rerun() # Перезагружаем страницу для обновления списка и очистки
                elif client_data:
                     st.error(f"Ошибка при регистрации: {client_data.get('detail', 'Неизвестная ошибка от сервера')}")
                else:
                    st.error("Не удалось зарегистрировать клиента. Проверьте логи сервера.")


st.markdown("---")
# --- Секция отображения списка клиентов ---
st.subheader("Список зарегистрированных клиентов")

# Пагинация (простая)
limit_per_page = st.slider("Клиентов на странице:", 5, 50, 10)
if 'client_page_number' not in st.session_state:
    st.session_state.client_page_number = 0

skip = st.session_state.client_page_number * limit_per_page

clients_list = api_client.get_clients(skip=skip, limit=limit_per_page)

if clients_list:
    # Убираем api_key_hash из отображения, если он есть
    clients_df_data = [{k: v for k, v in client.items() if k != 'api_key_hash'} for client in clients_list]
    clients_df = pd.DataFrame(clients_df_data)
    
    # Можно настроить порядок и видимость колонок
    columns_ordered = ['id', 'client_name', 'status', 'ip_address', 'os_info', 'registered_at', 'last_heartbeat']
    display_columns = [col for col in columns_ordered if col in clients_df.columns]
    
    st.dataframe(clients_df[display_columns], use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.client_page_number > 0:
            if st.button("⬅️ Предыдущая страница"):
                st.session_state.client_page_number -= 1
                st.experimental_rerun()
    with col2:
        # Для простоты, предполагаем, что если вернулось меньше лимита, то это последняя страница
        # В идеале, API должен возвращать общее количество для точной пагинации
        if len(clients_list) == limit_per_page:
             if st.button("Следующая страница ➡️"):
                st.session_state.client_page_number += 1
                st.experimental_rerun()
        elif not clients_list and st.session_state.client_page_number > 0: # Если на текущей странице нет данных, а мы не на первой
            st.info("Больше нет клиентов. Возможно, стоит вернуться на предыдущую страницу.")


    # --- Детали клиента (опционально) ---
    st.markdown("---")
    st.subheader("Просмотр деталей клиента")
    if clients_list:
        client_ids = {client['client_name']: client['id'] for client in clients_list}
        selected_client_name_for_details = st.selectbox(
            "Выберите клиента для просмотра деталей:",
            options=client_ids.keys(),
            key="client_details_select"
        )
        if selected_client_name_for_details:
            selected_client_id = client_ids[selected_client_name_for_details]
            if st.button(f"Показать детали для {selected_client_name_for_details}", key="show_details_btn"):
                with st.spinner(f"Загрузка деталей для клиента {selected_client_id}..."):
                    details = api_client.get_client_details(selected_client_id)
                if details:
                    st.json(details)
                else:
                    st.error("Не удалось загрузить детали клиента.")
    else:
        st.info("Нет клиентов для отображения деталей.")

elif not clients_list and st.session_state.client_page_number > 0:
    st.info("Нет клиентов на этой странице. Попробуйте вернуться на предыдущую.")
    if st.button("⬅️ Вернуться на предыдущую страницу"):
        st.session_state.client_page_number -= 1
        st.experimental_rerun()
elif not clients_list:
     st.info("Пока нет зарегистрированных клиентов.")

if st.button("Обновить список клиентов"):
    st.experimental_rerun()