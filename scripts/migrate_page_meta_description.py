"""
scripts/migrate_page_meta_description.py
------------------------------------------
Eenmalig migratiescript: voegt de kolom meta_description toe aan de
bestaande pages-tabel (zie models.Page). db.create_all() maakt enkel
NIEUWE tabellen aan en wijzigt geen bestaande - vandaar een directe
ALTER TABLE, zelfde aanpak als scripts/migrate_team_achievements.py.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_page_meta_description.py
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_PAD = Path(__file__).resolve().parent.parent / "instance" / "handbalclub.db"


def run():
    conn = sqlite3.connect(DB_PAD)
    try:
        cur = conn.execute("PRAGMA table_info(pages)")
        bestaande_kolommen = {rij[1] for rij in cur.fetchall()}

        if "meta_description" in bestaande_kolommen:
            print("kolom 'meta_description' bestaat al, overslaan")
        else:
            conn.execute("ALTER TABLE pages ADD COLUMN meta_description VARCHAR(300)")
            print("kolom 'meta_description' toegevoegd")

        conn.commit()
        print("klaar")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
