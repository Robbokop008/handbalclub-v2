"""
scripts/migrate_admin_lijsten.py
---------------------------------
Eenmalig migratiescript voor de overzichtelijkere adminlijsten: voegt toe

  - orders.gearchiveerd: bestellingen die een admin uit de standaardlijst
    haalde (zie models.Order)
  - inschrijvingen.notitie en vergeet_mij_verzoeken.notitie: interne
    notitie op de fiche, enkel voor admins

db.create_all() maakt enkel NIEUWE tabellen aan en wijzigt geen bestaande -
vandaar een directe ALTER TABLE, zelfde aanpak als
scripts/migrate_inschrijving_verwerkt.py.

Idempotent: slaat een kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_admin_lijsten.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("orders", "gearchiveerd", "BOOLEAN NOT NULL DEFAULT FALSE")
        add_column_if_missing("inschrijvingen", "notitie", "TEXT")
        add_column_if_missing("vergeet_mij_verzoeken", "notitie", "TEXT")
        print("klaar")


if __name__ == "__main__":
    run()
