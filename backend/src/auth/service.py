# pyrefly: ignore [missing-import]
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.src.auth.models import User

# Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-evaluation-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "absolutecinema360@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "type": "reset", "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None

def authenticate_user(db, username, password):
    u = db.query(User).filter(User.username == username).first()
    if u and verify_password(password, u.password_hash):
        return u.id
    return None

def register_new_user(db, username, email, password):
    if db.query(User).filter(User.username == username).first() or db.query(User).filter(User.email == email).first():
        return False
    new_user = User(username=username, email=email, password_hash=get_password_hash(password))
    db.add(new_user)
    db.commit()
    return True

def reset_user_password(db, email, new_password):
    u = db.query(User).filter(User.email == email).first()
    if u:
        u.password_hash = get_password_hash(new_password)
        db.commit()
        return True
    return False

def send_reset_email(email):
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
