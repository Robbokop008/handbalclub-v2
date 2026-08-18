"""
routes/fithandbal.py
---------------------
FIT-Handbal heeft sinds kort een eigen restyled overzichtspagina i.p.v.
de generieke teams/team_detail.html - zelfde aanpak als
routes/ghandbal.py:index(). FIT-Handbal blijft wel een gewoon Team (zie
models.Team, slug "fithandbal") voor de ploegfoto.
"""

from flask import Blueprint, render_template

from models import Team

fithandbal_bp = Blueprint("fithandbal", __name__, url_prefix="/fit-handbal")


@fithandbal_bp.route("/")
def index():
    team = Team.query.filter_by(slug="fithandbal").first()
    return render_template("fithandbal/overzicht.html", team=team)
