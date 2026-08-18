"""
scripts/migrate_over_ons_nav.py
--------------------------------
Eenmalig migratiescript: geeft "Over ons" een eigen, zichtbare plek in het
hoofdmenu, net na "Club". Voorheen stond er enkel een link in de footer
(zie templates/base.html), maar die was visueel niet als link herkenbaar -
dezelfde koptekst-stijl als de niet-klikbare "Support"/"Volg ons" ernaast -
en dus in de praktijk onvindbaar. Zelfde aanpak als Vacatures eerder kreeg
(zie routes/vacatures.py): een eigen navigatie-item i.p.v. weggemoffeld
onderaan.

Idempotent: als er al een top-level "Over ons"-navitem bestaat, wordt er
niets meer aangepast.

Gebruik:
    python scripts/migrate_over_ons_nav.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import NavItem, Page


def run():
    app = create_app("development")
    with app.app_context():
        bestaand = NavItem.query.filter_by(parent_id=None, label="Over ons").first()
        if bestaand is not None:
            print("al gemigreerd, niets te doen")
            return

        club = NavItem.query.filter_by(parent_id=None, label="Club").first()
        if club is None:
            print("geen 'Club'-navitem gevonden, niets te doen")
            return

        pagina = Page.query.filter_by(slug="over-ons").first()
        if pagina is None:
            print("geen Page met slug 'over-ons' gevonden, niets te doen")
            return

        # Alles na "Club" een positie opschuiven om ruimte te maken.
        volgende_items = NavItem.query.filter(
            NavItem.parent_id.is_(None), NavItem.position > club.position
        ).all()
        for item in volgende_items:
            item.position += 1

        over_ons = NavItem(
            parent_id=None, position=club.position + 1, label="Over ons",
            item_type="page", page_id=pagina.id,
        )
        db.session.add(over_ons)
        db.session.commit()
        print("'Over ons' toegevoegd aan het hoofdmenu, net na 'Club'")


if __name__ == "__main__":
    run()
