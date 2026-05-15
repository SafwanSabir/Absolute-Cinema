# Absolute Cinema

## Overview

Absolute Cinema is a full-stack movie seat reservation system: user authentication, an admin dashboard, seat booking with a countdown hold, and Stripe checkout. The UI is **Streamlit**; the API is **FastAPI** with **SQLAlchemy** and **SQLite**.

## Project layout

| Path | Purpose |
|------|---------|
| `frontend/` | Streamlit app (`app.py`, `ui_pages.py`, `api_client.py`) |
| `backend/src/` | FastAPI app (`main.py`), routers, models, services |
| `backend/init_db.py` | Create tables and seed admin, seats, sample movies |
| `db/` | Local SQLite file when using default `DATABASE_URL` (e.g. `db/cinema.db`) |
| `assets/` | Optional logo and favicon for the UI |
| `docker/` | `Dockerfile.api`, `Dockerfile.web` |
| `requirements.txt` | Full dependencies for local dev and the API image |
| `requirements-web.txt` | Slim dependencies for the web (Streamlit) image |
| `docker-compose.yml` | Run API + web together |

Legacy duplicate modules under `backend/` (old `database.py` / `services.py` / `auth.py`) have been removed; the active code lives in `backend/src/`.

## Requirements

- **Python 3.11+**
- **Docker Desktop** (optional, for containerized run)

## Local development

1. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

   **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`  
   **macOS / Linux:** `source venv/bin/activate`

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database (idempotent):

   ```bash
   python -m backend.init_db
   ```

4. Start the API from the **project root** (so `backend` is importable):

   ```bash
   python -m uvicorn backend.src.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. In another terminal, start Streamlit:

   ```bash
   python -m streamlit run frontend/app.py
   ```

6. Open **http://localhost:8501**. Default admin after `init_db`: username `admin`, password `admin`.

## Docker

From the project root:

```bash
docker compose up --build
```

- **API:** http://localhost:8000 (SQLite stored in the `cinema_data` volume at `/data/cinema.db` inside the API container)
- **Web:** http://localhost:8501

The compose file sets `API_BASE_URL=http://api:8000` for server-side calls from Streamlit, and `FRONTEND_BASE_URL=http://localhost:8501` for Stripe return URLs in the browser.

**Stripe in Docker:** add `STRIPE_API_KEY=sk_test_...` to `.env` next to `docker-compose.yml`. The **api** service loads that file via `env_file: .env` so the key reaches the container (it is not baked into the image). Restart with `docker compose up -d`.

### Live editing (no rebuild for frontend changes)

The compose file mounts your local `./frontend` into the **web** container at `/app/frontend`. Edit any file under `frontend/` on the host and Streamlit's auto-rerun picks it up — just refresh the browser tab. No `--build` needed.

You only need to rebuild the **web** image when `requirements-web.txt` changes:

```bash
docker compose up -d --build web
```

Backend changes still need an image rebuild (or local `--reload` uvicorn):

```bash
docker compose up -d --build api
```

## Configuration

Create a `.env` file in the project root (see `backend/src/config.py` for defaults). Common variables:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT signing (change in production) |
| `STRIPE_API_KEY` | Stripe secret key for checkout |
| `SMTP_SERVER`, `SMTP_PORT` | Outbound mail for password reset |
| `SENDER_EMAIL`, `SENDER_PASSWORD` | SMTP credentials |
| `DATABASE_URL` | Optional; default local SQLite is `sqlite:///./db/cinema.db` |
| `API_BASE_URL` | Used by Streamlit `api_client` (default `http://localhost:8000`) |
| `FRONTEND_BASE_URL` | Stripe success/cancel URLs (default `http://localhost:8501`) |

## Core features

- Authentication, registration, password reset (email)
- Seat map with corner vs regular pricing
- Reservation hold timer at checkout
- Stripe payment session
- Admin movie CRUD and user bookings view
