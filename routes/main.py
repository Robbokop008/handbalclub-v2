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

from datetime import date

from flask import Blueprint, render_template, request, current_app, abort, redirect, url_for, Response

from extensions import db, limiter
from models import NieuwsBericht, Evenement, VergeetMijVerzoek, Page, Product
from utils.mail import send_contact_mail, send_vergeet_mij_notification
from utils.sanitize import korte_omschrijving

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    laatste_nieuws = (
        NieuwsBericht.query.order_by(NieuwsBericht.position).limit(5).all()
    )
    volgende_evenementen = (
        Evenement.query.filter(Evenement.datum >= date.today())
        .order_by(Evenement.datum.asc()).limit(5).all()
    )
    return render_template(
        "index.html", nieuwsberichten=laatste_nieuws, evenementen=volgende_evenementen,
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
    # Zelfde bron als de kaart-preview op /nieuws (bericht.samenvatting of
    # anders een stuk van de volledige inhoud), enkel afgekapt op meta-
    # description-lengte i.p.v. kaart-lengte.
    meta_description = korte_omschrijving(bericht.samenvatting or bericht.inhoud)
    return render_template("nieuws_detail.html", bericht=bericht, meta_description=meta_description)


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


# URL's die geen enkele SEO-waarde hebben (login/account/winkelmandje/admin/
# GDPR-verzoek) en dus niet gecrawld hoeven te worden - gebruikt door
# robots_txt() hieronder. Bewust een expliciete lijst i.p.v. url_map-
# introspectie: duidelijker te lezen/aan te passen dan impliciete regels.
NIET_TE_CRAWLEN_PADEN = [
    "/admin/",
    "/login", "/register", "/logout", "/profile", "/account_settings",
    "/update_profile", "/delete_account",
    "/cart", "/add_to_cart", "/adjust_cart", "/remove_from_cart", "/clear_cart",
    "/checkout", "/checkout_success", "/webhook",
    "/privacy/vergeet-mij",
]


@main_bp.route("/robots.txt")
def robots_txt():
    regels = ["User-agent: *"]
    regels += [f"Disallow: {pad}" for pad in NIET_TE_CRAWLEN_PADEN]
    regels += ["", f"Sitemap: {url_for('main.sitemap', _external=True)}"]
    return Response("\n".join(regels), mimetype="text/plain")


# Statische, parameterloze pagina's voor de sitemap: (endpoint, prioriteit,
# wijzigingsfrequentie). Admin/auth/winkelmandje-routes staan hier bewust
# niet in - zie NIET_TE_CRAWLEN_PADEN hierboven. Pagina's met een variabele
# in de URL (nieuwsbericht, CMS-pagina, product) worden verderop in
# sitemap() dynamisch uit de database opgebouwd.
STATISCHE_SITEMAP_ENDPOINTS = [
    ("main.home", 1.0, "weekly"),
    ("main.nieuws", 0.7, "daily"),
    ("main.contact", 0.5, "yearly"),
    ("club.overzicht", 0.8, "monthly"),
    ("club.missie_visie", 0.4, "yearly"),
    ("club.bestuur", 0.4, "yearly"),
    ("club.historiek", 0.4, "yearly"),
    ("club.verzekering", 0.4, "yearly"),
    ("club.api", 0.4, "yearly"),
    ("dames.overzicht", 0.8, "weekly"),
    ("dames.dames_1", 0.6, "monthly"),
    ("dames.dames_regio", 0.6, "monthly"),
    ("heren.overzicht", 0.8, "weekly"),
    ("heren.heren_1", 0.6, "monthly"),
    ("heren.heren_2", 0.6, "monthly"),
    ("jeugd.overzicht", 0.8, "weekly"),
    ("jeugd.inschrijving", 0.6, "monthly"),
    ("jeugd.jeugdbeleidsplan", 0.4, "yearly"),
    ("jeugd.ballenbaasjes", 0.6, "monthly"),
    ("jeugd.jm08_jm10", 0.6, "monthly"),
    ("jeugd.jm12", 0.6, "monthly"),
    ("jeugd.j14", 0.6, "monthly"),
    ("jeugd.m14", 0.6, "monthly"),
    ("jeugd.api", 0.4, "yearly"),
    ("jeugd.welzijn", 0.4, "yearly"),
    ("ghandbal.index", 0.7, "monthly"),
    ("ghandbal.inschrijving", 0.6, "monthly"),
    ("fithandbal.index", 0.7, "monthly"),
    ("kalender.overzicht", 0.6, "weekly"),
    ("kalender.wedstrijden", 0.6, "weekly"),
    ("kalender.trainingen", 0.6, "weekly"),
    ("kalender.evenementen", 0.6, "weekly"),
    # vacatures.index is een permanente 301-redirect naar /pagina/vacatures
    # (zie routes/vacatures.py) - die pagina komt al binnen via de Page-query
    # hieronder, een aparte sitemap-entry zou enkel een nutteloze redirect-
    # hop toevoegen.
    ("shop.products", 0.7, "weekly"),
]


@main_bp.route("/sitemap.xml")
def sitemap():
    entries = [
        {"loc": url_for(endpoint, _external=True), "changefreq": freq, "priority": prioriteit}
        for endpoint, prioriteit, freq in STATISCHE_SITEMAP_ENDPOINTS
    ]

    for page in Page.query.filter_by(is_published=True).all():
        entries.append({
            "loc": url_for("pages.view", slug=page.slug, _external=True),
            "lastmod": page.updated_at.date().isoformat() if page.updated_at else None,
            "changefreq": "monthly",
            "priority": 0.5,
        })

    for bericht in NieuwsBericht.query.all():
        entries.append({
            "loc": url_for("main.nieuws_detail", bericht_id=bericht.id, _external=True),
            "lastmod": bericht.gepubliceerd_op.date().isoformat() if bericht.gepubliceerd_op else None,
            "changefreq": "yearly",
            "priority": 0.4,
        })

    for product in Product.query.filter_by(is_active=True).all():
        entries.append({
            "loc": url_for("shop.product_detail", product_id=product.id, _external=True),
            "changefreq": "weekly",
            "priority": 0.5,
        })

    xml = render_template("sitemap.xml", entries=entries)
    return Response(xml, mimetype="application/xml")
