"""
utils/site_settings.py
------------------------
Site-brede aan/uit-instellingen: de onderhoudsmodus en de webshop (zie
models.SiteInstelling en app.py: de before_request-blokken die op basis
hiervan resp. alle publieke routes vervangen door templates/onderhoud.html,
en de webshop-routes door templates/shop/gesloten.html).

Zelfde "singleton rij, lazy aangemaakt bij eerste gebruik"-aanpak als
utils/site_text.get_site_teksten, maar dan met één rij i.p.v. één rij per
sleutel - er is hier maar één instelling.
"""

from extensions import db
from models import SiteInstelling


def _get_or_create():
    instelling = SiteInstelling.query.first()
    if instelling is None:
        instelling = SiteInstelling(onderhoudsmodus_actief=False, webshop_actief=True)
        db.session.add(instelling)
        db.session.commit()
    return instelling


def is_onderhoudsmodus_actief():
    return _get_or_create().onderhoudsmodus_actief


def zet_onderhoudsmodus(actief):
    instelling = _get_or_create()
    instelling.onderhoudsmodus_actief = actief
    db.session.commit()


def is_webshop_actief():
    return _get_or_create().webshop_actief


def zet_webshop_actief(actief):
    instelling = _get_or_create()
    instelling.webshop_actief = actief
    db.session.commit()


def handleiding_laatst_bijgewerkt():
    return _get_or_create().handleiding_bijgewerkt_op


def zet_handleiding_bijgewerkt_op(dt):
    instelling = _get_or_create()
    instelling.handleiding_bijgewerkt_op = dt
    db.session.commit()


def is_webshop_zichtbaar_voor_huidige_gebruiker():
    """Of de webshop voor de HUIDIGE bezoeker zichtbaar/bereikbaar hoort te
    zijn: gewoon is_webshop_actief(), behalve voor een ingelogde admin - die
    blijft de webshop altijd zien, ook net nadat die dichtgezet is (bv. om
    nog iets na te kijken). Gedeeld door app.py (before_request-gate en
    winkelmandje-icoon) en utils/nav.py (FanShop-navitem), zodat admins
    overal consequent dezelfde uitzondering krijgen."""
    if is_webshop_actief():
        return True

    from flask import session
    user_id = session.get("user_id")
    if user_id is None:
        return False

    from models import User
    user = User.query.get(user_id)
    return user is not None and user.is_admin
