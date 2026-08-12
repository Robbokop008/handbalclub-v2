"""
scripts/cleanup_unused_images.py
----------------------------------
Zoekt bestanden in static/images/ die nergens meer naar verwezen worden -
bv. achtergebleven van vóór de automatische opruiming bij verwijderen/
vervangen van een afbeelding (zie routes/admin.py, _delete_uploaded_image) -
en verwijdert die.

Houdt rekening met:
  - de directe afbeeldingsvelden (Page.hero_image, NieuwsBericht.afbeelding,
    Team.foto_url, Sponsor.logo, Product.image_url)
  - inline afbeeldingen die via de rich-text-editor in Page.body_html of
    NieuwsBericht.inhoud terechtgekomen zijn (<img src="/static/images/...">)
  - vaste bestanden die rechtstreeks in templates gebruikt worden, niet via
    de databank (favicon.ico)

Standaard een "dry run": toont enkel wat verwijderd zou worden. Voeg
--delete toe om ook effectief te verwijderen.

Gebruik:
    python scripts/cleanup_unused_images.py            (dry run)
    python scripts/cleanup_unused_images.py --delete    (effectief opruimen)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import Page, NieuwsBericht, Team, Sponsor, Product

# Bestanden die nooit als 'ongebruikt' beschouwd mogen worden, ook al staan
# ze niet in de databank - rechtstreeks door templates gebruikt.
VASTE_BESTANDEN = {"favicon.ico"}

IMG_SRC_RE = re.compile(r"/static/images/([^\"'\s>]+)")


def _inline_afbeeldingen(html):
    if not html:
        return set()
    return set(IMG_SRC_RE.findall(html))


def run(effectief_verwijderen):
    app = create_app("development")
    with app.app_context():
        gebruikt = set(VASTE_BESTANDEN)

        for page in Page.query.all():
            if page.hero_image:
                gebruikt.add(page.hero_image)
            gebruikt |= _inline_afbeeldingen(page.body_html)

        for bericht in NieuwsBericht.query.all():
            if bericht.afbeelding:
                gebruikt.add(bericht.afbeelding)
            gebruikt |= _inline_afbeeldingen(bericht.inhoud)

        for team in Team.query.all():
            if team.foto_url:
                gebruikt.add(team.foto_url)

        for sponsor in Sponsor.query.all():
            if sponsor.logo:
                gebruikt.add(sponsor.logo)

        for product in Product.query.all():
            if product.image_url:
                gebruikt.add(product.image_url)

        upload_folder = Path(app.config["UPLOAD_FOLDER"])
        aanwezig = {p.name for p in upload_folder.iterdir() if p.is_file()}
        ongebruikt = sorted(aanwezig - gebruikt)

        if not ongebruikt:
            print("Geen ongebruikte afbeeldingen gevonden.")
            return

        print(f"{len(ongebruikt)} ongebruikte afbeelding(en) gevonden:")
        for naam in ongebruikt:
            print(f"  - {naam}")

        if effectief_verwijderen:
            for naam in ongebruikt:
                (upload_folder / naam).unlink(missing_ok=True)
            print(f"\n{len(ongebruikt)} bestand(en) verwijderd.")
        else:
            print("\nDit was een dry run - niets verwijderd. Draai met --delete om effectief op te ruimen.")


if __name__ == "__main__":
    run(effectief_verwijderen="--delete" in sys.argv)
