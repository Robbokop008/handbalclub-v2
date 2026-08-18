"""
routes/club.py
---------------
De "Club"-navigatie is één samengevoegde overzichtspagina (zie overzicht()
hieronder) i.p.v. een dropdown naar 5 aparte pagina's. De oude URL's van
die aparte pagina's (ooit beheerd via de admin-CMS, zie models.Page)
blijven permanent bestaan als 301-redirect zodat bestaande links/
bookmarks blijven werken - ze wijzen nu rechtstreeks naar de nieuwe
overzichtspagina (dezelfde aanpak als Kalender/Dames/Heren/Jeugd), niet
meer naar de losse Page-rijen: die inhoud staat nu hardcoded op de
overzichtspagina, en de losse Page-rijen zijn opgeruimd (zie
scripts/migrate_site_text_cleanup.py).
"""

from flask import Blueprint, redirect, render_template, url_for

club_bp = Blueprint("club", __name__, url_prefix="/club")


@club_bp.route("/")
def overzicht():
    return render_template("club/overzicht.html")


@club_bp.route("/missie-en-visie")
def missie_visie():
    return redirect(url_for("club.overzicht"), code=301)


@club_bp.route("/bestuur")
def bestuur():
    return redirect(url_for("club.overzicht"), code=301)


@club_bp.route("/historiek")
def historiek():
    return redirect(url_for("club.overzicht"), code=301)


@club_bp.route("/verzekering")
def verzekering():
    return redirect(url_for("club.overzicht"), code=301)


@club_bp.route("/aanspreekpunt-integriteit")
def api():
    return redirect(url_for("club.overzicht"), code=301)
