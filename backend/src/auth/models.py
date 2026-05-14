# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from backend.src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    reservations = relationship("Reservation", back_populates="user")
