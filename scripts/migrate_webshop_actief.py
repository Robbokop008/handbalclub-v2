"""
scripts/migrate_webshop_actief.py
------------------------------------
Eenmalig migratiescript: voegt de kolom webshop_actief toe aan de bestaande
site_instellingen-tabel (zie models.SiteInstelling). db.create_all() maakt
enkel NIEUWE tabellen aan en wijzigt geen bestaande - vandaar een directe
ALTER TABLE, zelfde aanpak als eerder bij inschrijvingen.verwerkt e.a.

DEFAULT TRUE: de webshop is nu al gewoon open, dus bestaande rijen mogen
niet per ongeluk dichtklappen zodra deze kolom bestaat.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_webshop_actief.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("site_instellingen", "webshop_actief", "BOOLEAN NOT NULL DEFAULT TRUE")
        print("klaar")


if __name__ == "__main__":
    run()
