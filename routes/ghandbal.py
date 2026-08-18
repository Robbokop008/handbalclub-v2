"""
routes/ghandbal.py
-------------------
G-Handbal (handbal voor personen met een beperking) heeft een eigen
restyled overzichtspagina - zelfde aanpak als routes/club.py:overzicht().
G-Handbal blijft wel een gewoon Team (zie models.Team, slug "ghandbal")
voor de ploegfoto.
"""

from flask import Blueprint, redirect, render_template, url_for

from models import Team

ghandbal_bp = Blueprint("ghandbal", __name__, url_prefix="/g-handbal")


@ghandbal_bp.route("/")
def index():
    team = Team.query.filter_by(slug="ghandbal").first()
    return render_template("ghandbal/overzicht.html", team=team)


@ghandbal_bp.route("/inschrijving")
def inschrijving():
    return redirect(url_for("jeugd.inschrijving", categorie="G-Handbal"))
