# src/domain/models.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Βασική κλάση για τα μοντέλα της SQLAlchemy 2.0"""
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
