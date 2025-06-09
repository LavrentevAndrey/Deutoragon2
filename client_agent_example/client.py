import requests
import time
import random
import os
import json
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from dotenv import load_dotenv
import schedule # Для периодических задач

# Загрузка переменных окружения (API_KEY, BACKEND_URL)
load_dotenv()

BACKEND_URL = os.getenv("CLIENT_AGENT_BACKEND_URL", "http://localhost:8000") # URL бэкенда
API_KEY = os.getenv("CLIENT_AGENT_API_KEY") # API ключ этого клиента
API_V1_STR = "/api/v1"

CLIENT_HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("CLIENT_HEARTBEAT_INTERVAL_SECONDS", 60)) # Каждые 60 секунд
EVENT_SEND_INTERVAL_SECONDS = int(os.getenv("EVENT_SEND_INTERVAL_SECONDS", 120)) # Каждые 120 секунд
COMMAND_FETCH_INTERVAL_SECONDS = int(os.getenv("COMMAND_FETCH_INTERVAL_SECONDS", 30)) # Каждые 30 секунд

if not API_KEY:
    print("Ошибка: CLIENT_AGENT_API_KEY не установлен в .env или переменных окружения.")
    exit(1)

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# --- Функции взаимодействия с API ---

def send_heartbeat():
    try:
        response = requests.post(f"{BACKEND_URL}{API_V1_STR}/clients/heartbeat", headers=HEADERS)
        response.raise_for_status()
        print(f"[{datetime.now(timezone.utc)}] Heartbeat successful. Server response: {response.json()['status']}")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now(timezone.utc)}] Error sending heartbeat: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")

def send_security_events(events: list):
    if not events:
        return
    try:
        response = requests.post(f"{BACKEND_URL}{API_V1_STR}/events", headers=HEADERS, json=events)
        response.raise_for_status()
        print(f"[{datetime.now(timezone.utc)}] Successfully sent {len(events)} events. Server response: {response.status_code}")
        # print(f"Response data: {response.json()}") # Для отладки можно раскомментировать
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now(timezone.utc)}] Error sending events: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")

def generate_random_event():
    event_types = ["login_failure", "file_access_denied", "sql_injection_attempt", "ssh_login", "firewall_block"]
    severities = ["low", "medium", "high", "critical"]
    source_ips = ["192.168.1.101", "10.0.0.5", "203.0.113.45", None] # None для внутренних событий
    db_names = ["main_db", "user_profiles", "audit_log_db", None]

    event = {
        "event_type": random.choice(event_types),
        "severity": random.choice(severities),
        "source_ip": random.choice(source_ips),
        "db_name_target": random.choice(db_names),
        "details": {"info": f"Random event generated at {datetime.now(timezone.utc)}", "code": random.randint(100,999)},
        "timestamp": datetime.now(timezone.utc).isoformat() # Модель ожидает строку в ISO формате или datetime
    }
    # Убираем None значения, если они были выбраны случайно (кроме details)
    event = {k: v for k, v in event.items() if v is not None or k == "details"}
    return event

def fetch_and_process_commands():
    print(f"[{datetime.now(timezone.utc)}] Fetching commands...")
    try:
        response = requests.get(f"{BACKEND_URL}{API_V1_STR}/commands?limit=5", headers=HEADERS) # Запрашиваем до 5 команд
        response.raise_for_status()
        commands_to_process = response.json()

        if not commands_to_process:
            print(f"[{datetime.now(timezone.utc)}] No new commands.")
            return

        print(f"[{datetime.now(timezone.utc)}] Received {len(commands_to_process)} commands.")
        for command in commands_to_process:
            process_single_command(command)
            time.sleep(0.5) # Небольшая задержка между обработкой команд

    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now(timezone.utc)}] Error fetching commands: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")


