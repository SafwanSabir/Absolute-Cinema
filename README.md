# Absolute Cinema

## Overview
Absolute Cinema is a comprehensive, full-stack movie seat reservation system. It features robust user authentication, an administrative dashboard for movie management, a sophisticated seat booking interface, and secure payment processing. The application is built using Streamlit for the frontend interface and Python with SQLAlchemy for the backend services.

## Architecture and Directory Structure
The project is modularized into distinct directories for maintainability and clear separation of concerns:

* `frontend/`: Contains the presentation layer and user interface code.
  * `app.py`: The main entry point for the Streamlit application, handling routing, navigation, and session state.
  * `ui_pages.py`: Contains the rendering logic for individual views (Home, Login, Register, Checkout, Admin Dashboard, My Bookings).
* `backend/`: Contains the core business logic, database models, and authentication services.
  * `database.py`: SQLAlchemy models (User, Movie, Seat, Reservation) and database connection configuration.
  * `services.py`: Core application services including user authentication, booking validation logic, email notifications, and Stripe API integration.
  * `auth.py`: Cryptographic utilities for password hashing and secure token generation.
  * `init_db.py`: Initialization script to populate the database with default data, including the initial admin user, seating layout, and sample movies.
* `db/`: Stores the SQLite database file (`cinema.db`).
* `assets/`: Contains static media files such as the application logo (`AC-logo-c.jpg`) and favicon (`tab-transparent.png`).

## Core Features
* **User Authentication:** Secure login, registration, and email-based password recovery functionality.
* **Session Management:** Persistent user sessions, ensuring continuity even during third-party payment redirection or page refreshes.
* **Booking System:** Interactive cinema seating layout with real-time availability checks and pricing tiers (e.g., corner seats vs. regular seats).
* **Reservation Timer:** A strict 5-minute countdown timer that temporarily locks selected seats during the checkout process to prevent double-booking.
* **Payment Integration:** Secure checkout process powered by the Stripe API.
* **Admin Dashboard:** Dedicated, role-based interface for administrators to dynamically add, schedule, and remove movies from the catalog.
* **Booking History:** User-specific dashboard to track upcoming reservations and review past bookings.

## Technology Stack
* **Frontend:** Streamlit
* **Backend:** Python 3
* **Database:** SQLite with SQLAlchemy ORM
* **Payments:** Stripe API
* **Environment Management:** python-dotenv

## Setup and Installation

1. Ensure Python 3.11+ is installed on your system.
2. Navigate to the project root directory and activate your virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Install the required dependencies (if not already installed). Ensure you have `streamlit`, `sqlalchemy`, `stripe`, `passlib`, and `python-dotenv`.
4. Initialize the database. This will create the necessary tables and populate the initial dataset:
   ```bash
   python -m backend.init_db
   ```
5. Start the FastAPI backend server on port 8000:
   ```bash
   uvicorn backend.src.main:app --reload
   ```
6. In a separate terminal, start the Streamlit application:
   ```bash
   streamlit run frontend/app.py
   ```

## Configuration
The application requires specific environment variables to function correctly, particularly for payments and emails. Ensure a `.env` file exists in the root directory with the following keys:

* `STRIPE_API_KEY`: Your secret Stripe API key for processing payments.
* `SMTP_SERVER`: The SMTP server address for password reset emails (e.g., smtp.gmail.com).
* `SMTP_PORT`: The SMTP server port (usually 587).
* `SENDER_EMAIL`: The email address used to send automated notifications.
* `SENDER_PASSWORD`: The application-specific password for the sender email account.
