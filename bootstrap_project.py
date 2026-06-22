# bootstrap_project.py
import os
from pathlib import Path

def create_structure():
    # Ορισμός των φακέλων που πρέπει να δημιουργηθούν
    directories = [
        "data/images",
        "src/domain",
        "src/repositories",
        "src/services",
        "src/ui/views",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[+] Δημιουργήθηκε ο φάκελος: {directory}")

    # Δημιουργία των __init__.py αρχείων για σωστά python imports
    init_files = [
        "src/__init__.py",
        "src/domain/__init__.py",
        "src/repositories/__init__.py",
        "src/services/__init__.py",
        "src/ui/__init__.py",
        "src/ui/views/__init__.py",
    ]

    for init_file in init_files:
        Path(init_file).touch()
        print(f"[+] Δημιουργήθηκε το αρχείο: {init_file}")


def write_file(path: str, content: str):
    file_path = Path(path)
    file_path.write_text(content, encoding="utf-8")
    print(f"[✔] Γράφτηκε το αρχείο: {path}")


# --- ΠΕΡΙΕΧΟΜΕΝΑ ΑΡΧΕΙΩΝ ---

pyproject_content = """[tool.poetry]
name = "flashcards-app"
version = "0.1.0"
description = "Τοπική εφαρμογή Flashcards με Python, PySide6 και SQLAlchemy 2.0"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
PySide6 = "^6.6.0"
SQLAlchemy = "^2.0.0"
Pillow = "^10.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

config_content = """# src/config.py
from pathlib import Path

# Βασικά μονοπάτια του συστήματος
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "database.db"

# Διασφάλιση ύπαρξης των φακέλων δεδομένων
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# Χρωματική Παλέτα Εφαρμογής (Hex Codes)
COLOR_DARK_BASE = "#26282B"   # Σκούρο Ανθρακί (Dark Mode)
COLOR_LIGHT_BASE = "#EAEAEA"  # Ανοιχτό Γκρι (Light Mode Base)
COLOR_ACCENT = "#FF555D"      # Ζωηρό Κοραλί (Accent Color)
"""

models_content = """# src/domain/models.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    \"\"\"Βασική κλάση για τα μοντέλα της SQLAlchemy 2.0\"\"\"
    pass

class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Σχέση ένα-προς-πολλά με τις κάρτες
    cards: Mapped[List["Card"]] = relationship(
        "Card", back_populates="deck", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Deck(id={self.id}, name='{self.name}')>"

class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)  # Μονοπάτι της εικόνας στον δίσκο
    word: Mapped[str] = mapped_column(String(255), nullable=False)        # Η σωστή λέξη-στόχος
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Αντίστροφη σχέση με το Deck
    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, word='{self.word}')>"
"""

database_content = """# src/repositories/database.py
from sqlalchemy import create_engine
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
    \"\"\"Δημιουργεί τους πίνακες στη βάση δεδομένων αν δεν υπάρχουν\"\"\"
    # Ενεργοποίηση Foreign Keys για την SQLite
    with engine.connect() as connection:
        connection.execute(type("PRAGMA", (), {})()) # Dummy execution for legacy fallback or direct pragma
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    \"\"\"Επιστρέφει ένα νέο session για αλληλεπίδραση με τη βάση\"\"\"
    return SessionLocal()
"""

repository_content = """# src/repositories/deck_repository.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.models import Deck, Card

class DeckRepository:
    \"\"\"Διαχειρίζεται όλες τις λειτουργίες CRUD για Decks και Cards στη βάση δεδομένων\"\"\"

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- DECK OPERATIONS ---

    def create_deck(self, name: str) -> Deck:
        \"\"\"Δημιουργεί ένα νέο Deck αν δεν υπάρχει ήδη\"\"\"
        deck = Deck(name=name)
        self.session.add(deck)
        self.session.commit()
        self.session.refresh(deck)
        return deck

    def get_all_decks(self) -> List[Deck]:
        \"\"\"Επιστρέφει όλα τα Decks μαζί με τις κάρτες τους\"\"\"
        statement = select(Deck).order_by(Deck.name)
        return list(self.session.scalars(statement).all())

    def get_deck_by_id(self, deck_id: int) -> Optional[Deck]:
        \"\"\"Επιστρέφει ένα Deck βάσει του ID του\"\"\"
        return self.session.get(Deck, deck_id)

    def delete_deck(self, deck_id: int) -> bool:
        \"\"\"Διαγράφει ένα Deck και όλες τις κάρτες του λόγω Cascade\"\"\"
        deck = self.get_deck_by_id(deck_id)
        if deck:
            self.session.delete(deck)
            self.session.commit()
            return True
        return False

    # --- CARD OPERATIONS ---

    def create_card(self, deck_id: int, image_path: str, word: str) -> Card:
        \"\"\"Δημιουργεί μια νέα κάρτα σε ένα συγκεκριμένο Deck\"\"\"
        card = Card(deck_id=deck_id, image_path=image_path, word=word.strip())
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def delete_card(self, card_id: int) -> bool:
        \"\"\"Διαγράφει μια κάρτα\"\"\"
        card = self.session.get(Card, card_id)
        if card:
            self.session.delete(card)
            self.session.commit()
            return True
        return False
"""

# --- ΕΚΤΕΛΕΣΗ BOOTSTRAP ---

if __name__ == "__main__":
    print("=== Έναρξη Δημιουργίας Project Flashcards ===")
    create_structure()
    
    # Συγγραφή των αρχείων με τα περιεχόμενά τους
    write_file("pyproject.toml", pyproject_content)
    write_file("src/config.py", config_content)
    write_file("src/domain/models.py", models_content)
    write_file("src/repositories/database.py", database_content)
    write_file("src/repositories/deck_repository.py", repository_content)
    
    print("\\n[✔] Το Backend Setup ολοκληρώθηκε με επιτυχία!")
    print("Παρακαλώ εκτελέστε το script για να δημιουργηθούν οι φάκελοι και τα αρχεία.")