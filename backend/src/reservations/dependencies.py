from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from backend.src.database import get_db
from backend.src.reservations.models import Seat, Reservation
from backend.src.auth.dependencies import get_current_user
from backend.src.auth.models import User

def valid_seat_id(seat_id: int, db: Session = Depends(get_db)):
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    return seat

def valid_reservation(res_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = db.query(Reservation).filter(Reservation.id == res_id, Reservation.user_id == current_user.id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found or does not belong to you")
    return res
