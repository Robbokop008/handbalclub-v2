"""
scripts/migrate_ghandbal_nav.py
--------------------------------
Eenmalig migratiescript, in 3 stappen:
1. Het "G-Handbal"-navitem onder Teams wees naar de generieke
   teams/team_detail.html (item_type='team'). G-Handbal heeft nu een
   eigen restyled overzichtspagina (zie routes/ghandbal.py:index()), dus
   dit item wordt een gewoon route-item.
2. De inschrijvingslink staat nu ook op die overzichtspagina zelf, dus
   het aparte "Inschrijving G-Handbal"-navitem kan weg.
3. De divider-header ("G-Handbal") die voordien de teamitems groepeerde
   is niet meer nodig nu het nog maar 1 link is - zelfde aanpak als
   Dames/Heren (gewoon 1 link, geen sub-categorie).

Idempotent: als er niets meer te migreren valt, gebeurt er niets.

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
        if item is not None:
            item.item_type = "route"
            item.route_endpoint = "ghandbal.index"
            item.team_id = None
            print("'G-Handbal' wijst nu naar ghandbal.index i.p.v. de generieke teampagina")
        else:
            print("geen 'G-Handbal'-team-navitem gevonden (mogelijk al gemigreerd)")

        inschrijving = NavItem.query.filter_by(
            parent_id=teams.id, label="Inschrijving G-Handbal", item_type="route"
        ).first()
        if inschrijving is not None:
            db.session.delete(inschrijving)
            print("'Inschrijving G-Handbal'-navitem verwijderd (staat nu op de overzichtspagina)")
        else:
            print("geen apart 'Inschrijving G-Handbal'-navitem gevonden (mogelijk al gemigreerd)")

        divider = NavItem.query.filter_by(parent_id=teams.id, label="G-Handbal", item_type="divider").first()
        if divider is not None:
            db.session.delete(divider)
            print("'G-Handbal'-divider verwijderd, is nu gewoon 1 link zoals Dames/Heren")
        else:
            print("geen 'G-Handbal'-divider gevonden (mogelijk al gemigreerd)")

        db.session.commit()


if __name__ == "__main__":
    run()
