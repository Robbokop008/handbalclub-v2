"""
scripts/migrate_site_text_cleanup.py
--------------------------------------
Eenmalig opkuisscript voor de admin-paginabeheer: verwijdert data die dood
werd sinds de restyling van Home/Kalender en de samenvoeging van Club naar
1 pagina, en die de admin dus voor niets zou tonen/laten bewerken:

1. De 2 Page-rijen "kalender-trainingen" en "kalender-evenementen" - deze
   werden door geen enkele route of navigatie-item meer aangesproken (de
   Kalender-pagina is intussen een volledig hardcoded accordion-pagina,
   zie routes/kalender.py:overzicht()).
2. De SiteText-rijen voor "home_hero_titel", "home_hero_subtitel",
   "kalender_hero_titel" en "kalender_hero_subtitel" - deze velden staan
   niet meer in utils/site_text.py (zie SITE_TEXT_PAGINAS) omdat Home en
   Kalender geen tekst-hero meer tonen; een admin die ze via /admin/pages
   zou bewerken zag voorheen geen enkel effect op de site.

Idempotent: als de rijen al weg zijn, gebeurt er niets.

Gebruik:
    python scripts/migrate_site_text_cleanup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Page, SiteText

DODE_PAGE_SLUGS = ["kalender-trainingen", "kalender-evenementen"]
DODE_SITE_TEXT_SLEUTELS = [
    "home_hero_titel", "home_hero_subtitel",
    "kalender_hero_titel", "kalender_hero_subtitel",
]


def run():
    app = create_app("development")
    with app.app_context():
        for slug in DODE_PAGE_SLUGS:
            page = Page.query.filter_by(slug=slug).first()
            if page is not None:
                db.session.delete(page)
                print(f"Page verwijderd: {slug}")
            else:
                print(f"Page niet gevonden (mogelijk al gemigreerd): {slug}")

        for sleutel in DODE_SITE_TEXT_SLEUTELS:
            rij = SiteText.query.filter_by(sleutel=sleutel).first()
            if rij is not None:
                db.session.delete(rij)
                print(f"SiteText verwijderd: {sleutel}")
            else:
                print(f"SiteText niet gevonden (mogelijk al gemigreerd): {sleutel}")

        db.session.commit()
        print("klaar")


if __name__ == "__main__":
    run()
