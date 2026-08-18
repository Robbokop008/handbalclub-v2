"""
scripts/seed_pages.py
-----------------------
Eenmalig migratiescript: zet de statische placeholder-pagina's (voorheen
hardcoded templates onder Over ons/Club/Kalender/Jeugd/Vacatures) om in
Page-rijen, zodat ze voortaan via de admin beheerd kunnen worden. De
inhoud is 1-op-1 overgenomen uit de oude templates (templates/about.html
is ondertussen verwijderd, /over-ons is nu een permanente 301-redirect
naar /pagina/over-ons - zie routes/main.py).

G-Handbal, FIT-Handbal en de 4 jeugd-leeftijdsgroepen (JM08&JM10, JM12,
J14, M14) stonden hier vroeger ook in, maar zijn ondertussen team-content
gebleken en verhuisd naar Team-rijen (zie scripts/seed_teams.py) - bewust
niet meer hier, anders zou opnieuw draaien de oude pagina's terugzetten.

"kalender-trainingen" en "kalender-evenementen" stonden hier ook, maar
werden nooit door een route of navigatie-item aangesproken (dode data
sinds Kalender een hardcoded accordion-pagina werd) en zijn dus
verwijderd.

De 5 losse Club-pagina's ("club-missie-en-visie", "club-bestuur",
"club-historiek", "club-verzekering", "club-aanspreekpunt-integriteit")
en "jeugd-aanspreekpunt-integriteit" stonden hier ook, maar hun inhoud
staat intussen hardcoded op de nieuwe overzichtspagina's (zie
templates/club/overzicht.html en templates/jeugd/overzicht.html) - een
admin die deze Page-rijen bewerkte zag dus geen effect meer op de
site. Ook verwijderd; de oude /club/... en /jeugd/aanspreekpunt-
integriteit-URL's redirecten nu rechtstreeks naar de overzichtspagina
i.p.v. naar deze Page-rijen (zie routes/club.py en routes/jeugd.py).

Zie scripts/migrate_site_text_cleanup.py voor de eenmalige opkuis van de
reeds bestaande rijen van al deze verwijderde pagina's.

Idempotent: opnieuw draaien overschrijft bestaande rijen met dezelfde slug
in plaats van duplicaten aan te maken.

Gebruik:
    python scripts/seed_pages.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Page
from utils.sanitize import sanitize_html


PAGES = [
    {
        "slug": "over-ons",
        "title": "Over ons",
        "body_html": """
            <p>Een familieclub met ambitie in het Belgische handbal</p>
            <h2>Onze club</h2>
            <p>Handbal Sint-Truiden is een Belgische handbalclub uit Sint-Truiden (Limburg), opgericht in 1977 en actief binnen de Vlaamse Handbal Vereniging.</p>
            <p>De club groeide door de jaren heen uit tot een vaste waarde in het Belgische handbal, met een sterke focus op zowel prestaties als jeugdontwikkeling.</p>
            <p>Met een warme en familiale sfeer staat de club bekend om haar sterke teamgeest, inzet en passie voor de sport.</p>
            <h2>Onze waarden</h2>
            <h3>Ambitie</h3>
            <p>De club streeft naar sportieve groei en sterke prestaties in nationale competities.</p>
            <h3>Jeugdopleiding</h3>
            <p>We investeren sterk in jeugdwerking en talentontwikkeling binnen de club.</p>
            <h3>Teamspirit</h3>
            <p>Respect, inzet en samenhorigheid vormen de kern van onze clubcultuur.</p>
        """,
    },
    {
        "slug": "jeugd-jeugdbeleidsplan",
        "title": "Jeugdbeleidsplan",
        "body_html": "<p>[Placeholder] Het jeugdbeleidsplan van Handbal Sint-Truiden, jaarlijks bijgewerkt. Beschrijft de visie op jeugdopleiding, de leeftijdscategorieën en de begeleiding per leeftijdsgroep.</p>",
    },
    {
        "slug": "vacatures",
        "title": "Vacatures",
        "body_html": """
            <p>[Placeholder] Handbal Sint-Truiden is steeds op zoek naar enthousiaste vrijwilligers - trainers, scheidsrechters, bestuursleden en helpende handen.</p>
            <p>Interesse? Neem contact op via de <a href="/contact">contactpagina</a>.</p>
        """,
    },
]


def run():
    app = create_app("development")
    with app.app_context():
        for entry in PAGES:
            page = Page.query.filter_by(slug=entry["slug"]).first()
            body_html = sanitize_html(entry["body_html"])
            if page is None:
                page = Page(slug=entry["slug"], title=entry["title"], body_html=body_html, is_published=True)
                db.session.add(page)
                print(f"aangemaakt: {entry['slug']}")
            else:
                page.title = entry["title"]
                page.body_html = body_html
                page.is_published = True
                print(f"bijgewerkt: {entry['slug']}")
        db.session.commit()
        print(f"klaar - {len(PAGES)} pagina's verwerkt.")


if __name__ == "__main__":
    run()
