"""
scripts/migrate_ghandbal_nav.py
--------------------------------
Eenmalig migratiescript: het "G-Handbal"-navitem onder Teams wees naar de
generieke teams/team_detail.html (item_type='team'). G-Handbal heeft nu
een eigen restyled overzichtspagina (zie routes/ghandbal.py:index()), dus
dit item wordt een gewoon route-item.

Idempotent: als het item al item_type='route' heeft, wordt er niets meer
aangepast.

Gebruik:
    python scripts/migrate_ghandbal_nav.py
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

        item = NavItem.query.filter_by(parent_id=teams.id, label="G-Handbal", item_type="team").first()
        if item is None:
            print("geen 'G-Handbal'-team-navitem gevonden, niets te doen (mogelijk al gemigreerd)")
            return

        item.item_type = "route"
        item.route_endpoint = "ghandbal.index"
        item.team_id = None
        db.session.commit()
        print("'G-Handbal' wijst nu naar ghandbal.index i.p.v. de generieke teampagina")


if __name__ == "__main__":
    run()
