"""
routes/kalender.py
-------------------
De "Kalender"-navigatie is één samengevoegde overzichtspagina (zie
overzicht() hieronder) i.p.v. een dropdown naar 3 aparte
bestemmingen - zelfde aanpak als routes/club.py:overzicht(). De oude
URL's blijven permanent bestaan als 301-redirect zodat bestaande
links/bookmarks blijven werken.

Let op: de exacte Spond embed-URL moet nog aangevuld worden (bv. via
Spond's eigen "embed"/widget-link voor de groep), zie config.py
SPOND_EMBED_URL.
"""

from flask import Blueprint, render_template, current_app, redirect, url_for

kalender_bp = Blueprint("kalender", __name__, url_prefix="/kalender")


@kalender_bp.route("/")
def overzicht():
    return render_template(
        "kalender/overzicht.html",
        spond_embed_url=current_app.config["SPOND_EMBED_URL"],
        flanders_trophy_instagram_url=current_app.config["FLANDERS_TROPHY_INSTAGRAM_URL"],
        flanders_trophy_facebook_url=current_app.config["FLANDERS_TROPHY_FACEBOOK_URL"],
    )


@kalender_bp.route("/wedstrijden")
def wedstrijden():
    return redirect(url_for("kalender.overzicht"), code=301)


@kalender_bp.route("/trainingen")
def trainingen():
    return redirect(url_for("kalender.overzicht"), code=301)


@kalender_bp.route("/evenementen")
def evenementen():
    return redirect(url_for("kalender.overzicht"), code=301)
