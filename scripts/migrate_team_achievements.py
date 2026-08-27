"""
scripts/migrate_team_achievements.py
--------------------------------------
Eenmalig migratiescript: voegt de kolommen aantal_bekers, aantal_landstitels
en aantal_europese_wedstrijden toe aan de bestaande teams-tabel (zie
models.Team). db.create_all() maakt enkel NIEUWE tabellen aan en wijzigt
geen bestaande - vandaar een directe ALTER TABLE, zelfde aanpak als eerder
bij nieuwsberichten.samenvatting.

Idempotent: slaat kolommen die al bestaan over.

Gebruik:
    python scripts/migrate_team_achievements.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app

NIEUWE_KOLOMMEN = ["aantal_bekers", "aantal_landstitels", "aantal_europese_wedstrijden"]


def run():
    app = get_app()
    with app.app_context():
        for kolom in NIEUWE_KOLOMMEN:
            add_column_if_missing("teams", kolom, "INTEGER")
        print("klaar")


if __name__ == "__main__":
    run()
