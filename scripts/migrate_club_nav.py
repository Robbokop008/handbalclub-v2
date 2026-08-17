"""
scripts/migrate_club_nav.py
------------------------------
Eenmalig migratiescript: past een bestaande database aan zodat "Club" in
de navbar niet langer een dropdown naar 5 aparte pagina's is, maar één
link naar de nieuwe samengevoegde overzichtspagina (zie
routes/club.py:overzicht()). Het contactformulier, dat voorheen onder
Club > Contact hing, wordt een eigen top-level navitem.

Idempotent: als "Club" al een 'route'-item is (geen kinderen meer heeft),
wordt er niets meer aangepast.

Gebruik:
    python scripts/migrate_club_nav.py
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
        club = NavItem.query.filter_by(parent_id=None, label="Club").first()
        if club is None:
            print("geen 'Club'-navitem gevonden, niets te doen")
            return

        kinderen = NavItem.query.filter_by(parent_id=club.id).all()
        if club.item_type == "route" and not kinderen:
            print("al gemigreerd, niets te doen")
            return

        for kind in kinderen:
            db.session.delete(kind)

        club.item_type = "route"
        club.route_endpoint = "club.overzicht"
        club.page_id = None

        bestaand_contact = NavItem.query.filter_by(
            parent_id=None, route_endpoint="main.contact"
        ).first()
        if bestaand_contact is None:
            # Alle top-level items na "Club" één plaats opschuiven, zodat
            # het nieuwe "Contact"-item er direct achter past.
            volgende_items = NavItem.query.filter(
                NavItem.parent_id.is_(None), NavItem.position > club.position
            ).all()
            for item in volgende_items:
                item.position += 1

            contact = NavItem(
                parent_id=None, position=club.position + 1, label="Contact",
                item_type="route", route_endpoint="main.contact",
            )
            db.session.add(contact)
            print("top-level 'Contact'-navitem aangemaakt")

        db.session.commit()
        print("'Club' is nu een directe link naar club.overzicht; oude dropdown-kinderen verwijderd")


if __name__ == "__main__":
    run()
