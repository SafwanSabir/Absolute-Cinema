from fastapi import FastAPI
from backend.src.database import engine, Base
import backend.src.auth.models
import backend.src.movies.models
import backend.src.reservations.models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Absolute Cinema API")

from backend.src.auth.router import router as auth_router
from backend.src.movies.router import router as movies_router
from backend.src.reservations.router import router as reservations_router
from backend.src.payments.router import router as payments_router

app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(reservations_router)
app.include_router(payments_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
