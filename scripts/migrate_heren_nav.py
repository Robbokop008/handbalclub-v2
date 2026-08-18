"""
scripts/migrate_heren_nav.py
--------------------------------
Eenmalig migratiescript: past een bestaande database aan zodat de
"Heren"-divider + "Heren 1"/"Heren 2"-teamlinks onder "Teams" vervangen
worden door één "Heren"-link naar de nieuwe samengevoegde
overzichtspagina (zie routes/heren.py:overzicht()). Zelfde aanpak als
scripts/migrate_dames_nav.py.

Idempotent: als er al een top-level-onder-Teams "Heren"-item van het
type 'route' bestaat, wordt er niets meer aangepast.

Gebruik:
    python scripts/migrate_heren_nav.py
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
        teams = NavItem.query.filter_by(parent_id=None, label="Teams").first()
        if teams is None:
            print("geen 'Teams'-navitem gevonden, niets te doen")
            return

        bestaand = NavItem.query.filter_by(
            parent_id=teams.id, label="Heren", item_type="route"
        ).first()
        if bestaand is not None:
            print("al gemigreerd, niets te doen")
            return

        oude_items = NavItem.query.filter(
            NavItem.parent_id == teams.id, NavItem.label == "Heren"
        ).all()
        oude_items += NavItem.query.filter_by(parent_id=teams.id, label="Heren 1").all()
        oude_items += NavItem.query.filter_by(parent_id=teams.id, label="Heren 2").all()

        if not oude_items:
            print("geen oude Heren-navitems gevonden onder Teams, niets te doen")
            return

        eerste_positie = min(item.position for item in oude_items)
        for item in oude_items:
            db.session.delete(item)

        heren = NavItem(
            parent_id=teams.id, position=eerste_positie, label="Heren",
            item_type="route", route_endpoint="heren.overzicht",
        )
        db.session.add(heren)
        db.session.commit()
        print("'Heren' is nu één link naar heren.overzicht onder Teams; oude items verwijderd")


if __name__ == "__main__":
    run()
