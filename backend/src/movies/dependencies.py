from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from backend.src.database import get_db
from backend.src.movies.models import Movie
from backend.src.movies.service import get_movie_details

def valid_movie_id(movie_id: int, db: Session = Depends(get_db)):
    movie = get_movie_details(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie
