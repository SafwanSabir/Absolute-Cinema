from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List
from backend.src.database import get_db
from backend.src.reservations import schemas, service, dependencies
from backend.src.auth.dependencies import get_current_user
from backend.src.auth.models import User
from backend.src.movies.dependencies import valid_movie_id
from backend.src.movies.models import Movie
from backend.src.movies.service import get_movie_details
from backend.src.reservations.models import Reservation, Seat

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.get("/seats", response_model=List[schemas.SeatResponse])
def get_seats(db: Session = Depends(get_db)):
    return service.get_all_seats(db)

@router.get("/movies/{movie_id}/seats/{seat_id}/availability")
def check_seat_availability(movie: Movie = Depends(valid_movie_id), seat: Seat = Depends(dependencies.valid_seat_id), db: Session = Depends(get_db)):
    available = service.is_seat_available(db, movie.id, seat.id)
    return {"available": available}

@router.post("/", response_model=schemas.ReservationResponse, status_code=201)
def book_seat(
    req: schemas.ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    movie = get_movie_details(db, req.movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    seat = db.query(Seat).filter(Seat.id == req.seat_id).first()
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    if not service.is_seat_available(db, movie.id, seat.id):
        raise HTTPException(status_code=400, detail="Seat is no longer available")

    res = service.book_seat_pending(db, current_user.id, movie.id, seat.id)
    return res

@router.get("/my", response_model=List[schemas.ReservationResponse])
def get_my_reservations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.user_id == current_user.id).order_by(Reservation.created_at.desc()).all()

@router.get("/{res_id}", response_model=schemas.ReservationResponse)
def get_reservation(res: Reservation = Depends(dependencies.valid_reservation)):
    return res
