"""
scripts/migrate_pages_to_blocks.py
------------------------------------
Eenmalig migratiescript: zet de bestaande Page.body_html (één groot
rich-text-veld, van vóór de blokken-page-builder) om in één PageBlock per
pagina (block_type="rich_text"), zodat de inhoud verder via de nieuwe
blokken-builder beheerd kan worden zonder verlies van bestaande tekst.

Idempotent: pagina's die al blokken hebben, worden overgeslagen (dus geen
duplicaten bij opnieuw draaien).

Gebruik:
    python scripts/migrate_pages_to_blocks.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from models import Page, PageBlock


def run():
    app = create_app("development")
    with app.app_context():
        for page in Page.query.order_by(Page.slug).all():
            if PageBlock.query.filter_by(page_id=page.id).count() > 0:
                print(f"overgeslagen (heeft al blokken): {page.slug}")
                continue

            if not (page.body_html or "").strip():
                print(f"overgeslagen (geen body_html): {page.slug}")
                continue

            blok = PageBlock(
                page_id=page.id, block_type="rich_text", position=1,
                data={"html": page.body_html},
            )
            db.session.add(blok)
            print(f"aangemaakt: {page.slug}")

        db.session.commit()


if __name__ == "__main__":
    run()
