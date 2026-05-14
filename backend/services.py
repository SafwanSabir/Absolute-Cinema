# pyrefly: ignore [missing-import]
import stripe
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from backend.database import User, Movie, Seat, Reservation
from backend.auth import get_password_hash, verify_password, create_reset_token

import os
try:
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "absolutecinema360@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

# Configuration
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
CORNER_SEAT_PRICE = 15.0
REGULAR_SEAT_PRICE = 10.0
RESERVATION_TIMEOUT_MINUTES = 5

def confirm_payment(db, res_id):
    """Confirms a reservation payment."""
    res = db.query(Reservation).filter(Reservation.id == int(res_id)).first()
    if res and res.status == "pending":
        res.status = "confirmed"
        db.commit()
        return True
    return False

def authenticate_user(db, username, password):
    """Verifies credentials and returns user ID if valid."""
    u = db.query(User).filter(User.username == username).first()
    if u and verify_password(password, u.password_hash):
        return u.id
    return None

def register_new_user(db, username, email, password):
    """Registers a new user, returns False if username or email exists."""
    if db.query(User).filter(User.username == username).first() or db.query(User).filter(User.email == email).first():
        return False
    new_user = User(username=username, email=email, password_hash=get_password_hash(password))
    db.add(new_user)
    db.commit()
    return True

def send_reset_email(email):
    """Generates a reset token and sends a reset email to the user."""
    token = create_reset_token(email)
    reset_url = f"http://localhost:8501/?token={token}"
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = "Absolute Cinema - Password Reset"
    
    body = f"Hello,\n\nClick the link below to reset your password:\n{reset_url}\n\nThis link will expire in 15 minutes."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def reset_user_password(db, email, new_password):
    """Updates the user's password."""
    u = db.query(User).filter(User.email == email).first()
    if u:
        u.password_hash = get_password_hash(new_password)
        db.commit()
        return True
    return False

def get_upcoming_movies(db):
    """Returns all movies that haven't started yet."""
    now = datetime.utcnow()
    return db.query(Movie).filter(Movie.start_time > now).all()

def get_movie_details(db, movie_id):
    """Fetches a specific movie by ID."""
    return db.query(Movie).filter(Movie.id == movie_id).first()

def get_all_seats(db):
    """Returns all seats in the cinema."""
    return db.query(Seat).all()

def is_seat_available(db, movie_id, seat_id):
    """Checks if a seat is currently available for booking."""
    now = datetime.utcnow()
    timeout_threshold = now - timedelta(minutes=RESERVATION_TIMEOUT_MINUTES)
    active = db.query(Reservation).filter(
        Reservation.movie_id == movie_id,
        Reservation.seat_id == seat_id,
        Reservation.status.in_(["confirmed", "pending"])
    ).order_by(Reservation.created_at.desc()).first()
    
    if active:
        if active.status == "confirmed":
            return False
        if active.status == "pending" and active.created_at > timeout_threshold:
            return False
    return True

def book_seat_pending(db, user_id, movie_id, seat_id):
    """Creates a temporary pending reservation for 5 minutes."""
    res = Reservation(user_id=user_id, movie_id=movie_id, seat_id=seat_id, status="pending", created_at=datetime.utcnow())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res

def get_reservation(db, res_id, user_id):
    """Fetches a specific user's reservation."""
    return db.query(Reservation).filter(Reservation.id == res_id, Reservation.user_id == user_id).first()

def create_stripe_checkout(reservation):
    """Generates a Stripe Checkout session URL."""
    price = CORNER_SEAT_PRICE if reservation.seat.is_corner else REGULAR_SEAT_PRICE
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(price * 100),
                'product_data': {
                    'name': f"{reservation.movie.name} - Seat {reservation.seat.row}{reservation.seat.number}",
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8501/?session_id={CHECKOUT_SESSION_ID}&res_id=' + str(reservation.id) + '&status=success',
        cancel_url='http://localhost:8501/?res_id=' + str(reservation.id) + '&status=cancel',
    )
    return session.url

def add_movie(db, name, start_date, start_time, duration):
    """Adds a new movie to the schedule."""
    dt = datetime.combine(start_date, start_time)
    new_m = Movie(name=name, start_time=dt, duration_minutes=duration)
    db.add(new_m)
    db.commit()

def delete_movie(db, movie_id):
    """Deletes a movie from the schedule."""
    m = db.query(Movie).filter(Movie.id == movie_id).first()
    if m:
        db.delete(m)
        db.commit()

def get_all_movies(db):
    """Returns all movies for admin view."""
    return db.query(Movie).all()
