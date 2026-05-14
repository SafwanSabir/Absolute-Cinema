from datetime import datetime
from backend.src.movies.models import Movie

def get_upcoming_movies(db):
    now = datetime.utcnow()
    return db.query(Movie).filter(Movie.start_time > now).all()

def get_movie_details(db, movie_id):
    return db.query(Movie).filter(Movie.id == movie_id).first()

def add_movie(db, name, start_date, start_time, duration):
    dt = datetime.combine(start_date, start_time)
    new_m = Movie(name=name, start_time=dt, duration_minutes=duration)
    db.add(new_m)
    db.commit()

def delete_movie(db, movie_id):
    m = db.query(Movie).filter(Movie.id == movie_id).first()
    if m:
        db.delete(m)
        db.commit()

def get_all_movies(db):
    return db.query(Movie).all()
