"""
utils/page_blocks.py
----------------------
Kleine helper, gedeeld tussen routes/admin.py (opruimen bij bewerken/
verwijderen van een blok) en scripts/cleanup_unused_images.py (wees-
detectie), die alle afbeeldingsbestanden teruggeeft die een PageBlock
gebruikt - los van hoe dat per block_type in 'data' zit opgeslagen.
"""


def afbeeldingen_uit_data(block_type, data):
    """Geeft een lijst bestandsnamen (in static/images/) terug die in deze
    'data'-dict van een blok van dit type gebruikt worden. Los van een
    concreet PageBlock-object bruikbaar, zodat de admin-routes ook oude vs.
    nieuwe data kunnen vergelijken vóór het effectief opslaan."""
    data = data or {}
    if block_type == "image_gallery":
        return [i["filename"] for i in data.get("images", []) if i.get("filename")]
    if block_type == "columns":
        return [c["image"] for c in data.get("columns", []) if c.get("image")]
    return []


def block_afbeeldingsbestanden(block):
    """Geeft een lijst bestandsnamen (in static/images/) terug die dit
    blok gebruikt."""
    return afbeeldingen_uit_data(block.block_type, block.data)
