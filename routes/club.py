"""
routes/club.py
---------------
De "Club"-navigatie is één samengevoegde overzichtspagina (zie overzicht()
hieronder) i.p.v. een dropdown naar 5 aparte pagina's. De oude URL's van
die aparte pagina's (ooit beheerd via de admin-CMS, zie models.Page)
blijven permanent bestaan als 301-redirect zodat bestaande links/
bookmarks blijven werken - ze staan alleen niet meer los in de navbar.
"""

from flask import Blueprint, redirect, render_template, url_for

club_bp = Blueprint("club", __name__, url_prefix="/club")


@club_bp.route("/")
def overzicht():
    return render_template("club/overzicht.html")


@club_bp.route("/missie-en-visie")
def missie_visie():
    return redirect(url_for("pages.view", slug="club-missie-en-visie"), code=301)


@club_bp.route("/bestuur")
def bestuur():
    return redirect(url_for("pages.view", slug="club-bestuur"), code=301)


@club_bp.route("/historiek")
def historiek():
    return redirect(url_for("pages.view", slug="club-historiek"), code=301)


@club_bp.route("/verzekering")
def verzekering():
    return redirect(url_for("pages.view", slug="club-verzekering"), code=301)


@club_bp.route("/aanspreekpunt-integriteit")
def api():
    return redirect(url_for("pages.view", slug="club-aanspreekpunt-integriteit"), code=301)
