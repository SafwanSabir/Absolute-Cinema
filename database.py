from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# SQLite database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./cinema.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    reservations = relationship("Reservation", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(DateTime)
    duration_minutes = Column(Integer)

    reservations = relationship("Reservation", back_populates="movie")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    row = Column(String) # e.g., 'A', 'B'
    number = Column(Integer) # e.g., 1, 2
    is_corner = Column(Boolean, default=False)
    
    reservations = relationship("Reservation", back_populates="seat")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    
    status = Column(String, default="pending") # "pending" or "confirmed"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reservations")
    movie = relationship("Movie", back_populates="reservations")
    seat = relationship("Seat", back_populates="reservations")

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
