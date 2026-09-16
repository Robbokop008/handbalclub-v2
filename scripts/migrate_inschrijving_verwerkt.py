"""
scripts/migrate_inschrijving_verwerkt.py
------------------------------------------
Eenmalig migratiescript: voegt de kolom verwerkt toe aan de bestaande
inschrijvingen-tabel (zie models.Inschrijving). db.create_all() maakt enkel
NIEUWE tabellen aan en wijzigt geen bestaande - vandaar een directe ALTER
TABLE, zelfde aanpak als eerder bij teams.aantal_bekers e.a.

DEFAULT FALSE zorgt dat bestaande rijen (allemaal al binnengekomen vóór
deze kolom bestond) niet per ongeluk als "verwerkt" gelden.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_inschrijving_verwerkt.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("inschrijvingen", "verwerkt", "BOOLEAN NOT NULL DEFAULT FALSE")
        print("klaar")


if __name__ == "__main__":
    run()
