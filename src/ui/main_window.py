# src/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QMessageBox
from src.services.deck_service import DeckService
from src.ui.styles import MODERN_DARK_STYLE

# Εισαγωγή των views (θα δημιουργηθούν στο Βήμα 2.3)
from src.ui.views.deck_list_view import DeckListView
from src.ui.views.card_creator_view import CardCreatorView
from src.ui.views.study_view import StudyView

class MainWindow(QMainWindow):
    """
    Το κύριο παράθυρο της εφαρμογής που διαχειρίζεται την πλοήγηση
    μεταξύ των διαφορετικών οθονών χρησιμοποιώντας QStackedWidget.
    """

    def __init__(self, deck_service: DeckService) -> None:
        super().__init__()
        self.deck_service = deck_service

        self.setWindowTitle("Local Flashcards")
        self.setMinimumSize(800, 650)
        self.setStyleSheet(MODERN_DARK_STYLE)

        # Δημιουργία κεντρικού widget και stacked controller
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget(self.central_widget)
        self.layout.addWidget(self.stacked_widget)

        # Φόρτωση της αρχικής οθόνης
        self.show_deck_list()

    def show_deck_list(self) -> None:
        """Εμφανίζει την οθόνη με τα διαθέσιμα decks"""
        self._clear_stack()
        deck_list_view = DeckListView(self, self.deck_service)
        self.stacked_widget.addWidget(deck_list_view)
        self.stacked_widget.setCurrentWidget(deck_list_view)

    def show_card_creator(self, deck_id: int) -> None:
        """Εμφανίζει την οθόνη προσθήκης καρτών για ένα συγκεκριμένο deck"""
        self._clear_stack()
        card_creator_view = CardCreatorView(self, self.deck_service, deck_id)
        self.stacked_widget.addWidget(card_creator_view)
        self.stacked_widget.setCurrentWidget(card_creator_view)

    def show_study_session(self, deck_id: int) -> None:
        """Εκκινεί και εμφανίζει τη διαδικασία μελέτης για ένα deck"""
        deck = self.deck_service.repository.get_deck_by_id(deck_id)
        if not deck or len(deck.cards) == 0:
            QMessageBox.warning(
                self, 
                "Άδειο Deck", 
                "Αυτό το deck δεν έχει κάρτες. Προσθέστε μερικές κάρτες πριν ξεκινήσετε τη μελέτη!"
            )
            return

        self._clear_stack()
        # Δημιουργούμε το study view περνώντας τις κάρτες του deck
        study_view = StudyView(self, deck.cards, deck.name)
        self.stacked_widget.addWidget(study_view)
        self.stacked_widget.setCurrentWidget(study_view)

    def _clear_stack(self) -> None:
        """Καθαρίζει τα παλιά widgets από το stacked widget για αποδέσμευση μνήμης"""
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()