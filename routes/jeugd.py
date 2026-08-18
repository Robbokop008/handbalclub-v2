"""
routes/jeugd.py
----------------
Jeugdwerking: leeftijdscategorieën, jeugdbeleidsplan, doorlinks naar
externe pagina's (Ballenbaasjes, VHV-welzijnspagina), en het gedeelde
inschrijvingsformulier (ook gebruikt door G-Handbal en FIT-Handbal).
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, request, current_app, url_for

from extensions import db
from models import Inschrijving, School, Team
from utils.mail import send_inschrijving_notification
from utils.inschrijving import get_inschrijving_categorieen, get_hoe_gehoord_opties, get_inschrijving_veld_config

jeugd_bp = Blueprint("jeugd", __name__, url_prefix="/jeugd")

# Nog aan te vullen met de echte, definitieve URL's
BALLENBAASJES_URL = "https://www.ballenbaasjes.be"
VHV_WELZIJN_URL = "https://www.handbal.be"


@jeugd_bp.route("/")
def overzicht():
    teams = {t.slug: t for t in Team.query.filter(Team.slug.in_(["jeugd-jm08-jm10", "jeugd-jm12"])).all()}
    return render_template(
        "jeugd/overzicht.html",
        team_jm08_jm10=teams.get("jeugd-jm08-jm10"),
        team_jm12=teams.get("jeugd-jm12"),
    )


def _parse_datum(waarde):
    try:
        return datetime.strptime(waarde, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@jeugd_bp.route("/inschrijving", methods=["GET", "POST"])
def inschrijving():
    gegevens = {}
    scholen = School.query.order_by(School.naam).all()
    categorieen = get_inschrijving_categorieen()
    hoe_gehoord_opties = get_hoe_gehoord_opties()
    veld_config = get_inschrijving_veld_config()

    if request.method == "POST":
        gegevens = {k: (v or "").strip() for k, v in request.form.items()}
        geboortedatum_ruw = gegevens.get("geboortedatum", "")
        geboortedatum = _parse_datum(geboortedatum_ruw) if geboortedatum_ruw else None
        geboortedatum_verplicht = veld_config["geboortedatum"].verplicht

        verplichte_velden = [
            sleutel for sleutel, config in veld_config.items()
            if config.verplicht and sleutel != "geboortedatum"
        ]
        ontbrekend = [v for v in verplichte_velden if not gegevens.get(v)]

        error = None
        if geboortedatum_verplicht and not geboortedatum_ruw:
            error = "Vul alle verplichte velden correct in (inclusief een geldige geboortedatum)."
        elif geboortedatum_ruw and geboortedatum is None:
            error = "Vul een geldige geboortedatum in."
        elif ontbrekend:
            error = "Vul alle verplichte velden correct in."
        elif gegevens.get("categorie") and gegevens["categorie"] not in categorieen:
            error = "Ongeldige categorie geselecteerd."
        elif gegevens.get("email") and "@" not in gegevens["email"]:
            error = "Vul een geldig e-mailadres in."

        if error:
            return render_template(
                "jeugd/inschrijving.html", categorieen=categorieen,
                hoe_gehoord_opties=hoe_gehoord_opties, scholen=scholen, veld_config=veld_config,
                gegevens=gegevens, error=error,
            )

        nieuwe_inschrijving = Inschrijving(
            categorie=gegevens.get("categorie") or None,
            voornaam_speler=gegevens.get("voornaam_speler") or None,
            achternaam_speler=gegevens.get("achternaam_speler") or None,
            geboortedatum=geboortedatum,
            geboorteplaats=gegevens.get("geboorteplaats") or None,
            straat_nr=gegevens.get("straat_nr") or None,
            postcode=gegevens.get("postcode") or None,
            gemeente=gegevens.get("gemeente") or None,
            email=gegevens.get("email") or None,
            telefoon=gegevens.get("telefoon") or None,
            hoe_gehoord=gegevens.get("hoe_gehoord") or None,
            school=gegevens.get("school") or None,
            opmerkingen=gegevens.get("opmerkingen") or None,
        )
        db.session.add(nieuwe_inschrijving)
        db.session.commit()

        try:
            send_inschrijving_notification(nieuwe_inschrijving)
        except Exception as exc:
            current_app.logger.error(f"Kon inschrijvingsmail niet versturen: {exc}")

        return render_template("jeugd/inschrijving_bedankt.html", inschrijving=nieuwe_inschrijving)

    # Via ?categorie=... kan een link (bv. vanaf FIT-Handbal) de categorie voorselecteren
    voorgeselecteerd = request.args.get("categorie", "")
    return render_template(
        "jeugd/inschrijving.html", categorieen=categorieen,
        hoe_gehoord_opties=hoe_gehoord_opties, scholen=scholen, veld_config=veld_config,
        gegevens={"categorie": voorgeselecteerd}, error=None,
    )


@jeugd_bp.route("/jeugdbeleidsplan")
def jeugdbeleidsplan():
    return redirect(url_for("pages.view", slug="jeugd-jeugdbeleidsplan"), code=301)


@jeugd_bp.route("/ballenbaasjes")
def ballenbaasjes():
    return redirect(BALLENBAASJES_URL)


@jeugd_bp.route("/jm08-jm10")
def jm08_jm10():
    return redirect(url_for("jeugd.overzicht"), code=301)


@jeugd_bp.route("/jm12")
def jm12():
    return redirect(url_for("jeugd.overzicht"), code=301)


@jeugd_bp.route("/j14")
def j14():
    return redirect(url_for("jeugd.overzicht"), code=301)


@jeugd_bp.route("/m14")
def m14():
    return redirect(url_for("jeugd.overzicht"), code=301)


@jeugd_bp.route("/aanspreekpunt-integriteit")
def api():
    return redirect(url_for("pages.view", slug="jeugd-aanspreekpunt-integriteit"), code=301)


@jeugd_bp.route("/welzijn")
def welzijn():
    return redirect(VHV_WELZIJN_URL)
