# src/services/study_service.py
import difflib
from typing import List, Tuple
from src.domain.models import Card

class StudyService:
    """
    Υπηρεσία που διαχειρίζεται τη ροή της μελέτης (Score Tracking, State, Input Validation).
    """

    def __init__(self, cards: List[Card]) -> None:
        self.cards: List[Card] = cards
        self.current_index: int = 0
        self.score: int = 0

    def get_current_card(self) -> Optional[Card]:
        """Επιστρέφει την τρέχουσα κάρτα ή None αν τελείωσε το deck"""
        if self.is_finished():
            return None
        return self.cards[self.current_index]

    def is_finished(self) -> bool:
        """Ελέγχει αν ολοκληρώθηκε η μελέτη του deck"""
        return self.current_index >= len(self.cards)

    def next_card(self) -> bool:
        """Προχωράει στην επόμενη κάρτα. Επιστρέφει True αν υπάρχει κι άλλη κάρτα"""
        self.current_index += 1
        return not self.is_finished()

    def check_answer(self, user_answer: str) -> Tuple[bool, str, str]:
        """
        Ελέγχει την απάντηση του χρήστη.
        Επιστρέφει:
        - bool: True αν είναι ολόσωστη, False αν έχει λάθος.
        - str: Η σωστή λέξη.
        - str: HTML κείμενο που δείχνει με κόκκινο/κοραλί χρώμα πού έγινε το λάθος.
        """
        current_card = self.get_current_card()
        if not current_card:
            return False, "", ""

        correct = current_card.word.strip()
        user = user_answer.strip()

        # Case-insensitive σύγκριση για βασική ορθότητα
        is_correct = user.lower() == correct.lower()

        if is_correct:
            self.score += 1
            # Επιστρέφουμε τη σωστή λέξη χωρίς μορφοποίηση λαθών
            return True, correct, f'<span style="color: #EAEAEA;">{correct}</span>'
        else:
            self.score -= 1
            # Υπολογισμός των διαφορών χαρακτήρα προς χαρακτήρα με difflib
            diff_html = self._generate_diff_html(user, correct)
            return False, correct, diff_html

    def _generate_diff_html(self, user: str, correct: str) -> str:
        """
        Παράγει κώδικα HTML που δείχνει με χρώμα #FF555D τους χαρακτήρες 
        που λείπουν ή είναι λάθος στην προσπάθεια του χρήστη.
        """
        diff = difflib.ndiff(user.lower(), correct.lower())
        html_parts = []

        for char in diff:
            # char[0] δείχνει την κατάσταση: ' ' = σωστό, '+' = λείπει από τον χρήστη, '-' = περίσσιο γράμμα
            code = char[0]
            val = char[2:]

            if code == ' ':
                # Σωστός χαρακτήρας
                html_parts.append(f'<span style="color: #EAEAEA;">{val}</span>')
            elif code == '+':
                # Χαρακτήρας που έπρεπε να υπάρχει (λείπει από τον χρήστη) - Κοραλί με Bold
                html_parts.append(f'<span style="color: #FF555D; font-weight: bold; text-decoration: underline;">{val}</span>')
            elif code == '-':
                # Περίσσιος χαρακτήρας που έγραψε ο χρήστης (δεν τον εμφανίζουμε στη σωστή λέξη, αλλά τον αγνοούμε στο feedback)
                pass

        return "".join(html_parts)