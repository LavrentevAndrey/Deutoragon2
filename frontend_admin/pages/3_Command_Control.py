import streamlit as st
import pandas as pd
from utils import api_client
import json # Для парсинга JSON payload

st.set_page_config(page_title="Command Control", layout="wide")

st.title("Управление Командами")
st.markdown("Отправка команд клиентам и просмотр их статусов.")

# --- Секция создания новой команды ---
with st.expander("Создать новую команду", expanded=False):
    with st.form("new_command_form"):
        st.subheader("Параметры команды")
        
        clients_list_for_command = api_client.get_clients(limit=1000) # Получаем всех клиентов
        if not clients_list_for_command:
            st.warning("Нет доступных клиентов для отправки команды. Сначала зарегистрируйте клиента.")
            cmd_client_id = None
        else:
            client_options_cmd = {client['client_name']: client['id'] for client in clients_list_for_command}
            selected_client_name_cmd = st.selectbox(
                "Выберите клиента:",
                options=list(client_options_cmd.keys()),
                key="cmd_client_select"
            )
            cmd_client_id = client_options_cmd[selected_client_name_cmd] if selected_client_name_cmd else None

        cmd_type = st.text_input("Тип команды (например, 'run_script', 'block_ip')", key="cmd_type")
        cmd_payload_str = st.text_area(
            "Полезная нагрузка (JSON формат, например, {\"script_path\": \"/tmp/cleanup.sh\"} или {\"ip\": \"1.2.3.4\"})",
            height=100,
            key="cmd_payload"
        )
        cmd_deadline_str = st.text_input(
            "Крайний срок отправки (опционально, формат YYYY-MM-DDTHH:MM:SSZ, например, 2025-12-31T23:59:59Z)",
            key="cmd_deadline"
        )

        submitted_cmd = st.form_submit_button("Отправить команду")
        if submitted_cmd:
            if not cmd_client_id or not cmd_type:
                st.error("Клиент и тип команды обязательны для заполнения.")
            else:
                payload_dict = None
                if cmd_payload_str:
                    try:
                        payload_dict = json.loads(cmd_payload_str)
                    except json.JSONDecodeError:
                        st.error("Ошибка в формате JSON для полезной нагрузки. Оставьте пустым, если не требуется.")
                        # Не выходим, позволяем отправить без payload, если формат неверный, но поле было заполнено
                        # Либо можно сделать строже: if ...: st.stop() / return
                
                deadline = cmd_deadline_str if cmd_deadline_str else None

                with st.spinner("Отправка команды..."):
                    command_data = api_client.create_command(
                        client_id=str(cmd_client_id),
                        command_type=cmd_type,
                        payload=payload_dict,
                        dispatch_deadline=deadline
                    )
                
                if command_data:
                    st.success(f"Команда ID '{command_data.get('id')}' успешно создана для клиента '{selected_client_name_cmd}'.")
                    st.json(command_data)
                    st.experimental_rerun()
                else:
                    st.error("Не удалось создать команду. Проверьте правильность введенных данных и логи сервера.")

st.markdown("---")
# --- Секция отображения списка команд ---
st.subheader("Список отправленных команд")

# Фильтры для команд
st.sidebar.header("Фильтры команд")
clients_list_for_cmd_filter = api_client.get_clients(limit=1000)
cmd_filter_client_options = {client['client_name']: client['id'] for client in clients_list_for_cmd_filter}
cmd_filter_client_options["Все клиенты"] = None

selected_cmd_filter_client_name = st.sidebar.selectbox(
    "Клиент (фильтр команд):",
    options=list(cmd_filter_client_options.keys()),
    index=0,
    key="cmd_filter_client"
)
filter_cmd_client_id = cmd_filter_client_options[selected_cmd_filter_client_name]

command_statuses = [
    "", "pending_dispatch", "dispatched", "acknowledged",
    "in_progress", "completed", "failed", "timeout"
]
filter_cmd_status = st.sidebar.selectbox(
    "Статус команды:",
    options=command_statuses,
    index=0,
    key="cmd_filter_status"
)

# Пагинация
limit_cmd_per_page = st.sidebar.slider("Команд на странице:", 10, 100, 15, key="commands_limit")
if 'command_page_number' not in st.session_state:
    st.session_state.command_page_number = 0

skip_cmd = st.session_state.command_page_number * limit_cmd_per_page

with st.spinner("Загрузка команд..."):
    commands_list = api_client.get_all_commands(
        skip=skip_cmd,
        limit=limit_cmd_per_page,
        client_id=str(filter_cmd_client_id) if filter_cmd_client_id else None,
        status=filter_cmd_status if filter_cmd_status else None
    )

if commands_list:
    commands_df = pd.DataFrame(commands_list)
    # Форматирование дат
    for date_col in ['created_at', 'updated_at', 'dispatch_deadline']:
        if date_col in commands_df.columns:
            commands_df[date_col] = pd.to_datetime(commands_df[date_col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            commands_df[date_col] = commands_df[date_col].fillna("N/A") # Заполняем NaT (если были ошибки конвертации или None)

    columns_cmd_ordered = ['id', 'client_id', 'command_type', 'status', 'created_at', 'updated_at', 'dispatch_deadline', 'execution_result', 'payload']
    display_cmd_columns = [col for col in columns_cmd_ordered if col in commands_df.columns]
    
    st.dataframe(commands_df[display_cmd_columns], use_container_width=True)

    col1_cmd, col2_cmd = st.columns(2)
    with col1_cmd:
        if st.session_state.command_page_number > 0:
            if st.button("⬅️ Предыдущая страница", key="prev_commands"):
                st.session_state.command_page_number -= 1
                st.experimental_rerun()
    with col2_cmd:
        if len(commands_list) == limit_cmd_per_page:
            if st.button("Следующая страница ➡️", key="next_commands"):
                st.session_state.command_page_number += 1
                st.experimental_rerun()
        elif not commands_list and st.session_state.command_page_number > 0:
             st.info("Больше нет команд. Возможно, стоит вернуться.")


    # --- Детали команды (опционально) ---
    st.markdown("---")
    st.subheader("Просмотр деталей команды")
    if commands_list:
        # Используем ID команды для выбора, так как он уникален
        command_ids_options = {cmd['id']: cmd['id'] for cmd in commands_list}
        selected_command_id_for_details = st.selectbox(
            "Выберите ID команды для просмотра деталей:",
            options=list(command_ids_options.keys()),
            format_func=lambda x: f"ID: ...{x[-12:]} (Тип: {next((c['command_type'] for c in commands_list if c['id'] == x), 'N/A')})", # Показываем часть ID и тип
            key="command_details_select"
        )
        if selected_command_id_for_details:
            if st.button(f"Показать детали для команды ...{selected_command_id_for_details[-12:]}", key="show_cmd_details_btn"):
                with st.spinner(f"Загрузка деталей для команды {selected_command_id_for_details}..."):
                    details = api_client.get_command_details(selected_command_id_for_details)
                if details:
                    st.json(details)
                else:
                    st.error("Не удалось загрузить детали команды.")
    else:
        st.info("Нет команд для отображения деталей.")


elif not commands_list and st.session_state.command_page_number > 0:
    st.info("Нет команд на этой странице. Попробуйте вернуться или изменить фильтры.")
    if st.button("⬅️ Вернуться на предыдущую (команды)"):
        st.session_state.command_page_number -= 1
        st.experimental_rerun()
else:
    st.info("Команд по указанным фильтрам не найдено.")


if st.sidebar.button("Применить фильтры и обновить список команд"):
    st.session_state.command_page_number = 0 # Сбрасываем на первую страницу
    st.experimental_rerun()