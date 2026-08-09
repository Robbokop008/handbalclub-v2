"""
routes/heren.py
----------------
Teampagina's voor de herenploegen worden sinds de admin-CMS beheerd via
/teams/<slug> (zie models.Team, routes/main.py team_detail) - deze routes
blijven als permanente 301-redirect bestaan zodat bestaande links/bookmarks
blijven werken. Heren Regio bestaat niet meer (zie sitemap: "Valt weg").
"""

from flask import Blueprint, redirect, url_for

heren_bp = Blueprint("heren", __name__, url_prefix="/heren")


@heren_bp.route("/heren-1")
def heren_1():
    return redirect(url_for("main.team_detail", slug="heren-1"), code=301)


@heren_bp.route("/heren-2")
def heren_2():
    return redirect(url_for("main.team_detail", slug="heren-2"), code=301)
