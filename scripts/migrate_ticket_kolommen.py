"""
scripts/migrate_ticket_kolommen.py
-----------------------------------
Eenmalig migratiescript: voegt de kolommen verkoop_einde en
max_per_bestelling toe aan de bestaande ticket_wedstrijden-tabel (zie
models.TicketWedstrijd). db.create_all() maakt enkel NIEUWE tabellen aan en
wijzigt geen bestaande - vandaar een directe ALTER TABLE, zelfde aanpak als
scripts/migrate_evenement_locatie.py.

Idempotent: slaat een kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_ticket_kolommen.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("ticket_wedstrijden", "verkoop_einde", "TIMESTAMP")
        add_column_if_missing("ticket_wedstrijden", "max_per_bestelling", "INTEGER")
        print("klaar")


if __name__ == "__main__":
    run()
