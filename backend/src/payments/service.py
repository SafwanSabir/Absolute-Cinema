# pyrefly: ignore [missing-import]
import stripe
from backend.src.config import settings

stripe.api_key = settings.STRIPE_API_KEY

CORNER_SEAT_PRICE = 15.0
REGULAR_SEAT_PRICE = 10.0

def create_stripe_checkout(reservation):
    price = CORNER_SEAT_PRICE if reservation.seat.is_corner else REGULAR_SEAT_PRICE
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(price * 100),
                'product_data': {
                    'name': f"{reservation.movie.name} - Seat {reservation.seat.row}{reservation.seat.number}",
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=base + '/?session_id={CHECKOUT_SESSION_ID}&res_id=' + str(reservation.id) + '&status=success',
        cancel_url=base + '/?res_id=' + str(reservation.id) + '&status=cancel',
    )
    return session.url
