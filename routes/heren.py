"""
routes/heren.py
----------------
"Heren 1" en "Heren 2" staan sinds kort samen op één overzichtspagina
(zie overzicht() hieronder) i.p.v. als 2 aparte teampagina's onder de
"Teams"-dropdown - zelfde aanpak als routes/dames.py:overzicht(). De
oude per-team-URL's (ooit beheerd via /teams/<slug>, zie models.Team,
routes/main.py team_detail) blijven permanent bestaan als 301-redirect
zodat bestaande links/bookmarks blijven werken. Heren Regio bestaat
niet meer (zie sitemap: "Valt weg").
"""

from flask import Blueprint, redirect, render_template, url_for

from models import Team

heren_bp = Blueprint("heren", __name__, url_prefix="/heren")


@heren_bp.route("/")
def overzicht():
    teams = {t.slug: t for t in Team.query.filter(Team.slug.in_(["heren-1", "heren-2"])).all()}
    return render_template(
        "heren/overzicht.html",
        team_1=teams.get("heren-1"),
        team_2=teams.get("heren-2"),
    )


@heren_bp.route("/heren-1")
def heren_1():
    return redirect(url_for("heren.overzicht"), code=301)


@heren_bp.route("/heren-2")
def heren_2():
    return redirect(url_for("heren.overzicht"), code=301)
