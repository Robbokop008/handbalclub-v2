"""
utils/validators.py
---------------------
Validatiefuncties voor gebruikersinvoer die op meerdere plekken nodig zijn:
registratie (routes/auth.py) en het aanmaken van admin-accounts
(routes/admin.py).
"""

import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email or ""))


def is_valid_password(password):
    """Minimaal 8 tekens, met minstens 1 cijfer en 1 speciaal teken."""
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        return False
    return True
