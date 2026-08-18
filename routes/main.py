"""
routes/main.py
---------------
Routes voor het publieke, informatieve deel van de site: home, nieuws,
over ons en contact. Bewust NIET achter een login, in tegenstelling tot
de webshop-functionaliteit (winkelmandje, afrekenen, profiel) die wel
inloggen vereist.

De vroegere generieke "/teams" en "/teams/<slug>" (het volledige
teamoverzicht en een per-team detailpagina) zijn verwijderd: sinds elk
team een eigen restyled overzichtspagina heeft (Dames/Heren/Jeugd/
G-Handbal/FIT-Handbal), linkte niets meer naar deze generieke pagina's -
zie de projectaudit die dit aan het licht bracht.
"""

from flask import Blueprint, render_template, request, current_app, abort, redirect, url_for

from extensions import db, limiter
from models import NieuwsBericht, VergeetMijVerzoek
from utils.mail import send_contact_mail, send_vergeet_mij_notification

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    laatste_nieuws = (
        NieuwsBericht.query.order_by(NieuwsBericht.position).limit(5).all()
    )
    return render_template(
        "index.html", nieuwsberichten=laatste_nieuws,
        spond_embed_url=current_app.config["SPOND_EMBED_URL"],
        flanders_trophy_website_url=current_app.config["FLANDERS_TROPHY_WEBSITE_URL"],
        flanders_trophy_instagram_url=current_app.config["FLANDERS_TROPHY_INSTAGRAM_URL"],
        flanders_trophy_facebook_url=current_app.config["FLANDERS_TROPHY_FACEBOOK_URL"],
    )


@main_bp.route("/nieuws")
def nieuws():
    alle_berichten = NieuwsBericht.query.order_by(NieuwsBericht.position).all()
    return render_template("nieuws.html", nieuwsberichten=alle_berichten)


@main_bp.route("/nieuws/<int:bericht_id>")
def nieuws_detail(bericht_id):
    bericht = NieuwsBericht.query.get(bericht_id)
    if bericht is None:
        abort(404)
    return render_template("nieuws_detail.html", bericht=bericht)


@main_bp.route("/over-ons")
def about():
    return redirect(url_for("pages.view", slug="over-ons"), code=301)


@main_bp.route("/privacy/vergeet-mij", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def vergeet_mij():
    if request.method == "POST":
        naam = (request.form.get("naam") or "").strip()
        email = (request.form.get("email") or "").strip()
        lidnummer = (request.form.get("lidnummer") or "").strip()
        opmerking = (request.form.get("opmerking") or "").strip()

        if not naam or not email or "@" not in email:
            return render_template(
                "vergeet_mij.html", error="Vul een naam en een geldig e-mailadres in.",
                naam=naam, email=email, lidnummer=lidnummer, opmerking=opmerking,
            )

        verzoek = VergeetMijVerzoek(naam=naam, email=email, lidnummer=lidnummer or None, opmerking=opmerking or None)
        db.session.add(verzoek)
        db.session.commit()

        try:
            send_vergeet_mij_notification(verzoek)
        except Exception as exc:
            current_app.logger.error(f"Kon GDPR-verzoekmail niet versturen: {exc}")

        return render_template("vergeet_mij.html", success=True)

    return render_template("vergeet_mij.html")


@main_bp.route("/contact", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message or "@" not in email:
            return render_template(
                "contact.html", error="Vul alle velden correct in (met een geldig e-mailadres).", name=name, email=email, message=message
            )

        try:
            send_contact_mail(name, email, message)
        except Exception as exc:
            # Mail-fout mag de gebruiker niet blokkeren, maar loggen we wel
            from flask import current_app
            current_app.logger.error(f"Kon contactmail niet versturen: {exc}")

        return render_template("contact.html", success="Je bericht is succesvol verzonden.")

    return render_template("contact.html")
