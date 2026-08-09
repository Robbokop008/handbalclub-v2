"""
routes/kalender.py
-------------------
Wedstrijden (ingebed via een Spond-iframe) blijft code-gedreven. Trainingen
en evenementen worden sinds de admin-CMS beheerd via /pagina/<slug> (zie
models.Page) - hun oude routes blijven als permanente 301-redirect bestaan.

Let op: de exacte Spond embed-URL moet nog aangevuld worden (bv. via
Spond's eigen "embed"/widget-link voor de groep), zie config.py
SPOND_EMBED_URL.
"""

from flask import Blueprint, render_template, current_app, redirect, url_for

kalender_bp = Blueprint("kalender", __name__, url_prefix="/kalender")


@kalender_bp.route("/wedstrijden")
def wedstrijden():
    return render_template("kalender/wedstrijden.html", spond_embed_url=current_app.config["SPOND_EMBED_URL"])


@kalender_bp.route("/trainingen")
def trainingen():
    return redirect(url_for("pages.view", slug="kalender-trainingen"), code=301)


@kalender_bp.route("/evenementen")
def evenementen():
    return redirect(url_for("pages.view", slug="kalender-evenementen"), code=301)