def process_single_command(command: dict):
    command_id = command.get("id")
    command_type = command.get("command_type")
    payload = command.get("payload", {})
    print(f"[{datetime.now(timezone.utc)}] Processing command ID: {command_id}, Type: {command_type}")
    
    status_update = {"status": "acknowledged"} # Сначала подтверждаем получение
    update_command_status(command_id, status_update)
    time.sleep(0.1) # Даем время на обновление статуса

    status_update["status"] = "in_progress"
    update_command_status(command_id, status_update)
    time.sleep(random.uniform(0.5, 2)) # Имитация выполнения

    # Имитация выполнения команды
    if command_type == "log_message":
        message = payload.get("message", "No message in payload.")
        print(f"    COMMAND EXECUTE [log_message]: {message}")
        status_update["status"] = "completed"
        status_update["execution_result"] = f"Message logged: '{message[:50]}...'"
    elif command_type == "block_ip":
        ip_to_block = payload.get("ip", "No IP specified.")
        print(f"    COMMAND EXECUTE [block_ip]: Attempting to block IP {ip_to_block}")
        # Здесь могла бы быть реальная логика блокировки
        if random.choice([True, False]): # Имитация успеха/неудачи
            status_update["status"] = "completed"
            status_update["execution_result"] = f"IP {ip_to_block} successfully processed for blocking."
        else:
            status_update["status"] = "failed"
            status_update["execution_result"] = f"Failed to process IP {ip_to_block} for blocking."
    else:
        print(f"    COMMAND EXECUTE [unknown_type: {command_type}]: No specific action defined. Marking as completed.")
        status_update["status"] = "completed"
        status_update["execution_result"] = "Unknown command type processed with generic completion."

    update_command_status(command_id, status_update)
    print(f"[{datetime.now(timezone.utc)}] Finished processing command ID: {command_id}, Final Status: {status_update['status']}")


def update_command_status(command_id: str, update_data: dict):
    """
    Обновляет статус команды на сервере.
    update_data: {"status": "new_status", "execution_result": "optional_result"}
    """
    try:
        response = requests.patch(f"{BACKEND_URL}{API_V1_STR}/commands/{command_id}", headers=HEADERS, json=update_data)
        response.raise_for_status()
        # print(f"[{datetime.now(timezone.utc)}] Status for command {command_id} updated to {update_data['status']}. Result: {response.json().get('execution_result', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now(timezone.utc)}] Error updating status for command {command_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")


def scheduled_event_generation():
    num_events = random.randint(1, 3) # Генерируем от 1 до 3 событий за раз
    events = [generate_random_event() for _ in range(num_events)]
    print(f"[{datetime.now(timezone.utc)}] Generated {len(events)} random events to send.")
    send_security_events(events)

# --- Основной цикл или планировщик ---
if __name__ == "__main__":
    print("Starting Client Agent...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Heartbeat Interval: {CLIENT_HEARTBEAT_INTERVAL_SECONDS}s")
    print(f"Event Send Interval: {EVENT_SEND_INTERVAL_SECONDS}s")
    print(f"Command Fetch Interval: {COMMAND_FETCH_INTERVAL_SECONDS}s")

    # Первоначальный heartbeat при запуске
    send_heartbeat()
    # Первоначальный запрос команд
    fetch_and_process_commands()

    # Настройка расписания
    schedule.every(CLIENT_HEARTBEAT_INTERVAL_SECONDS).seconds.do(send_heartbeat)
    schedule.every(EVENT_SEND_INTERVAL_SECONDS).seconds.do(scheduled_event_generation)
    schedule.every(COMMAND_FETCH_INTERVAL_SECONDS).seconds.do(fetch_and_process_commands)

    print(f"[{datetime.now(timezone.utc)}] Client agent running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1) # Проверяем задачи каждую секунду
    except KeyboardInterrupt:
        print(f"\n[{datetime.now(timezone.utc)}] Client agent stopping...")
    finally:
        print(f"[{datetime.now(timezone.utc)}] Client agent stopped.")