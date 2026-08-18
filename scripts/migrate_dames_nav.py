"""
scripts/migrate_dames_nav.py
--------------------------------
Eenmalig migratiescript: past een bestaande database aan zodat de
"Dames"-divider + "Dames 1 & Beloften"/"Dames Regio"-teamlinks onder
"Teams" vervangen worden door één "Dames"-link naar de nieuwe
samengevoegde overzichtspagina (zie routes/dames.py:overzicht()).
Zelfde aanpak als scripts/migrate_club_nav.py.

Idempotent: als er al een top-level-onder-Teams "Dames"-item van het
type 'route' bestaat, wordt er niets meer aangepast.

Gebruik:
    python scripts/migrate_dames_nav.py
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
            parent_id=teams.id, label="Dames", item_type="route"
        ).first()
        if bestaand is not None:
            print("al gemigreerd, niets te doen")
            return

        oude_items = NavItem.query.filter(
            NavItem.parent_id == teams.id, NavItem.label == "Dames"
        ).all()
        oude_items += NavItem.query.filter_by(parent_id=teams.id, label="Dames 1 & Beloften").all()
        oude_items += NavItem.query.filter_by(parent_id=teams.id, label="Dames Regio").all()

        if not oude_items:
            print("geen oude Dames-navitems gevonden onder Teams, niets te doen")
            return

        eerste_positie = min(item.position for item in oude_items)
        for item in oude_items:
            db.session.delete(item)

        dames = NavItem(
            parent_id=teams.id, position=eerste_positie, label="Dames",
            item_type="route", route_endpoint="dames.overzicht",
        )
        db.session.add(dames)
        db.session.commit()
        print("'Dames' is nu één link naar dames.overzicht onder Teams; oude items verwijderd")


if __name__ == "__main__":
    run()
