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

from datetime import date

from flask import Blueprint, render_template, current_app, redirect, url_for

from models import Evenement

kalender_bp = Blueprint("kalender", __name__, url_prefix="/kalender")


@kalender_bp.route("/")
def overzicht():
    # Zelfde bron als het "Volgende event"-kaartje op de homepage (zie
    # routes/main.py:home) - hier zonder limiet, want dit is de pagina waar
    # de "bekijk onze evenementen"-link naartoe leidt en dus alle
    # aankomende, door een admin ingevoerde evenementen moet tonen, niet
    # enkel de eerstvolgende(n).
    aankomende_evenementen = (
        Evenement.query.filter(Evenement.datum >= date.today())
        .order_by(Evenement.datum.asc()).all()
    )
    return render_template(
        "kalender/overzicht.html",
        aankomende_evenementen=aankomende_evenementen,
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
