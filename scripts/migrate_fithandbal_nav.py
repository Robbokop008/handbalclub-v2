"""
scripts/migrate_fithandbal_nav.py
--------------------------------
Eenmalig migratiescript: het "FIT-Handbal"-navitem onder Teams stond als
divider + team-item (item_type='team', generieke teams/team_detail.html).
FIT-Handbal heeft nu een eigen restyled overzichtspagina (zie
routes/fithandbal.py:index()), dus dit wordt net als G-Handbal gewoon 1
route-item, geen divider meer - zelfde aanpak als
scripts/migrate_ghandbal_nav.py.

Idempotent: als er niets meer te migreren valt, gebeurt er niets.

Gebruik:
    python scripts/migrate_fithandbal_nav.py
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

        item = NavItem.query.filter_by(parent_id=teams.id, label="FIT-Handbal", item_type="team").first()
        if item is not None:
            item.item_type = "route"
            item.route_endpoint = "fithandbal.index"
            item.team_id = None
            print("'FIT-Handbal' wijst nu naar fithandbal.index i.p.v. de generieke teampagina")
        else:
            print("geen 'FIT-Handbal'-team-navitem gevonden (mogelijk al gemigreerd)")

        divider = NavItem.query.filter_by(parent_id=teams.id, label="FIT-Handbal", item_type="divider").first()
        if divider is not None:
            db.session.delete(divider)
            print("'FIT-Handbal'-divider verwijderd, is nu gewoon 1 link zoals Dames/Heren/G-Handbal")
        else:
            print("geen 'FIT-Handbal'-divider gevonden (mogelijk al gemigreerd)")

        db.session.commit()


if __name__ == "__main__":
    run()
