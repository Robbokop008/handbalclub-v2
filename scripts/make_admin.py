"""
scripts/make_admin.py
-----------------------
Geeft een BESTAANDE gebruiker adminrechten (of trekt ze in), zonder iets
anders aan het account te wijzigen. In tegenstelling tot
scripts/create_admin.py blijft het wachtwoord van de gebruiker dus
ongemoeid.

Zoekt de gebruiker op via gebruikersnaam of e-mailadres.

Gebruikt scripts/_common.py voor de juiste databankconfiguratie: zet
FLASK_CONFIG=production op de hostingdienst.

Gebruik:
    python scripts/make_admin.py jan.peeters
    python scripts/make_admin.py jan@voorbeeld.be
    python scripts/make_admin.py jan.peeters --intrekken
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, or_

from extensions import db
from models import User
from scripts._common import get_app


def run(gebruiker, intrekken=False):
    app = get_app()
    with app.app_context():
        user = User.query.filter(or_(
            User.username == gebruiker,
            func.lower(User.email) == gebruiker.lower(),
        )).first()
        if user is None:
            print(f"Geen gebruiker gevonden met gebruikersnaam of e-mailadres '{gebruiker}'.")
            sys.exit(1)

        naam = f"{user.first_name} {user.last_name} ({user.username}, {user.email})"
        nieuw = not intrekken
        if user.is_admin == nieuw:
            print(f"{naam} is al {'admin' if nieuw else 'geen admin'} - niets gewijzigd.")
            return

        user.is_admin = nieuw
        db.session.commit()
        print(f"{naam} is nu {'admin' if nieuw else 'geen admin meer'}.")


def main():
    parser = argparse.ArgumentParser(description="Geef een bestaande gebruiker adminrechten (of trek ze in).")
    parser.add_argument("gebruiker", help="gebruikersnaam of e-mailadres")
    parser.add_argument("--intrekken", action="store_true", help="adminrechten afnemen i.p.v. toekennen")
    args = parser.parse_args()
    run(args.gebruiker.strip(), args.intrekken)


if __name__ == "__main__":
    main()
