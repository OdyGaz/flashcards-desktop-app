# fix_syntax.py
import pathlib

print("=== Έναρξη Αυτόματης Διόρθωσης Συντακτικών Σφαλμάτων ===")

# Σάρωση όλων των python αρχείων στον φάκελο src
for path in pathlib.Path("src").rglob("*.py"):
    content = path.read_text(encoding="utf-8")
    
    # Αντικατάσταση του \" με σκέτο "
    if '\\"' in content:
        corrected_content = content.replace('\\"', '"')
        path.write_text(corrected_content, encoding="utf-8")
        print(f"[✔] Διορθώθηκε το αρχείο: {path}")

print("=== Η διόρθωση ολοκληρώθηκε! ===")