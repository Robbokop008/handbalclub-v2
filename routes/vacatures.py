"""
routes/vacatures.py
--------------------
Vacatures krijgen een prominentere plek op de site (i.p.v. weggemoffeld
als losse link onderaan) - vandaar een eigen route en een link in het
hoofdmenu i.p.v. enkel in de footer. De inhoud wordt sinds de admin-CMS
beheerd via /pagina/<slug> (zie models.Page) - deze route blijft als
permanente 301-redirect bestaan.
"""

from flask import Blueprint, redirect, url_for

vacatures_bp = Blueprint("vacatures", __name__, url_prefix="/vacatures")


@vacatures_bp.route("/")
def index():
    return redirect(url_for("pages.view", slug="vacatures"), code=301)
