# src/ui/styles.py
from src.config import COLOR_DARK_BASE, COLOR_LIGHT_BASE, COLOR_ACCENT

# Σύγχρονο Dark Mode stylesheet με στρογγυλεμένες γωνίες και Neumorphic επιρροές
MODERN_DARK_STYLE = f"""
QMainWindow {{
    background-color: {COLOR_DARK_BASE};
}}

QWidget {{
    background-color: {COLOR_DARK_BASE};
    color: {COLOR_LIGHT_BASE};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 14px;
}}

/* Τίτλοι και Ετικέτες */
QLabel {{
    color: {COLOR_LIGHT_BASE};
}}

QLabel#title_label {{
    font-size: 24px;
    font-weight: bold;
    color: {COLOR_ACCENT};
    margin-bottom: 10px;
}}

QLabel#score_label {{
    font-size: 18px;
    font-weight: bold;
    color: {COLOR_LIGHT_BASE};
    background-color: #323539;
    border-radius: 8px;
    padding: 6px 12px;
}}

/* Κουμπιά */
QPushButton {{
    background-color: #2F3136;
    color: {COLOR_LIGHT_BASE};
    border: 1px solid #40444B;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: bold;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLOR_ACCENT};
    color: #ffffff;
    border: 1px solid {COLOR_ACCENT};
}}

QPushButton:pressed {{
    background-color: #D4444B;
}}

QPushButton#danger_button {{
    background-color: #3A2325;
    border: 1px solid #722424;
    color: #FF555D;
}}

QPushButton#danger_button:hover {{
    background-color: {COLOR_ACCENT};
    color: #ffffff;
    border: 1px solid {COLOR_ACCENT};
}}

/* Πεδία Εισαγωγής (Inputs) */
QLineEdit {{
    background-color: #1E2022;
    border: 2px solid #323539;
    border-radius: 8px;
    padding: 10px;
    color: {COLOR_LIGHT_BASE};
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 2px solid {COLOR_ACCENT};
}}

/* Λίστες (QListWidget) */
QListWidget {{
    background-color: #1E2022;
    border: 1px solid #323539;
    border-radius: 8px;
    padding: 5px;
}}

QListWidget::item {{
    background-color: #2F3136;
    border-radius: 6px;
    padding: 12px;
    margin: 4px 2px;
    color: {COLOR_LIGHT_BASE};
    font-weight: bold;
}}

QListWidget::item:hover {{
    background-color: #3A3D42;
}}

QListWidget::item:selected {{
    background-color: {COLOR_ACCENT};
    color: #ffffff;
}}

/* ScrollBars */
QScrollBar:vertical {{
    border: none;
    background: #1E2022;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #40444B;
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_ACCENT};
}}
"""