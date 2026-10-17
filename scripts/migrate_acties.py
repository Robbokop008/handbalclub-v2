"""
scripts/migrate_acties.py
--------------------------
Eenmalig migratiescript voor acties met afhaling: voegt de kolom telefoon
toe aan de bestaande orders-tabel (zie models.Order). De nieuwe tabellen
(acties, actie_artikelen, actie_varianten, afhaalmomenten,
order_actie_lines) maakt db.create_all() bij het opstarten zelf aan - dat
wijzigt enkel geen bestaande tabellen, vandaar deze ALTER TABLE.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_acties.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("orders", "telefoon", "VARCHAR(30)")
        print("klaar")


if __name__ == "__main__":
    run()
