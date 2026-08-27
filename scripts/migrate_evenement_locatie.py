"""
scripts/migrate_evenement_locatie.py
--------------------------------------
Eenmalig migratiescript: voegt de kolom locatie toe aan de bestaande
evenementen-tabel (zie models.Evenement). db.create_all() maakt enkel
NIEUWE tabellen aan en wijzigt geen bestaande - vandaar een directe
ALTER TABLE, zelfde aanpak als scripts/migrate_team_achievements.py.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_evenement_locatie.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("evenementen", "locatie", "VARCHAR(255)")
        print("klaar")


if __name__ == "__main__":
    run()
