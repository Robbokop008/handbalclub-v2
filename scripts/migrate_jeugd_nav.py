"""
scripts/migrate_jeugd_nav.py
--------------------------------
Eenmalig migratiescript: vervangt de bestaande "Jeugd"-dropdown
(Inschrijving nieuwe speler, Jeugdbeleidsplan, Kleuters: De Ballenbaasjes,
JM08 & JM10, JM12, J14, M14, Aanspreekpunt Integriteit, VHV - Welzijn van
de speler) door één top-level "Jeugd"-link naar de nieuwe samengevoegde
overzichtspagina (zie routes/jeugd.py:overzicht()). Zelfde aanpak als
scripts/migrate_club_nav.py / migrate_kalender_nav.py / migrate_dames_nav.py
/ migrate_heren_nav.py.

Idempotent: als er al een top-level "Jeugd"-item van het type 'route'
bestaat, wordt er niets meer aangepast.

Gebruik:
    python scripts/migrate_jeugd_nav.py
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
        bestaand = NavItem.query.filter_by(
            parent_id=None, label="Jeugd", item_type="route"
        ).first()
        if bestaand is not None:
            print("al gemigreerd, niets te doen")
            return

        oude_categorie = NavItem.query.filter_by(
            parent_id=None, label="Jeugd", item_type="category"
        ).first()
        if oude_categorie is None:
            print("geen oude 'Jeugd'-categorie gevonden, niets te doen")
            return

        positie = oude_categorie.position
        kinderen = NavItem.query.filter_by(parent_id=oude_categorie.id).all()
        for kind in kinderen:
            db.session.delete(kind)
        db.session.delete(oude_categorie)

        jeugd = NavItem(
            parent_id=None, position=positie, label="Jeugd",
            item_type="route", route_endpoint="jeugd.overzicht",
        )
        db.session.add(jeugd)
        db.session.commit()
        print("'Jeugd' is nu één link naar jeugd.overzicht; oude dropdown-items verwijderd")


if __name__ == "__main__":
    run()
