from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.src.movies.schemas import MovieResponse
from backend.src.auth.schemas import UserResponse

class SeatBase(BaseModel):
    row: str
    number: int
    is_corner: bool

class SeatResponse(SeatBase):
    id: int

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    movie_id: int
    seat_id: int

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    status: str
    created_at: datetime
    seat: SeatResponse
    movie: MovieResponse

    class Config:
        from_attributes = True
