# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.src.database import Base

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
