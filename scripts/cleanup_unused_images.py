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
    - body_html is legacy sinds de page-builder (zie models.PageBlock), maar
      de kolom bevat nog steeds de originele inhoud van vóór de migratie
      (scripts/migrate_pages_to_blocks.py leest ze enkel uit, wist niets)
  - afbeeldingen gebruikt in PageBlock's (image_gallery-/columns-blokken,
    zie utils/page_blocks.py)
  - afbeeldingen die rechtstreeks (hardcoded) in een .html-template staan
    via url_for('static', filename='images/...'), bv. logo's/hero-foto's in
    base.html of jeugd/overzicht.html - deze staan nergens in de databank,
    dus zonder deze scan zou het script ze onterecht als "ongebruikt"
    aanmerken (en met --delete effectief van de live site verwijderen)

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

from models import Page, NieuwsBericht, Team, Sponsor, Product
from scripts._common import get_app
from utils.page_blocks import block_afbeeldingsbestanden

# Bestanden die nooit als 'ongebruikt' beschouwd mogen worden, ook al staan
# ze niet in de databank - rechtstreeks door templates gebruikt.
VASTE_BESTANDEN = {"favicon.ico"}

IMG_SRC_RE = re.compile(r"/static/images/([^\"'\s>]+)")

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
# Vangt filename='images/naam.png' / filename="images/naam.png" - niet de
# dynamische vorm filename='images/' + iets.image_url, want daar volgt de
# sluitende quote meteen na 'images/' (geen tekens ertussen), dus geen match.
TEMPLATE_IMG_RE = re.compile(r"""filename=['"]images/([^'"]+)['"]""")


def _inline_afbeeldingen(html):
    if not html:
        return set()
    return set(IMG_SRC_RE.findall(html))


def _hardcoded_template_afbeeldingen():
    """Afbeeldingen die rechtstreeks in een template-bestand staan i.p.v. via
    de databank - zie de moduledocstring hierboven."""
    gevonden = set()
    for pad in TEMPLATES_DIR.rglob("*.html"):
        gevonden |= set(TEMPLATE_IMG_RE.findall(pad.read_text(encoding="utf-8")))
    return gevonden


def run(effectief_verwijderen):
    app = get_app()
    with app.app_context():
        gebruikt = set(VASTE_BESTANDEN)
        gebruikt |= _hardcoded_template_afbeeldingen()

        for page in Page.query.all():
            if page.hero_image:
                gebruikt.add(page.hero_image)
            gebruikt |= _inline_afbeeldingen(page.body_html)
            for block in page.blocks:
                gebruikt |= set(block_afbeeldingsbestanden(block))

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
