"""
scripts/migrate_actie_opmerking.py
-----------------------------------
Eenmalig migratiescript voor het opmerkingenveld bij acties: voegt de kolom
opmerking_label toe aan de bestaande acties-tabel (zie models.Actie). De
nieuwe tabel order_actie_opmerkingen maakt db.create_all() bij het
opstarten zelf aan.

Idempotent: slaat de kolom over als ze al bestaat.

Gebruik:
    python scripts/migrate_actie_opmerking.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._common import add_column_if_missing, get_app


def run():
    app = get_app()
    with app.app_context():
        add_column_if_missing("acties", "opmerking_label", "VARCHAR(100)")
        print("klaar")


if __name__ == "__main__":
    run()
