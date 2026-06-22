# src/main.py
import sys
from PySide6.QtWidgets import QApplication
from src.repositories.database import init_db, get_db_session
from src.repositories.deck_repository import DeckRepository
from src.services.deck_service import DeckService
from src.ui.main_window import MainWindow

def main() -> None:
    """
    Το σημείο εισόδου της εφαρμογής. 
    Αρχικοποιεί τη βάση δεδομένων, συνδέει τα επίπεδα της αρχιτεκτονικής (DI)
    και εκκινεί το γραφικό περιβάλλον (PySide6).
    """
    # 1. Αρχικοποίηση της βάσης δεδομένων SQLite
    try:
        init_db()
    except Exception as e:
        print(f"Σφάλμα κατά την αρχικοποίηση της βάσης δεδομένων: {e}")
        sys.exit(1)

    # 2. Δημιουργία του database session
    db_session = get_db_session()

    # 3. Αρχικοποίηση των Repositories και Services (Dependency Injection)
    deck_repository = DeckRepository(db_session)
    deck_service = DeckService(deck_repository)

    # 4. Εκκίνηση της PySide6 QApplication
    app = QApplication(sys.argv)

    # 5. Δημιουργία και εμφάνιση του κεντρικού παραθύρου
    main_window = MainWindow(deck_service)
    main_window.show()

    # 6. Εκτέλεση της εφαρμογής και διασφάλιση καθαρού τερματισμού
    try:
        sys.exit(app.exec())
    finally:
        # Κλείσιμο του session της βάσης δεδομένων κατά την έξοδο της εφαρμογής
        db_session.close()

if __name__ == "__main__":
    main()