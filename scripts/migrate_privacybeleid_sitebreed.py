"""
scripts/migrate_privacybeleid_sitebreed.py
---------------------------------------------
Eenmalig migratiescript: de vroegere webshop-only privacyverklaring
("privacybeleid-webshop") wordt de site-brede privacyverklaring
("privacybeleid", zie scripts/seed_legal_pages.py), zodat Google Analytics
(zie config.GA_MEASUREMENT_ID en base.html) er correct naar kan verwijzen
i.p.v. enkel webshop-klanten te informeren.

Herschrijft slug, titel en inhoud van de bestaande Page-rij naar de nieuwe
versie uit seed_legal_pages.py - net als dat seed-script zelf zijn deze
inhoud dus bij het draaien overschreven. Dat is hier bewust: deze
gegevensverwerking (Analytics) bestond voordien niet, dus er is geen eerdere
admin-aanpassing die verloren kan gaan.

Idempotent: als er al een Page met slug "privacybeleid" bestaat (deze
migratie al gedraaid, of een verse install via seed_legal_pages.py), gebeurt
er niets.

Gebruik:
    python scripts/migrate_privacybeleid_sitebreed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extensions import db
from models import Page, PageBlock
from scripts._common import get_app
from scripts.seed_legal_pages import PAGES
from utils.sanitize import sanitize_html

OUDE_SLUG = "privacybeleid-webshop"
NIEUWE_ENTRY = next(entry for entry in PAGES if entry["slug"] == "privacybeleid")


def run():
    app = get_app()
    with app.app_context():
        if Page.query.filter_by(slug=NIEUWE_ENTRY["slug"]).first() is not None:
            print(f"Page '{NIEUWE_ENTRY['slug']}' bestaat al - niets te migreren.")
            return

        page = Page.query.filter_by(slug=OUDE_SLUG).first()
        if page is None:
            print(f"Page '{OUDE_SLUG}' niet gevonden - niets te migreren (mogelijk nog geen seed gedraaid).")
            return

        page.slug = NIEUWE_ENTRY["slug"]
        page.title = NIEUWE_ENTRY["title"]
        PageBlock.query.filter_by(page_id=page.id).delete()
        db.session.add(PageBlock(
            page_id=page.id, block_type="rich_text", position=1,
            data={"html": sanitize_html(NIEUWE_ENTRY["html"])},
        ))
        db.session.commit()
        print(f"Page '{OUDE_SLUG}' hernoemd naar '{NIEUWE_ENTRY['slug']}' met bijgewerkte, site-brede inhoud.")


if __name__ == "__main__":
    run()
