"""
scripts/migrate_shop_hero_tekst.py
-----------------------------------
Eenmalig migratiescript: de hero-titel van de webshop was "Ontdek onze
collectie", wat enkel over kledij gaat - intussen verkoopt de webshop ook
tickets en acties. Site-teksten worden bij het eerste bezoek met hun
standaardwaarde in de databank gezet (zie utils/site_text.py,
get_site_teksten), dus een nieuwe standaardwaarde alleen verandert niets
aan een bestaande site.

Vervangt de titel enkel als die nog op de oude standaardwaarde staat: een
titel die een admin zelf aanpaste, blijft ongemoeid. De nieuwe hero-
subtekst (shop_hero_subtitel) komt er vanzelf bij het eerste bezoek.

Idempotent: na de eerste keer staat de oude waarde er niet meer.

Gebruik:
    python scripts/migrate_shop_hero_tekst.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extensions import db
from models import SiteText
from scripts._common import get_app

OUDE_TITEL = "Ontdek onze collectie"
NIEUWE_TITEL = "Fanshop"


def run():
    app = get_app()
    with app.app_context():
        tekst = SiteText.query.filter_by(sleutel="shop_hero_titel").first()
        if tekst is None or tekst.waarde != OUDE_TITEL:
            print("shop_hero_titel staat niet (meer) op de oude standaardwaarde, overslaan")
            return
        tekst.waarde = NIEUWE_TITEL
        db.session.commit()
        print(f"shop_hero_titel aangepast naar '{NIEUWE_TITEL}'")


if __name__ == "__main__":
    run()
