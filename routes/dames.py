"""
routes/dames.py
----------------
"Dames 1 & Beloften" en "Dames Regio" staan sinds kort samen op één
overzichtspagina (zie overzicht() hieronder) i.p.v. als 2 aparte
teampagina's onder de "Teams"-dropdown - zelfde aanpak als
routes/club.py:overzicht(). De oude per-team-URL's (ooit beheerd via
/teams/<slug>, zie models.Team, routes/main.py team_detail) blijven
permanent bestaan als 301-redirect zodat bestaande links/bookmarks
blijven werken.
"""

from flask import Blueprint, redirect, render_template, url_for

from models import Team

dames_bp = Blueprint("dames", __name__, url_prefix="/dames")


@dames_bp.route("/")
def overzicht():
    teams = {t.slug: t for t in Team.query.filter(Team.slug.in_(["dames-1-beloften", "dames-regio"])).all()}
    return render_template(
        "dames/overzicht.html",
        team_1_beloften=teams.get("dames-1-beloften"),
        team_regio=teams.get("dames-regio"),
    )


@dames_bp.route("/dames-1-en-beloften")
def dames_1():
    return redirect(url_for("dames.overzicht"), code=301)


@dames_bp.route("/dames-regio")
def dames_regio():
    return redirect(url_for("dames.overzicht"), code=301)
