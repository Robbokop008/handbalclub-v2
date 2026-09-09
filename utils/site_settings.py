"""
utils/site_settings.py
------------------------
Site-brede aan/uit-instellingen, momenteel enkel de onderhoudsmodus (zie
models.SiteInstelling en app.py: het before_request-blok dat op basis
hiervan alle publieke routes vervangt door templates/onderhoud.html).

Zelfde "singleton rij, lazy aangemaakt bij eerste gebruik"-aanpak als
utils/site_text.get_site_teksten, maar dan met één rij i.p.v. één rij per
sleutel - er is hier maar één instelling.
"""

from extensions import db
from models import SiteInstelling


def _get_or_create():
    instelling = SiteInstelling.query.first()
    if instelling is None:
        instelling = SiteInstelling(onderhoudsmodus_actief=False)
        db.session.add(instelling)
        db.session.commit()
    return instelling


def is_onderhoudsmodus_actief():
    return _get_or_create().onderhoudsmodus_actief


def zet_onderhoudsmodus(actief):
    instelling = _get_or_create()
    instelling.onderhoudsmodus_actief = actief
    db.session.commit()
