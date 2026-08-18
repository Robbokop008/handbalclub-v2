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

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_PAD = Path(__file__).resolve().parent.parent / "instance" / "handbalclub.db"

NIEUWE_KOLOMMEN = ["aantal_bekers", "aantal_landstitels", "aantal_europese_wedstrijden"]


def run():
    conn = sqlite3.connect(DB_PAD)
    try:
        cur = conn.execute("PRAGMA table_info(teams)")
        bestaande_kolommen = {rij[1] for rij in cur.fetchall()}

        for kolom in NIEUWE_KOLOMMEN:
            if kolom in bestaande_kolommen:
                print(f"kolom '{kolom}' bestaat al, overslaan")
                continue
            conn.execute(f"ALTER TABLE teams ADD COLUMN {kolom} INTEGER")
            print(f"kolom '{kolom}' toegevoegd")

        conn.commit()
        print("klaar")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
