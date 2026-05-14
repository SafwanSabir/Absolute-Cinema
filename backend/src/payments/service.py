# pyrefly: ignore [missing-import]
import stripe
import os

stripe.api_key = os.getenv("STRIPE_API_KEY", "")

CORNER_SEAT_PRICE = 15.0
REGULAR_SEAT_PRICE = 10.0

def create_stripe_checkout(reservation):
    price = CORNER_SEAT_PRICE if reservation.seat.is_corner else REGULAR_SEAT_PRICE
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
        success_url='http://localhost:8501/?session_id={CHECKOUT_SESSION_ID}&res_id=' + str(reservation.id) + '&status=success',
        cancel_url='http://localhost:8501/?res_id=' + str(reservation.id) + '&status=cancel',
    )
    return session.url
