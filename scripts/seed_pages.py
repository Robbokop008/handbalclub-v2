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
        "slug": "club-missie-en-visie",
        "title": "Missie en Visie",
        "body_html": """
            <h2>Onze missie</h2>
            <p>[Placeholder] Handbal Sint-Truiden wil een familiale, toegankelijke handbalclub zijn waar sportieve ontwikkeling en plezier hand in hand gaan, voor spelers van alle leeftijden en niveaus.</p>
            <h2>Onze visie</h2>
            <p>[Placeholder] We streven naar duurzame sportieve groei, met een sterke jeugdwerking als fundament en respect, teamgeest en inzet als kernwaarden.</p>
        """,
    },
    {
        "slug": "club-bestuur",
        "title": "Bestuur",
        "body_html": """
            <p>[Placeholder] Overzicht van de bestuursleden van Handbal Sint-Truiden, met hun functie binnen de club.</p>
            <h3>Voorzitter</h3>
            <p>Naam - functie</p>
            <h3>Secretaris</h3>
            <p>Naam - functie</p>
            <h3>Penningmeester</h3>
            <p>Naam - functie</p>
        """,
    },
    {
        "slug": "club-historiek",
        "title": "Historiek",
        "body_html": "<p>[Placeholder] Het verhaal van Handbal Sint-Truiden, van de oprichting in 1977 tot vandaag.</p>",
    },
    {
        "slug": "club-verzekering",
        "title": "Verzekeringsformulier",
        "body_html": """
            <p>[Placeholder] Informatie over de sportverzekering en het formulier dat je moet gebruiken bij een blessure of ongeval.</p>
            <p>Hier komt normaal een downloadbaar PDF-formulier of een link naar het verzekeringsdocument.</p>
        """,
    },
    {
        "slug": "club-aanspreekpunt-integriteit",
        "title": "Aanspreekpunt Persoonlijke Integriteit",
        "body_html": """
            <p>[Placeholder] Handbal Sint-Truiden hecht veel belang aan een veilige sportomgeving. Onze Aanspreekpunt Persoonlijke Integriteit (API) is er om grensoverschrijdend gedrag te melden of bespreekbaar te maken.</p>
            <p><strong>Contactpersoon:</strong> naam - e-mailadres</p>
        """,
    },
    {
        "slug": "jeugd-aanspreekpunt-integriteit",
        "title": "Aanspreekpunt Persoonlijke Integriteit - Jeugd",
        "body_html": """
            <p>[Placeholder] Ook binnen de jeugdwerking kan je bij onze API terecht met vragen of meldingen over grensoverschrijdend gedrag.</p>
            <p><strong>Contactpersoon:</strong> naam - e-mailadres</p>
        """,
    },
    {
        "slug": "jeugd-jeugdbeleidsplan",
        "title": "Jeugdbeleidsplan",
        "body_html": "<p>[Placeholder] Het jeugdbeleidsplan van Handbal Sint-Truiden, jaarlijks bijgewerkt. Beschrijft de visie op jeugdopleiding, de leeftijdscategorieën en de begeleiding per leeftijdsgroep.</p>",
    },
    {
        "slug": "kalender-trainingen",
        "title": "Trainingen",
        "body_html": """
            <p>[Placeholder] Overzicht van de trainingsmomenten per team - dag, uur en locatie. Wordt jaarlijks bijgewerkt.</p>
            <table>
                <thead><tr><th>Team</th><th>Dag</th><th>Uur</th><th>Locatie</th></tr></thead>
                <tbody>
                    <tr><td>Heren 1</td><td>Dinsdag</td><td>20:00 - 22:00</td><td>Sporthal Speelhof</td></tr>
                    <tr><td>Dames 1</td><td>Woensdag</td><td>19:00 - 21:00</td><td>Sporthal Speelhof</td></tr>
                </tbody>
            </table>
        """,
    },
    {
        "slug": "kalender-evenementen",
        "title": "Evenementen",
        "body_html": "<p>[Placeholder] Clubevenementen doorheen het seizoen: eetfestijnen, feesten, tornooien, ...</p>",
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
