from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
import stripe
from backend.src.config import settings
from backend.src.database import get_db
from backend.src.payments import service
from backend.src.reservations.dependencies import valid_reservation
from backend.src.reservations.models import Reservation
from backend.src.reservations.service import confirm_payment

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/checkout/{res_id}")
def create_checkout_session(res: Reservation = Depends(valid_reservation)):
    if res.status != "pending":
        raise HTTPException(status_code=400, detail="Reservation is not pending")
    if not settings.STRIPE_API_KEY.strip():
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Set STRIPE_API_KEY in the API environment or .env file.",
        )
    try:
        url = service.create_stripe_checkout(res)
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=502,
            detail=e.user_message or str(e) or "Stripe request failed",
        ) from e
    return {"url": url}

@router.post("/confirm/{res_id}")
def confirm_checkout(res_id: int, db: Session = Depends(get_db)):
    # Note: In a real app, this should be verified via a Stripe Webhook!
    # Here we are just allowing it to be confirmed by the frontend for simplicity.
    success = confirm_payment(db, res_id)
    if not success:
        raise HTTPException(status_code=400, detail="Payment could not be confirmed")
    return {"message": "Payment confirmed"}
