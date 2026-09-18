"""
scripts/migrate_handleiding_bijgewerkt_op.py
------------------------------------------------
Eenmalig migratiescript: voegt de kolom handleiding_bijgewerkt_op toe aan de
bestaande site_instellingen-tabel (zie models.SiteInstelling).
db.create_all() maakt enkel NIEUWE tabellen aan en wijzigt geen bestaande -
vandaar een directe ALTER TABLE, zelfde aanpak als bij webshop_actief.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_handleiding_bijgewerkt_op.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("site_instellingen", "handleiding_bijgewerkt_op", "TIMESTAMP")
        print("klaar")


if __name__ == "__main__":
    run()
