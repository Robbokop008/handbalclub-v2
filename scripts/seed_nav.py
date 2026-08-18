"""
scripts/seed_nav.py
---------------------
Eenmalig migratiescript: zet de hardcoded navbar uit templates/base.html om
in NavItem-rijen (zie models.NavItem), zodat de navigatie voortaan via de
admin beheerd kan worden (categorieën, volgorde, verplaatsen tussen
categorieën) i.p.v. hardcoded in de template.

Reproduceert de huidige navbar 1-op-1: Home, Nieuws, Club/Kalender/Teams/
Jeugd (met de Teams-groepslabels), FanShop, Flanders Trophy, Vacatures.
Het Profiel/Inloggen-blok en het winkelmandje-icoon blijven bewust
hardcoded in base.html, want hun doel hangt af van de actieve sessie.

Destructief maar idempotent: verwijdert eerst alle bestaande NavItem's en
bouwt de boom opnieuw op, dus opnieuw draaien geeft telkens dezelfde,
schone boom (eventuele nadien via de admin aangebrachte wijzigingen gaan
dan wel verloren - dit script is enkel bedoeld voor de eenmalige migratie).

Vereist dat scripts/seed_pages.py en scripts/seed_teams.py al gedraaid zijn
(de Page/Team-rijen waar dit script naar verwijst moeten al bestaan).

Gebruik:
    python scripts/seed_nav.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import NavItem, Page, Team


def _page_id(slug):
    page = Page.query.filter_by(slug=slug).first()
    if page is None:
        raise RuntimeError(f"Page met slug '{slug}' niet gevonden - draai eerst scripts/seed_pages.py")
    return page.id


def _team_id(slug):
    team = Team.query.filter_by(slug=slug).first()
    if team is None:
        raise RuntimeError(f"Team met slug '{slug}' niet gevonden - draai eerst scripts/seed_teams.py")
    return team.id


def _add(parent, position, label, **kwargs):
    item = NavItem(
        parent_id=parent.id if parent else None,
        position=position,
        label=label,
        **kwargs,
    )
    db.session.add(item)
    db.session.flush()  # zodat item.id beschikbaar is voor eventuele kinderen
    return item


def run():
    app = create_app("development")
    with app.app_context():
        NavItem.query.delete()
        db.session.commit()

        pos = 0

        pos += 1
        _add(None, pos, "Home", item_type="route", route_endpoint="main.home")

        pos += 1
        _add(None, pos, "Nieuws", item_type="route", route_endpoint="main.nieuws")

        # "Club" is één samengevoegde overzichtspagina (missie/visie +
        # accordions voor Contact/Historiek/API/Verzekering) i.p.v. een
        # dropdown naar 5 aparte pagina's - zie routes/club.py:overzicht().
        pos += 1
        _add(None, pos, "Club", item_type="route", route_endpoint="club.overzicht")

        # Het contactformulier hing voorheen onder Club > Contact; nu Club
        # geen dropdown meer is, staat het als eigen top-level item.
        pos += 1
        _add(None, pos, "Contact", item_type="route", route_endpoint="main.contact")

        pos += 1
        # Zelfde aanpak als "Club": één samengevoegde overzichtspagina
        # (Wedstrijden/Trainingen/Evenementen als accordions) i.p.v. een
        # dropdown naar 3 aparte bestemmingen - zie
        # routes/kalender.py:overzicht().
        _add(None, pos, "Kalender", item_type="route", route_endpoint="kalender.overzicht")

        pos += 1
        teams = _add(None, pos, "Teams", item_type="category")
        # "Dames 1 & Beloften" en "Dames Regio" staan samen op één
        # overzichtspagina (accordions) i.p.v. als 2 aparte teamlinks -
        # zie routes/dames.py:overzicht().
        _add(teams, 1, "Dames", item_type="route", route_endpoint="dames.overzicht")
        # Zelfde als Dames: "Heren 1" en "Heren 2" op één overzichtspagina
        # i.p.v. als 2 aparte teamlinks - zie routes/heren.py:overzicht().
        _add(teams, 2, "Heren", item_type="route", route_endpoint="heren.overzicht")
        # G-Handbal heeft sinds kort een eigen restyled overzichtspagina
        # i.p.v. de generieke teams/team_detail.html, met daarop nu ook de
        # inschrijvingslink - zie routes/ghandbal.py:index(). Zelfde aanpak
        # als Dames/Heren hierboven: gewoon 1 route-item, geen divider meer.
        _add(teams, 3, "G-Handbal", item_type="route", route_endpoint="ghandbal.index")
        _add(teams, 6, "FIT-Handbal", item_type="divider")
        _add(teams, 7, "FIT-Handbal", item_type="team", team_id=_team_id("fithandbal"))

        # "Jeugd" is één samengevoegde overzichtspagina (Beleidsplan/
        # Interesse/Ballenbaasjes als zwevende kaarten + JM08&JM10/JM12/
        # JM14/Welzijn als accordions) i.p.v. een dropdown naar 9 aparte
        # bestemmingen - zelfde aanpak als Club/Kalender/Dames/Heren, zie
        # routes/jeugd.py:overzicht().
        pos += 1
        _add(None, pos, "Jeugd", item_type="route", route_endpoint="jeugd.overzicht")

        pos += 1
        _add(None, pos, "FanShop", item_type="route", route_endpoint="shop.products")

        pos += 1
        flanders_trophy = _add(None, pos, "Flanders Trophy", item_type="category")
        _add(flanders_trophy, 1, "Website", item_type="external", external_url=app.config["FLANDERS_TROPHY_WEBSITE_URL"], open_in_new_tab=True)
        _add(flanders_trophy, 2, "Instagram", item_type="external", external_url=app.config["FLANDERS_TROPHY_INSTAGRAM_URL"], open_in_new_tab=True)
        _add(flanders_trophy, 3, "Facebook", item_type="external", external_url=app.config["FLANDERS_TROPHY_FACEBOOK_URL"], open_in_new_tab=True)

        pos += 1
        _add(None, pos, "Vacatures", item_type="page", page_id=_page_id("vacatures"))

        db.session.commit()
        print(f"klaar - {NavItem.query.count()} navitems aangemaakt.")


if __name__ == "__main__":
    run()
