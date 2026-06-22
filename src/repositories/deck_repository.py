# src/repositories/deck_repository.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.models import Deck, Card

class DeckRepository:
    """Διαχειρίζεται όλες τις λειτουργίες CRUD για Decks και Cards στη βάση δεδομένων"""

    def __init__(self, session: Session) -> None:
        self.session = session

    # --- DECK OPERATIONS ---

    def create_deck(self, name: str) -> Deck:
        """Δημιουργεί ένα νέο Deck αν δεν υπάρχει ήδη"""
        deck = Deck(name=name)
        self.session.add(deck)
        self.session.commit()
        self.session.refresh(deck)
        return deck

    def get_all_decks(self) -> List[Deck]:
        """Επιστρέφει όλα τα Decks μαζί με τις κάρτες τους"""
        statement = select(Deck).order_by(Deck.name)
        return list(self.session.scalars(statement).all())

    def get_deck_by_id(self, deck_id: int) -> Optional[Deck]:
        """Επιστρέφει ένα Deck βάσει του ID του"""
        return self.session.get(Deck, deck_id)

    def delete_deck(self, deck_id: int) -> bool:
        """Διαγράφει ένα Deck και όλες τις κάρτες του λόγω Cascade"""
        deck = self.get_deck_by_id(deck_id)
        if deck:
            self.session.delete(deck)
            self.session.commit()
            return True
        return False

    # --- CARD OPERATIONS ---

    def create_card(self, deck_id: int, image_path: str, word: str) -> Card:
        """Δημιουργεί μια νέα κάρτα σε ένα συγκεκριμένο Deck"""
        card = Card(deck_id=deck_id, image_path=image_path, word=word.strip())
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def delete_card(self, card_id: int) -> bool:
        """Διαγράφει μια κάρτα"""
        card = self.session.get(Card, card_id)
        if card:
            self.session.delete(card)
            self.session.commit()
            return True
        return False
