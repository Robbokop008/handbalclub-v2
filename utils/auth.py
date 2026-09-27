"""
utils/auth.py
--------------
Decorators om routes te beschermen: @login_required voor ingelogde
gebruikers, @admin_required voor beheerders. Voorkomt dat elke route
zelf handmatig 'if "user_id" not in session' moet herhalen.
"""

from functools import wraps
from urllib.parse import urlparse
from flask import session, redirect, url_for, g, request
from models import User


def veilige_next_url(url):
    """Geeft url terug als het een relatief pad binnen deze site is, anders
    None. Voorkomt een open redirect: zonder deze check stuurt een link als
    /login?next=https://phishing.example een gebruiker na het inloggen door
    naar een externe site. '//host' en '/\\host' worden door browsers ook als
    externe URL gelezen, dus die worden eveneens geweigerd."""
    if not url or not url.startswith("/") or url.startswith("//") or "\\" in url:
        return None
    if any(ord(teken) < 32 for teken in url):
        return None
    delen = urlparse(url)
    if delen.scheme or delen.netloc:
        return None
    return url


def huidige_pagina_als_next():
    """Pad van de huidige pagina, om na het inloggen naar terug te keren.
    Bij een POST (bv. 'in winkelmandje' terwijl je uitgelogd bent) is dat de
    pagina waarvandaan het formulier verstuurd werd, niet de POST-route zelf."""
    if request.method == "GET":
        return veilige_next_url(request.full_path.rstrip("?"))
    if request.referrer:
        delen = urlparse(request.referrer)
        if delen.netloc == request.host:
            pad = delen.path + (f"?{delen.query}" if delen.query else "")
            return veilige_next_url(pad)
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login", next=huidige_pagina_als_next()))
        g.user = User.query.get(session["user_id"])
        if g.user is None:
            # gebruiker bestaat niet meer -> sessie opruimen
            session.clear()
            return redirect(url_for("auth.login", next=huidige_pagina_als_next()))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user.is_admin:
            return redirect(url_for("main.home"))
        return view(*args, **kwargs)
    return wrapped


# Gebruikersnaam van het enige account dat de adminhandleiding-PDF mag
# vervangen en wijzigingslogboek-items mag toevoegen/verwijderen (zie
# @hoofdadmin_required hieronder) - andere admins mogen enkel bekijken.
HOOFDADMIN_USERNAME = "RobbeBoyen"


def hoofdadmin_required(view):
    """Zoals @admin_required, maar enkel voor HOOFDADMIN_USERNAME. Andere
    admins krijgen een redirect naar het dashboard - zij mogen de
    handleiding/het wijzigingslogboek wel bekijken, niet bewerken."""
    @wraps(view)
    @admin_required
    def wrapped(*args, **kwargs):
        if g.user.username != HOOFDADMIN_USERNAME:
            return redirect(url_for("admin.dashboard"))
        return view(*args, **kwargs)
    return wrapped
