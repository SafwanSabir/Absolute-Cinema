import os
import requests
# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime

# In Docker Compose, set API_BASE_URL=http://api:8000 (service name + internal port)
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")

def get_headers():
    headers = {}
    if "token" in st.session_state and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

def login(username, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    return response.json() if response.status_code == 200 else None

def register(username, email, password):
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    return response.status_code == 201

def get_current_user():
    if "token" not in st.session_state or not st.session_state.token:
        return None
    response = requests.get(f"{BASE_URL}/auth/me", headers=get_headers())
    return response.json() if response.status_code == 200 else None

def request_password_reset(email):
    response = requests.post(f"{BASE_URL}/auth/reset-password-request", json={"email": email})
    return response.status_code == 200

def reset_password(token, new_password):
    response = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })
    return response.status_code == 200

def get_upcoming_movies():
    response = requests.get(f"{BASE_URL}/movies/upcoming", headers=get_headers())
    return response.json() if response.status_code == 200 else []

def get_all_movies():
    response = requests.get(f"{BASE_URL}/movies/", headers=get_headers())
    return response.json() if response.status_code == 200 else []

def get_movie_details(movie_id):
    response = requests.get(f"{BASE_URL}/movies/{movie_id}", headers=get_headers())
    return response.json() if response.status_code == 200 else None

def add_movie(name, start_date, start_time, duration):
    # Combine start_date and start_time formatting required by Pydantic
    response = requests.post(f"{BASE_URL}/movies/", json={
        "name": name,
        "start_date": start_date.isoformat(),
        "start_time": start_time.isoformat(),
        "duration_minutes": duration
    }, headers=get_headers())
    return response.status_code == 201

def delete_movie(movie_id):
    response = requests.delete(f"{BASE_URL}/movies/{movie_id}", headers=get_headers())
    return response.status_code == 204

def get_all_seats():
    response = requests.get(f"{BASE_URL}/reservations/seats", headers=get_headers())
    return response.json() if response.status_code == 200 else []

def is_seat_available(movie_id, seat_id):
    response = requests.get(f"{BASE_URL}/reservations/movies/{movie_id}/seats/{seat_id}/availability", headers=get_headers())
    if response.status_code == 200:
        return response.json().get("available", False)
    return False

def book_seat_pending(movie_id, seat_id):
    response = requests.post(f"{BASE_URL}/reservations/", json={
        "movie_id": movie_id,
        "seat_id": seat_id
    }, headers=get_headers())
    return response.json() if response.status_code == 201 else None

def get_reservation(res_id):
    response = requests.get(f"{BASE_URL}/reservations/{res_id}", headers=get_headers())
    return response.json() if response.status_code == 200 else None

def get_my_reservations():
    response = requests.get(f"{BASE_URL}/reservations/my", headers=get_headers())
    return response.json() if response.status_code == 200 else []

def create_checkout_session(res_id):
    response = requests.post(f"{BASE_URL}/payments/checkout/{res_id}", headers=get_headers())
    if response.status_code == 200:
        return response.json().get("url"), None
    try:
        body = response.json()
        detail = body.get("detail", response.text)
        if isinstance(detail, list):
            detail = "; ".join(str(x) for x in detail)
    except Exception:
        detail = response.text[:500] if response.text else f"HTTP {response.status_code}"
    return None, detail

def confirm_payment(res_id):
    response = requests.post(f"{BASE_URL}/payments/confirm/{res_id}", headers=get_headers())
    return response.status_code == 200
