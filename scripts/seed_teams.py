"""
scripts/seed_teams.py
-----------------------
Eenmalig migratiescript: zet placeholder-teams klaar. De eerste 4 (Dames/
Heren) hadden al een vaste route + menulink (routes/dames.py, routes/
heren.py) maar 404'en zonder Team-rij in de database. De overige 6
(G-Handbal, FIT-Handbal, de 4 jeugd-leeftijdsgroepen) waren voorheen
gewone content-pagina's (zie scripts/seed_pages.py, ondertussen daaruit
verwijderd) - ook zij zijn organisatorisch teams, en krijgen zo dezelfde
gestructureerde admin-velden (trainer, foto, omschrijving) als Dames/Heren.
Idempotent: opnieuw draaien overschrijft bestaande rijen met dezelfde slug
i.p.v. duplicaten aan te maken.

Gebruik:
    python scripts/seed_teams.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Team


TEAMS = [
    {
        "slug": "dames-1-beloften",
        "naam": "Dames 1 & Beloften",
        "sectie": "dames",
        "categorie": "Eerste ploeg & Beloften",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "dames-regio",
        "naam": "Dames Regio",
        "sectie": "dames",
        "categorie": "Regio",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "heren-1",
        "naam": "Heren 1",
        "sectie": "heren",
        "categorie": "Eerste ploeg",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "heren-2",
        "naam": "Heren 2",
        "sectie": "heren",
        "categorie": "Tweede ploeg",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "ghandbal",
        "naam": "G-Handbal",
        "sectie": "ghandbal",
        "categorie": None,
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "fithandbal",
        "naam": "FIT-Handbal",
        "sectie": "fithandbal",
        "categorie": None,
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "jeugd-jm08-jm10",
        "naam": "JM08 & JM10",
        "sectie": "jeugd",
        "categorie": "Jeugd",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "jeugd-jm12",
        "naam": "JM12",
        "sectie": "jeugd",
        "categorie": "Jeugd",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "jeugd-j14",
        "naam": "J14",
        "sectie": "jeugd",
        "categorie": "Jeugd",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
    {
        "slug": "jeugd-m14",
        "naam": "M14",
        "sectie": "jeugd",
        "categorie": "Jeugd",
        "omschrijving": "[Placeholder] Nog geen omschrijving toegevoegd voor dit team.",
    },
]


def run():
    app = create_app("development")
    with app.app_context():
        for entry in TEAMS:
            team = Team.query.filter_by(slug=entry["slug"]).first()
            if team is None:
                team = Team(**entry)
                db.session.add(team)
                print(f"aangemaakt: {entry['slug']}")
            else:
                team.naam = entry["naam"]
                team.sectie = entry["sectie"]
                team.categorie = entry["categorie"]
                if not team.omschrijving:
                    team.omschrijving = entry["omschrijving"]
                print(f"bijgewerkt: {entry['slug']}")
        db.session.commit()
        print(f"klaar - {len(TEAMS)} teams verwerkt.")


if __name__ == "__main__":
    run()
