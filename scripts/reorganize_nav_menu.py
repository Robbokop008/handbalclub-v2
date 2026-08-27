"""
scripts/reorganize_nav_menu.py
--------------------------------
Eenmalig herindelingsscript: groepeert een aantal bestaande top-level
NavItem's in dropdowns, om het hamburgermenu minder druk te maken (van
11 naar 7 hoofditems). Zie models.NavItem / utils/nav.py voor hoe de
navboom is opgebouwd.

In tegenstelling tot scripts/seed_nav.py verwijdert dit script NIETS en
bouwt het niet alles opnieuw op - het zoekt bestaande rijen op via hun
huidige label (top-level, parent_id is None) en herparent/herordent ze:

- Nieuwe dropdown "Over de club" -> Club, Over ons, Contact, Vacatures
- "Jeugd" verhuist naar de bestaande "Teams"-dropdown (samen met Dames,
  Heren, G-Handbal, FIT-Handbal)
- Home, Nieuws, Kalender, FanShop en Flanders Trophy blijven zoals ze zijn

Idempotent: opnieuw draaien geeft dezelfde eindstructuur (geen
duplicaten, geen fouten), want het werkt op het huidige label i.p.v.
blind alles te herbouwen. Als een verwacht item niet gevonden wordt (bv.
al herbenoemd via de admin), wordt die ene stap overgeslagen met een
duidelijke melding i.p.v. het hele script te laten crashen.

Gebruik:
    python scripts/reorganize_nav_menu.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extensions import db
from models import NavItem
from scripts._common import get_app


def _top_level(label):
    return NavItem.query.filter_by(parent_id=None, label=label).first()


def _child(parent, label):
    if parent is None:
        return None
    return NavItem.query.filter_by(parent_id=parent.id, label=label).first()


def run():
    app = get_app()
    with app.app_context():
        teams = _top_level("Teams")
        if teams is None or teams.item_type != "category":
            print("WAARSCHUWING: top-level categorie 'Teams' niet gevonden, sla die stap over")
        else:
            jeugd = _top_level("Jeugd") or _child(teams, "Jeugd")
            if jeugd is None:
                print("WAARSCHUWING: 'Jeugd' niet gevonden (top-level of onder 'Teams'), sla die stap over")
            else:
                jeugd.parent_id = teams.id
                jeugd.position = 1
                print("'Jeugd' staat in de 'Teams'-dropdown")

            volgorde_teams = ["Dames", "Heren", "G-Handbal", "FIT-Handbal"]
            for i, label in enumerate(volgorde_teams, start=2):
                item = _child(teams, label)
                if item is None:
                    print(f"WAARSCHUWING: '{label}' niet gevonden onder 'Teams', sla over")
                    continue
                item.position = i

        over_de_club = _top_level("Over de club")
        if over_de_club is None:
            over_de_club = NavItem(
                parent_id=None, position=0, label="Over de club", item_type="category",
            )
            db.session.add(over_de_club)
            db.session.flush()
            print("nieuwe dropdown 'Over de club' aangemaakt")
        else:
            print("dropdown 'Over de club' bestaat al, hergebruiken")

        volgorde_over_de_club = ["Club", "Over ons", "Contact", "Vacatures"]
        for i, label in enumerate(volgorde_over_de_club, start=1):
            item = _top_level(label)
            if item is None:
                # Kan al onder "Over de club" hangen van een vorige run.
                item = _child(over_de_club, label)
            if item is None:
                print(f"WAARSCHUWING: '{label}' niet gevonden, sla die stap over")
                continue
            item.parent_id = over_de_club.id
            item.position = i
            print(f"'{label}' verplaatst naar de 'Over de club'-dropdown")

        # Nette volgorde voor de overgebleven top-level items.
        top_level_volgorde = [
            ("Home", 1), ("Nieuws", 2), ("Kalender", 3), ("Teams", 4),
            ("Over de club", 5), ("FanShop", 6), ("Flanders Trophy", 7),
        ]
        for label, positie in top_level_volgorde:
            item = _top_level(label)
            if item is None:
                print(f"WAARSCHUWING: top-level item '{label}' niet gevonden, sla over")
                continue
            item.position = positie

        db.session.commit()

        print("\nNieuwe navboom:")
        for item in NavItem.query.filter_by(parent_id=None).order_by(NavItem.position).all():
            print(f"- {item.label} ({item.item_type})")
            for child in NavItem.query.filter_by(parent_id=item.id).order_by(NavItem.position).all():
                print(f"    - {child.label} ({child.item_type})")

        print("\nklaar")


if __name__ == "__main__":
    run()
