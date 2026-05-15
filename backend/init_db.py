from backend.src.database import SessionLocal, engine, Base
from backend.src.auth.models import User
from backend.src.reservations.models import Seat
from backend.src.movies.models import Movie
from backend.src.auth.service import get_password_hash

def init():
    # Make sure tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if admin exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(username="admin", email="admin@absolutecinema.com", password_hash=get_password_hash("admin"), is_admin=True)
        db.add(admin)
        print("Created admin user (admin / admin)")
    
    # Create seats if none exist
    if db.query(Seat).count() == 0:
        rows = ['A', 'B', 'C', 'D']
        numbers = [1, 2, 3, 4, 5, 6]
        for row in rows:
            for num in numbers:
                # Let's say seats 1 and 6 are corners
                is_corner = (num == 1 or num == 6)
                seat = Seat(row=row, number=num, is_corner=is_corner)
                db.add(seat)
        print("Created sample seats (A1 to D6)")
    
    # Create sample movies if none exist
    import random
    from datetime import datetime, timedelta

    if db.query(Movie).count() == 0:
        movie_titles = [
            "Harry Potter and the Sorcerer's Stone", "Harry Potter and the Chamber of Secrets", 
            "Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire",
            "John Wick", "John Wick: Chapter 2", "John Wick: Chapter 3 – Parabellum", "John Wick: Chapter 4",
            "The Lord of the Rings: The Fellowship of the Ring", "The Lord of the Rings: The Two Towers", "The Lord of the Rings: The Return of the King",
            "The Avengers", "Avengers: Age of Ultron", "Avengers: Infinity War", "Avengers: Endgame",
            "Jumanji", "Jumanji: Welcome to the Jungle", "Jumanji: The Next Level"
        ]
        
        base_date = datetime(2026, 5, 15, 18, 0, 0) # May 15, 2026, 6 PM
        
        for title in movie_titles:
            # Randomize date between May 15, 2026 and June 15, 2026
            random_days_offset = random.randint(0, 30)
            random_hours_offset = random.randint(-4, 4) # +/- 4 hours from 6 PM
            start_time = base_date + timedelta(days=random_days_offset, hours=random_hours_offset)
            
            # Randomize duration between 90 and 180 mins
            duration = random.randint(90, 180)
            
            movie = Movie(name=title, start_time=start_time, duration_minutes=duration)
            db.add(movie)
            
        print("Created sample movies (Harry Potter, John Wick, LOTR, Avengers, Jumanji)")

    db.commit()
    db.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init()
