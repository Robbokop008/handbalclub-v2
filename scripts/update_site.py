"""
scripts/update_site.py
------------------------
Eén script dat alle veilig-herhaalbare aanpassingen doorvoert die nodig
zijn om een bestaande (al live/bevolkte) databank in orde te brengen -
i.p.v. bij elke update een reeks losse scripts na elkaar te moeten
onthouden en draaien op de hostingdienst.

Roept enkel scripts aan die idempotent zijn EN geen risico lopen om
handmatige admin-aanpassingen te overschrijven: schema-aanpassingen
(nieuwe kolommen) en gerichte datacorrecties (bv. navigatie-herstructu-
rering) die zichzelf controleren voor ze iets wijzigen.

NIET inbegrepen, bewust:
  - scripts/seed_pages.py, seed_teams.py, seed_nav.py, seed_legal_pages.py
    Dit zijn eenmalige BOOTSTRAP-scripts voor een nieuwe/lege databank: ze
    overschrijven content op basis van slug/label zonder te checken of een
    admin die nadien handmatig aangepast heeft. Enkel handmatig draaien bij
    het allereerst opzetten van een nieuwe site (zie README.md).
  - scripts/cleanup_unused_images.py
    Verwijdert bestanden - dat vergt een menselijke blik op de lijst eerst.
    Dit script draait 'm daarom enkel als dry run (louter ter info, er
    wordt nooit iets verwijderd); zie de melding onderaan de output om
    zelf --delete te draaien indien gewenst.

Gebruikt scripts/_common.py voor de juiste databankconfiguratie: zet de
omgevingsvariabele FLASK_CONFIG=production op de hostingdienst (zelfde
manier waarop wsgi.py dat voor de site zelf al doet), anders wordt net als
lokaal de development-config gebruikt.

Volgorde is van belang: de navigatie-consolidatiescripts (club/kalender/
dames/heren/jeugd/ghandbal/fithandbal/over_ons) moeten vóór
reorganize_nav_menu draaien, want die laatste gaat er net van uit dat de
navboom al in zijn geconsolideerde vorm staat (bv. "Jeugd" als één
route-item i.p.v. een dropdown) voor hij de nieuwe dropdown-groepering
("Over de club") aanmaakt.

Gebruik:
    python scripts/update_site.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import (
    migrate_page_meta_description,
    migrate_team_achievements,
    migrate_evenement_locatie,
    migrate_pages_to_blocks,
    migrate_site_text_cleanup,
    migrate_club_nav,
    migrate_kalender_nav,
    migrate_dames_nav,
    migrate_heren_nav,
    migrate_jeugd_nav,
    migrate_ghandbal_nav,
    migrate_fithandbal_nav,
    migrate_over_ons_nav,
    reorganize_nav_menu,
    cleanup_unused_images,
)

# Volgorde is van belang - zie docstring hierboven.
STAPPEN = [
    ("Kolom: pages.meta_description", migrate_page_meta_description.run),
    ("Kolommen: teams.aantal_*", migrate_team_achievements.run),
    ("Kolom: evenementen.locatie", migrate_evenement_locatie.run),
    ("Pagina's omzetten naar blokken", migrate_pages_to_blocks.run),
    ("Opkuis dode pagina's/site-teksten", migrate_site_text_cleanup.run),
    ("Navigatie: Club", migrate_club_nav.run),
    ("Navigatie: Kalender", migrate_kalender_nav.run),
    ("Navigatie: Dames", migrate_dames_nav.run),
    ("Navigatie: Heren", migrate_heren_nav.run),
    ("Navigatie: Jeugd", migrate_jeugd_nav.run),
    ("Navigatie: G-Handbal", migrate_ghandbal_nav.run),
    ("Navigatie: FIT-Handbal", migrate_fithandbal_nav.run),
    ("Navigatie: Over ons", migrate_over_ons_nav.run),
    ("Navigatie: herindelen in dropdowns", reorganize_nav_menu.run),
]


def run():
    for titel, stap in STAPPEN:
        print(f"\n=== {titel} ===")
        stap()

    print("\n=== Ongebruikte afbeeldingen (enkel ter info, dry run) ===")
    cleanup_unused_images.run(effectief_verwijderen=False)

    print("\nAlles klaar. Draai 'python scripts/cleanup_unused_images.py --delete' "
          "zelf nog handmatig als je de hierboven getoonde afbeeldingen ook echt wil verwijderen.")


if __name__ == "__main__":
    run()
