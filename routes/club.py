"""
routes/club.py
---------------
Statische informatiepagina's onder het menu "Club". De inhoud wordt sinds
de admin-CMS (zie models.Page) beheerd via /pagina/<slug> - deze routes
blijven permanent bestaan als 301-redirect zodat bestaande links/bookmarks
naar de oude URL's blijven werken.
"""

from flask import Blueprint, redirect, url_for

club_bp = Blueprint("club", __name__, url_prefix="/club")


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
