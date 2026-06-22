# src/ui/views/deck_list_view.py
from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QListWidget, QMessageBox
)
from src.services.deck_service import DeckService

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


class DeckListView(QWidget):
    """
    Η αρχική οθόνη που εμφανίζει τη λίστα των Decks, 
    επιτρέπει τη δημιουργία νέων και την επιλογή δράσεων (Μελέτη, Προσθήκη Καρτών, Διαγραφή).
    """

    def __init__(self, main_window: "MainWindow", deck_service: DeckService) -> None:
        super().__init__()
        self.main_window = main_window
        self.deck_service = deck_service

        self._init_ui()
        self._refresh_deck_list()

    def _init_ui(self) -> None:
        # Κεντρικό layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Τίτλος
        self.title = QLabel("Τα Decks Μου", self)
        self.title.setObjectName("title_label")
        self.layout.addWidget(self.title)

        # Λίστα Decks
        self.deck_list_widget = QListWidget(self)
        self.deck_list_widget.itemDoubleClicked.connect(self._on_study_clicked)
        self.layout.addWidget(self.deck_list_widget)

        # Layout για τη δημιουργία νέου Deck
        self.create_layout = QHBoxLayout()
        self.new_deck_input = QLineEdit(self)
        self.new_deck_input.setPlaceholderText("Όνομα νέου Deck...")
        self.new_deck_input.returnPressed.connect(self._on_create_deck)
        
        self.create_btn = QPushButton("Δημιουργία Deck", self)
        self.create_btn.clicked.connect(self._on_create_deck)
        
        self.create_layout.addWidget(self.new_deck_input)
        self.create_layout.addWidget(self.create_btn)
        self.layout.addLayout(self.create_layout)

        # Layout για τα κουμπιά ενεργειών
        self.actions_layout = QHBoxLayout()
        
        self.study_btn = QPushButton("Έναρξη Μελέτης", self)
        self.study_btn.clicked.connect(self._on_study_clicked)
        
        self.add_cards_btn = QPushButton("Προσθήκη Καρτών", self)
        self.add_cards_btn.clicked.connect(self._on_add_cards_clicked)
        
        self.delete_btn = QPushButton("Διαγραφή Deck", self)
        self.delete_btn.setObjectName("danger_button")
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        self.actions_layout.addWidget(self.study_btn)
        self.actions_layout.addWidget(self.add_cards_btn)
        self.actions_layout.addWidget(self.delete_btn)
        self.layout.addLayout(self.actions_layout)

    def _refresh_deck_list(self) -> None:
        """Ανανεώνει τα decks που εμφανίζονται στη λίστα από τη βάση δεδομένων"""
        self.deck_list_widget.clear()
        decks = self.deck_service.get_all_decks()
        for deck in decks:
            # Αποθήκευση του ID του deck μέσα στο item της λίστας
            item_text = f"{deck.name} ({len(deck.cards)} κάρτες)"
            self.deck_list_widget.addItem(item_text)
            # Κρατάμε το ID του deck στο UserRole
            self.deck_list_widget.item(self.deck_list_widget.count() - 1).setData(32, deck.id)

    def _get_selected_deck_id(self) -> int:
        """Επιστρέφει το ID του επιλεγμένου deck ή -1 αν δεν υπάρχει επιλογή"""
        selected_items = self.deck_list_widget.selectedItems()
        if not selected_items:
            return -1
        return selected_items[0].data(32)

    def _on_create_deck(self) -> None:
        deck_name = self.new_deck_input.text().strip()
        if not deck_name:
            QMessageBox.warning(self, "Σφάλμα", "Παρακαλώ πληκτρολογήστε ένα όνομα για το Deck.")
            return

        try:
            deck = self.deck_service.create_deck(deck_name)
            if deck:
                self.new_deck_input.clear()
                self._refresh_deck_list()
            else:
                QMessageBox.warning(self, "Σφάλμα", "Δεν ήταν δυνατή η δημιουργία του Deck.")
        except Exception:
            QMessageBox.warning(self, "Σφάλμα", "Το όνομα αυτού του Deck υπάρχει ήδη.")

    def _on_study_clicked(self) -> None:
        deck_id = self._get_selected_deck_id()
        if deck_id == -1:
            QMessageBox.warning(self, "Επιλογή Deck", "Παρακαλώ επιλέξτε ένα Deck για μελέτη.")
            return
        self.main_window.show_study_session(deck_id)

    def _on_add_cards_clicked(self) -> None:
        deck_id = self._get_selected_deck_id()
        if deck_id == -1:
            QMessageBox.warning(self, "Επιλογή Deck", "Παρακαλώ επιλέξτε ένα Deck για να προσθέσετε κάρτες.")
            return
        self.main_window.show_card_creator(deck_id)

    def _on_delete_clicked(self) -> None:
        deck_id = self._get_selected_deck_id()
        if deck_id == -1:
            QMessageBox.warning(self, "Επιλογή Deck", "Παρακαλώ επιλέξτε ένα Deck για διαγραφή.")
            return

        confirm = QMessageBox.question(
            self,
            "Επιβεβαίωση Διαγραφής",
            "Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το Deck και όλες τις κάρτες του; Αυτή η ενέργεια δεν αναιρείται.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            if self.deck_service.delete_deck(deck_id):
                self._refresh_deck_list()
            else:
                QMessageBox.warning(self, "Σφάλμα", "Η διαγραφή απέτυχε.")