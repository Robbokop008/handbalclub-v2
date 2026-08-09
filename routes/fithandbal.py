"""
routes/fithandbal.py
---------------------
FIT-Handbal is een team (zie models.Team, slug "fithandbal") en wordt
beheerd via de Teams-sectie van de admin - deze route blijft als
permanente 301-redirect bestaan.
"""

from flask import Blueprint, redirect, url_for

fithandbal_bp = Blueprint("fithandbal", __name__, url_prefix="/fit-handbal")


@fithandbal_bp.route("/")
def index():
    return redirect(url_for("main.team_detail", slug="fithandbal"), code=301)
