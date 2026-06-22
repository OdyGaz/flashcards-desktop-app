# src/services/deck_service.py
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from PySide6.QtGui import QImage
from src.config import IMAGES_DIR
from src.domain.models import Deck, Card
from src.repositories.deck_repository import DeckRepository

class DeckService:
    """
    Υπηρεσία που διαχειρίζεται τα Decks και τις Κάρτες.
    Γέφυρα μεταξύ του UI και του Repository, αναλαμβάνει και τη διαχείριση αρχείων εικόνας.
    """

    def __init__(self, repository: DeckRepository) -> None:
        self.repository = repository

    def create_deck(self, name: str) -> Optional[Deck]:
        """Δημιουργεί ένα νέο deck, ελέγχοντας αν το όνομα είναι κενό"""
        name_clean = name.strip()
        if not name_clean:
            return None
        return self.repository.create_deck(name_clean)

    def get_all_decks(self) -> List[Deck]:
        """Επιστρέφει όλα τα διαθέσιμα decks"""
        return self.repository.get_all_decks()

    def delete_deck(self, deck_id: int) -> bool:
        """Διαγράφει ένα deck και καθαρίζει τις εικόνες των καρτών του από τον δίσκο"""
        deck = self.repository.get_deck_by_id(deck_id)
        if not deck:
            return False

        # Κρατάμε τα paths των εικόνων πριν τη διαγραφή από τη βάση
        image_paths = [card.image_path for card in deck.cards]

        # Διαγραφή από τη βάση
        success = self.repository.delete_deck(deck_id)
        
        # Διαγραφή των αρχείων εικόνας από τον δίσκο
        if success:
            for path_str in image_paths:
                try:
                    path = Path(path_str)
                    if path.exists():
                        path.unlink()
                except Exception as e:
                    print(f"Σφάλμα κατά τη διαγραφή της εικόνας {path_str}: {e}")

        return success

    def add_card_from_file(self, deck_id: int, source_path_str: str, word: str) -> Optional[Card]:
        """Αντιγράφει μια εικόνα από τοπικό αρχείο στον φάκελο data/images και δημιουργεί την κάρτα"""
        word_clean = word.strip()
        if not word_clean or not source_path_str:
            return None

        source_path = Path(source_path_str)
        if not source_path.exists():
            return None

        # Δημιουργία μοναδικού ονόματος αρχείου για αποφυγή συγκρούσεων
        file_extension = source_path.suffix if source_path.suffix else ".png"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        destination_path = IMAGES_DIR / unique_filename

        try:
            # Αντιγραφή αρχείου στον τοπικό φάκελο της εφαρμογής
            shutil.copy(source_path, destination_path)
            return self.repository.create_card(deck_id, str(destination_path), word_clean)
        except Exception as e:
            print(f"Σφάλμα κατά την αντιγραφή του αρχείου: {e}")
            return None

    def add_card_from_qimage(self, deck_id: int, qimage: QImage, word: str) -> Optional[Card]:
        """Αποθηκεύει μια εικόνα (από Clipboard/Paste) στον δίσκο και δημιουργεί την κάρτα"""
        word_clean = word.strip()
        if not word_clean or qimage.isNull():
            return None

        # Ορίζουμε PNG ως default format για paste από clipboard
        unique_filename = f"{uuid.uuid4()}.png"
        destination_path = IMAGES_DIR / unique_filename

        try:
            # Η PySide6 παρέχει αυτόματη αποθήκευση της QImage στο δίσκο
            success = qimage.save(str(destination_path), "PNG")
            if success:
                return self.repository.create_card(deck_id, str(destination_path), word_clean)
            return None
        except Exception as e:
            print(f"Σφάλμα κατά την αποθήκευση της εικόνας από το clipboard: {e}")
            return None

    def delete_card(self, card_id: int) -> bool:
        """Διαγράφει μια κάρτα και το αρχείο εικόνας της"""
        # Εύρεση της κάρτας για να πάρουμε το path της εικόνας
        card = self.repository.session.get(Card, card_id)
        if not card:
            return False

        image_path_str = card.image_path
        
        # Διαγραφή από τη βάση
        success = self.repository.delete_card(card_id)
        
        # Διαγραφή αρχείου
        if success:
            try:
                path = Path(image_path_str)
                if path.exists():
                    path.unlink()
            except Exception as e:
                print(f"Σφάλμα κατά τη διαγραφή αρχείου κάρτας: {e}")

        return success