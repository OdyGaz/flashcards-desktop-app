# src/config.py
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
