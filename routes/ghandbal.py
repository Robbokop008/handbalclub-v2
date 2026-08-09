"""
routes/ghandbal.py
-------------------
G-Handbal (handbal voor personen met een beperking). Het
inschrijvingsformulier is hetzelfde als bij Jeugd - zie sitemap
("is het zelfde inschrijvingsformulier") - met de categorie 'G-Handbal'
alvast voorgeselecteerd. G-Handbal is een team (zie models.Team, slug
"ghandbal") en wordt beheerd via de Teams-sectie van de admin - deze route
blijft als permanente 301-redirect bestaan.
"""

from flask import Blueprint, redirect, url_for

ghandbal_bp = Blueprint("ghandbal", __name__, url_prefix="/g-handbal")


@ghandbal_bp.route("/")
def index():
    return redirect(url_for("main.team_detail", slug="ghandbal"), code=301)


@ghandbal_bp.route("/inschrijving")
def inschrijving():
    return redirect(url_for("jeugd.inschrijving", categorie="G-Handbal"))
