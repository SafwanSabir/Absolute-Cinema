from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List
from backend.src.database import get_db
from backend.src.movies import schemas, service, dependencies
from backend.src.auth.dependencies import get_current_admin
from backend.src.movies.models import Movie

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("/upcoming", response_model=List[schemas.MovieResponse])
def get_upcoming(db: Session = Depends(get_db)):
    return service.get_upcoming_movies(db)

@router.get("/", response_model=List[schemas.MovieResponse])
def get_all(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return service.get_all_movies(db)

@router.get("/{movie_id}", response_model=schemas.MovieResponse)
def get_movie(movie: Movie = Depends(dependencies.valid_movie_id)):
    return movie

@router.post("/", status_code=201)
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service.add_movie(db, movie.name, movie.start_date, movie.start_time, movie.duration_minutes)
    return {"message": "Movie added successfully"}

@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie: Movie = Depends(dependencies.valid_movie_id), db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service.delete_movie(db, movie.id)
