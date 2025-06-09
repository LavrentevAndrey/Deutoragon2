import requests
import streamlit as st
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv() # Загружаем переменные из .env файла в корне проекта

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000") # Значение по умолчанию для локального запуска
API_V1_STR = "/api/v1" # Можно также взять из настроек, если они доступны фронтенду

BASE_ADMIN_URL = f"{BACKEND_URL}{API_V1_STR}/admin"
BASE_CLIENT_URL = f"{BACKEND_URL}{API_V1_STR}/clients" # Для heartbeat, если понадобится от имени админа (нет)
BASE_COMMANDS_URL = f"{BACKEND_URL}{API_V1_STR}/commands" # Для получения команд клиентом (не для админа)


# --- Client Management ---
def register_client(client_name: str, ip_address: Optional[str] = None, os_info: Optional[str] = None) -> Optional[Dict[str, Any]]:
    payload = {"client_name": client_name, "ip_address": ip_address, "os_info": os_info}
    # Удаляем None значения, чтобы не отправлять их, если они не заданы
    payload = {k: v for k, v in payload.items() if v is not None}
    try:
        response = requests.post(f"{BASE_ADMIN_URL}/clients", json=payload)
        response.raise_for_status() # Вызовет исключение для HTTP ошибок 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error registering client: {e}")
        if response is not None and response.content:
            try:
                st.error(f"Server response: {response.json()}")
            except ValueError:
                st.error(f"Server response (not JSON): {response.text}")
        return None

def get_clients(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    params = {"skip": skip, "limit": limit}
    try:
        response = requests.get(f"{BASE_ADMIN_URL}/clients", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching clients: {e}")
        return []

def get_client_details(client_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{BASE_ADMIN_URL}/clients/{client_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching client details for {client_id}: {e}")
        return None

# --- Event Management ---
def get_events(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[str] = None, # ISO format string
    end_date: Optional[str] = None,   # ISO format string
) -> List[Dict[str, Any]]:
    params = {
        "skip": skip,
        "limit": limit,
        "client_id": client_id,
        "event_type": event_type,
        "severity": severity,
        "start_date": start_date,
        "end_date": end_date,
    }
    # Удаляем None значения из параметров
    params = {k: v for k, v in params.items() if v is not None and v != ""}
    try:
        response = requests.get(f"{BASE_ADMIN_URL}/events", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching events: {e}")
        return []

# --- Command Management ---
def create_command(
    client_id: str,
    command_type: str,
    payload: Optional[Dict[str, Any]] = None,
    dispatch_deadline: Optional[str] = None # ISO format string
) -> Optional[Dict[str, Any]]:
    command_data = {
        "client_id": client_id,
        "command_type": command_type,
        "payload": payload if payload else {},
        "dispatch_deadline": dispatch_deadline
    }
    command_data = {k:v for k,v in command_data.items() if v is not None}

    try:
        response = requests.post(f"{BASE_ADMIN_URL}/commands", json=command_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating command: {e}")
        if response is not None and response.content:
            try:
                st.error(f"Server response: {response.json()}")
            except ValueError:
                st.error(f"Server response (not JSON): {response.text}")
        return None

def get_all_commands(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = {
        "skip": skip,
        "limit": limit,
        "client_id": client_id,
        "status": status,
    }
    params = {k: v for k, v in params.items() if v is not None and v != ""}
    try:
        response = requests.get(f"{BASE_ADMIN_URL}/commands", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching commands: {e}")
        return []

def get_command_details(command_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(f"{BASE_ADMIN_URL}/commands/{command_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching command details for {command_id}: {e}")
        return None