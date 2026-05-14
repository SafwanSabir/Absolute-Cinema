# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from backend.src.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(DateTime)
    duration_minutes = Column(Integer)

    reservations = relationship("Reservation", back_populates="movie")
