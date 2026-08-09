"""
routes/dames.py
----------------
Teampagina's voor de damesploegen worden sinds de admin-CMS beheerd via
/teams/<slug> (zie models.Team, routes/main.py team_detail) - deze routes
blijven als permanente 301-redirect bestaan zodat bestaande links/bookmarks
blijven werken.
"""

from flask import Blueprint, redirect, url_for

dames_bp = Blueprint("dames", __name__, url_prefix="/dames")


@dames_bp.route("/dames-1-en-beloften")
def dames_1():
    return redirect(url_for("main.team_detail", slug="dames-1-beloften"), code=301)


@dames_bp.route("/dames-regio")
def dames_regio():
    return redirect(url_for("main.team_detail", slug="dames-regio"), code=301)
