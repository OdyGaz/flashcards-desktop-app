# src/ui/views/card_creator_view.py
from typing import TYPE_CHECKING, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QApplication
)
from src.services.deck_service import DeckService

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


class CardCreatorView(QWidget):
    """
    Η οθόνη δημιουργίας νέων καρτών. Υποστηρίζει Drag & Drop (ή File Dialog)
    καθώς και Direct Paste από το Clipboard (Printscreen).
    """

    def __init__(self, main_window: "MainWindow", deck_service: DeckService, deck_id: int) -> None:
        super().__init__()
        self.main_window = main_window
        self.deck_service = deck_service
        self.deck_id = deck_id

        # Προσωρινή αποθήκευση των δεδομένων εικόνας
        self.selected_file_path: Optional[str] = None
        self.pasted_qimage: Optional[QImage] = None

        self._init_ui()

    def _init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Τίτλος
        deck = self.deck_service.repository.get_deck_by_id(self.deck_id)
        deck_name = deck.name if deck else ""
        self.title = QLabel(f"Προσθήκη Καρτών στο Deck: {deck_name}", self)
        self.title.setObjectName("title_label")
        self.layout.addWidget(self.title)

        # Πλαίσιο προεπισκόπησης εικόνας
        self.image_preview = QLabel("Δεν έχει επιλεγεί εικόνα\\n(Πατήστε 'Επικόλληση' ή κάντε Browse)", self)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet(
            "border: 2px dashed #40444B; border-radius: 8px; background-color: #1E2022; padding: 20px;"
        )
        self.image_preview.setMinimumHeight(250)
        self.layout.addWidget(self.image_preview)

        # Layout για τον έλεγχο εισαγωγής εικόνας
        self.image_buttons_layout = QHBoxLayout()
        
        self.browse_btn = QPushButton("📁 Αναζήτηση Εικόνας (Browse)", self)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        
        self.paste_btn = QPushButton("📋 Επικόλληση (Paste Screenshot)", self)
        self.paste_btn.clicked.connect(self._on_paste_clicked)

        self.image_buttons_layout.addWidget(self.browse_btn)
        self.image_buttons_layout.addWidget(self.paste_btn)
        self.layout.addLayout(self.image_buttons_layout)

        # Πεδίο εισαγωγής λέξης-στόχου
        self.word_input = QLineEdit(self)
        self.word_input.setPlaceholderText("Πληκτρολογήστε τη σωστή λέξη/φράση...")
        self.word_input.returnPressed.connect(self._on_save_clicked)
        self.layout.addWidget(self.word_input)

        # Layout για τα κουμπιά αποθήκευσης/επιστροφής
        self.navigation_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Αποθήκευση Κάρτας", self)
        self.save_btn.clicked.connect(self._on_save_clicked)
        
        self.back_btn = QPushButton("⬅ Πίσω στα Decks", self)
        self.back_btn.clicked.connect(self._on_back_clicked)

        self.navigation_layout.addWidget(self.save_btn)
        self.navigation_layout.addWidget(self.back_btn)
        self.layout.addLayout(self.navigation_layout)

    def _on_browse_clicked(self) -> None:
        file_filter = "Εικόνες (*.png *.jpg *.jpeg *.bmp *.webp)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Επιλογή Εικόνας", "", file_filter)
        
        if file_path:
            self.selected_file_path = file_path
            self.pasted_qimage = None  # Ακύρωση προηγούμενου clipboard paste αν υπήρχε
            
            # Ενημέρωση προεπισκόπησης
            pixmap = QPixmap(file_path)
            self._set_preview_pixmap(pixmap)

    def _on_paste_clicked(self) -> None:
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            qimage = clipboard.image()
            if not qimage.isNull():
                self.pasted_qimage = qimage
                self.selected_file_path = None  # Ακύρωση προηγούμενου αρχείου αν υπήρχε
                
                # Μετατροπή QImage σε QPixmap για προβολή
                pixmap = QPixmap.fromImage(qimage)
                self._set_preview_pixmap(pixmap)
            else:
                QMessageBox.warning(self, "Σφάλμα Clipboard", "Η εικόνα στο πρόχειρο είναι κατεστραμμένη.")
        else:
            QMessageBox.warning(
                self, 
                "Κενό Πρόχειρο", 
                "Δεν βρέθηκε εικόνα στο πρόχειρο. Κάντε Printscreen (ή Win+Shift+S) και δοκιμάστε ξανά."
            )

    def _set_preview_pixmap(self, pixmap: QPixmap) -> None:
        """Προσαρμόζει την εικόνα στο μέγεθος του preview label χωρίς να την παραμορφώνει"""
        scaled_pixmap = pixmap.scaled(
            self.image_preview.width() - 20, 
            self.image_preview.height() - 20, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_preview.setPixmap(scaled_pixmap)

    def _on_save_clicked(self) -> None:
        word = self.word_input.text().strip()
        if not word:
            QMessageBox.warning(self, "Λείπουν Στοιχεία", "Παρακαλώ εισάγετε τη σωστή λέξη για την κάρτα.")
            return

        if not self.selected_file_path and not self.pasted_qimage:
            QMessageBox.warning(self, "Λείπει Εικόνα", "Παρακαλώ επιλέξτε μια εικόνα ή κάντε επικόλληση (Paste).")
            return

        # Αποθήκευση ανάλογα με την πηγή της εικόνας
        card = None
        if self.selected_file_path:
            card = self.deck_service.add_card_from_file(self.deck_id, self.selected_file_path, word)
        elif self.pasted_qimage:
            card = self.deck_service.add_card_from_qimage(self.deck_id, self.pasted_qimage, word)

        if card:
            # Καθαρισμός φορμών για την επόμενη κάρτα
            self.word_input.clear()
            self.image_preview.clear()
            self.image_preview.setText("Δεν έχει επιλεγεί εικόνα\\n(Πατήστε 'Επικόλληση' ή κάντε Browse)")
            self.selected_file_path = None
            self.pasted_qimage = None
            QMessageBox.information(self, "Επιτυχία", "Η κάρτα προστέθηκε με επιτυχία!")
        else:
            QMessageBox.warning(self, "Σφάλμα", "Παρουσιάστηκε σφάλμα κατά την αποθήκευση της κάρτας.")

    def _on_back_clicked(self) -> None:
        self.main_window.show_deck_list()