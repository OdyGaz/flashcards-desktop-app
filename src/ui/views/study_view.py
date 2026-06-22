# src/ui/views/study_view.py
import random
from typing import TYPE_CHECKING, List
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from src.domain.models import Card
from src.services.study_service import StudyService

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


class StudyView(QWidget):
    """
    Η οθόνη μελέτης (εξάσκησης). Προβάλλει την εικόνα, δέχεται την απάντηση,
    ελέγχει την ορθότητα, δείχνει τα λάθη με difflib (HTML) και διαχειρίζεται το σκορ.
    """

    def __init__(self, main_window: "MainWindow", cards: List[Card], deck_name: str) -> None:
        super().__init__()
        self.main_window = main_window
        self.deck_name = deck_name

        # Ανακατεύουμε τις κάρτες για καλύτερη εκμάθηση
        shuffled_cards = list(cards)
        random.shuffle(shuffled_cards)

        # Αρχικοποίηση της υπηρεσίας μελέτης
        self.study_service = StudyService(shuffled_cards)
        
        # Κατάσταση ελέγχου: True αν εμφανίζεται το feedback του λάθους, False αν περιμένει απάντηση
        self.is_showing_feedback: bool = False

        self._init_ui()
        self._load_current_card()

    def _init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Layout Κορυφής (Τίτλος & Σκορ)
        self.header_layout = QHBoxLayout()
        
        self.title = QLabel(f"Μελέτη: {self.deck_name}", self)
        self.title.setObjectName("title_label")
        
        self.score_label = QLabel("Σκορ: 0", self)
        self.score_label.setObjectName("score_label")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.score_label)
        self.layout.addLayout(self.header_layout)

        # Προβολή Εικόνας Κάρτας
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "border: 1px solid #323539; border-radius: 8px; background-color: #1E2022;"
        )
        self.image_label.setMinimumHeight(300)
        self.layout.addWidget(self.image_label)

        # Πλαίσιο Απάντησης (Input)
        self.answer_input = QLineEdit(self)
        self.answer_input.setPlaceholderText("Πληκτρολογήστε τη λέξη εδώ και πατήστε Enter...")
        self.answer_input.returnPressed.connect(self._on_enter_pressed)
        self.layout.addWidget(self.answer_input)

        # Πλαίσιο Feedback (Αποτελέσματα & Λάθη)
        self.feedback_label = QLabel("", self)
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setTextFormat(Qt.TextFormat.RichText)  # Υποστήριξη HTML χρωματισμού
        self.feedback_label.setStyleSheet("font-size: 18px; margin: 5px;")
        self.layout.addWidget(self.feedback_label)

        # Layout Κουμπιών Πλοήγησης
        self.nav_layout = QHBoxLayout()
        
        self.action_btn = QPushButton("Έλεγχος (Enter)", self)
        self.action_btn.clicked.connect(self._on_enter_pressed)
        
        self.exit_btn = QPushButton("Έξοδος", self)
        self.exit_btn.setObjectName("danger_button")
        self.exit_btn.clicked.connect(self._on_exit_clicked)

        self.nav_layout.addWidget(self.action_btn)
        self.nav_layout.addWidget(self.exit_btn)
        self.layout.addLayout(self.nav_layout)

    def _load_current_card(self) -> None:
        """Φορτώνει τα δεδομένα της τρέχουσας κάρτας στο UI"""
        card = self.study_service.get_current_card()
        if not card:
            self._finish_study()
            return

        # Φόρτωση εικόνας
        pixmap = QPixmap(card.image_path)
        if not pixmap.isNull():
            # Προσαρμογή μεγέθους διατηρώντας το aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.width() if self.image_label.width() > 100 else 600,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("⚠️ Σφάλμα: Η εικόνα δεν βρέθηκε ή έχει διαγραφεί.")

        # Επαναφορά στοιχείων εισαγωγής και feedback
        self.answer_input.clear()
        self.answer_input.setReadOnly(False) # Ενεργοποιούμε ξανά την πληκτρολόγηση
        self.answer_input.setFocus()
        self.feedback_label.clear()
        
        self.action_btn.setText("Έλεγχος (Enter)")
        self.is_showing_feedback = False

    def _on_enter_pressed(self) -> None:
        """Διαχειρίζεται το πάτημα του Enter (ή του κουμπιού δράσης)"""
        if self.is_showing_feedback:
            # Αν είμαστε σε κατάσταση feedback, το Enter προχωράει στην επόμενη κάρτα
            self._advance()
        else:
            # Αν ο χρήστης μόλις έγραψε, ελέγχουμε την απάντηση
            self._check_answer()

    def _check_answer(self) -> None:
        user_ans = self.answer_input.text().strip()
        if not user_ans:
            return

        # Έλεγχος απάντησης μέσω του service
        is_correct, correct_word, diff_html = self.study_service.check_answer(user_ans)

        # Ενημέρωση σκορ
        self.score_label.setText(f"Σκορ: {self.study_service.score}")

        # Κλείδωμα του input κατά τη διάρκεια του feedback χωρίς να χάσει το focus
        self.answer_input.setReadOnly(True) # Το κάνουμε read-only
        self.answer_input.setFocus()        # Διατηρούμε το focus για το επόμενο Enter

        if is_correct:
            self.feedback_label.setText(
                f'<span style="color: #4CAF50; font-weight: bold;">✔ Σωστά!</span><br/>'
                f'<span style="color: #EAEAEA;">{correct_word}</span>'
            )
        else:
            self.feedback_label.setText(
                f'<span style="color: #FF555D; font-weight: bold;">❌ Λάθος! Η σωστή λέξη είναι:</span><br/>'
                f'{diff_html}'
            )

        # Αλλαγή της κατάστασης και του κουμπιού
        self.action_btn.setText("Επόμενο (Enter)")
        self.is_showing_feedback = True

    def _advance(self) -> None:
        """Προχωράει στην επόμενη κάρτα ή ολοκληρώνει τη μελέτη"""
        self.study_service.next_card()
        self._load_current_card()

    def _finish_study(self) -> None:
        """Καλείται όταν τελειώσουν όλες οι κάρτες του deck"""
        QMessageBox.information(
            self,
            "Ολοκλήρωση Μελέτης",
            f"Συγχαρητήρια! Ολοκληρώσατε αυτό το deck.\\nΤελικό Σκορ: {self.study_service.score} πόντοι!"
        )
        self.main_window.show_deck_list()

    def _on_exit_clicked(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Έξοδος από τη Μελέτη",
            "Είστε σίγουροι ότι θέλετε να σταματήσετε τη μελέτη; Η τρέχουσα πρόοδος θα χαθεί.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.main_window.show_deck_list()

    def resizeEvent(self, event) -> None:
        """Εξασφαλίζει τη σωστή προσαρμογή της εικόνας όταν αλλάζει μέγεθος το παράθυρο"""
        super().resizeEvent(event)
        card = self.study_service.get_current_card()
        if card and self.image_label.pixmap() and not self.image_label.pixmap().isNull():
            pixmap = QPixmap(card.image_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.width() if self.image_label.width() > 100 else 600,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)