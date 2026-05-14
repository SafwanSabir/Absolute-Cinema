# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./db/cinema.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
