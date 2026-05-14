from datetime import datetime, timedelta
from backend.src.reservations.models import Seat, Reservation

RESERVATION_TIMEOUT_MINUTES = 5

def get_all_seats(db):
    return db.query(Seat).all()

def is_seat_available(db, movie_id, seat_id):
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
    res = Reservation(user_id=user_id, movie_id=movie_id, seat_id=seat_id, status="pending", created_at=datetime.utcnow())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res

def get_reservation(db, res_id, user_id):
    return db.query(Reservation).filter(Reservation.id == res_id, Reservation.user_id == user_id).first()

def confirm_payment(db, res_id):
    res = db.query(Reservation).filter(Reservation.id == int(res_id)).first()
    if res and res.status == "pending":
        res.status = "confirmed"
        db.commit()
        return True
    return False
