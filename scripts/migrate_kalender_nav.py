"""
scripts/migrate_kalender_nav.py
----------------------------------
Eenmalig migratiescript: past een bestaande database aan zodat "Kalender"
in de navbar niet langer een dropdown naar 3 aparte bestemmingen is, maar
één link naar de nieuwe samengevoegde overzichtspagina (zie
routes/kalender.py:overzicht()). Zelfde aanpak als
scripts/migrate_club_nav.py.

Idempotent: als "Kalender" al een 'route'-item is (geen kinderen meer
heeft), wordt er niets meer aangepast.

Gebruik:
    python scripts/migrate_kalender_nav.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import NavItem


def run():
    app = create_app("development")
    with app.app_context():
        kalender = NavItem.query.filter_by(parent_id=None, label="Kalender").first()
        if kalender is None:
            print("geen 'Kalender'-navitem gevonden, niets te doen")
            return

        kinderen = NavItem.query.filter_by(parent_id=kalender.id).all()
        if kalender.item_type == "route" and not kinderen:
            print("al gemigreerd, niets te doen")
            return

        for kind in kinderen:
            db.session.delete(kind)

        kalender.item_type = "route"
        kalender.route_endpoint = "kalender.overzicht"
        kalender.page_id = None

        db.session.commit()
        print("'Kalender' is nu een directe link naar kalender.overzicht; oude dropdown-kinderen verwijderd")


if __name__ == "__main__":
    run()
