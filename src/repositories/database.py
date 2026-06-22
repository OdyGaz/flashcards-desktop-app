# src/repositories/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.config import DB_PATH
from src.domain.models import Base

# Δημιουργία του Engine για SQLite με υποστήριξη Foreign Keys
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Δημιουργία Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Δημιουργεί τους πίνακες στη βάση δεδομένων αν δεν υπάρχουν"""
    # Ενεργοποίηση Foreign Keys για την SQLite με χρήση της text()
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))
        connection.commit()
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Επιστρέφει ένα νέο session για αλληλεπίδραση με τη βάση"""
    return SessionLocal()
