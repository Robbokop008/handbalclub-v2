"""
routes/admin.py
----------------
Adminpaneel: producten (+ varianten), gebruikers en bestellingen beheren.

Belangrijk principe: producten en varianten worden nooit verwijderd, enkel
actief/inactief gezet. Bestaande orderregels verwijzen naar hun product_id/
variant_id (voor historiek: kleur, maat, prijs op moment van bestellen) en
zouden anders naar niets meer verwijzen.
"""

import re
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, render_template, request, redirect, url_for, current_app, g, jsonify, abort
from werkzeug.utils import secure_filename

from werkzeug.routing import BuildError

from datetime import datetime, timedelta

from extensions import db
from models import (
    Product, ProductVariant, User, Order, ORDER_STATUSES, Inschrijving, VergeetMijVerzoek,
    Page, PageBlock, PAGE_BLOCK_TYPES, NavItem, NAV_ITEM_TYPES, NieuwsBericht, NIEUWS_CATEGORIEEN, Evenement, Sponsor, Team,
    TEAM_SECTIES, TEAM_SECTIE_LABELS, School, SiteText,
    InschrijvingCategorie, HoeGehoordOptie, InschrijvingVeldConfig, INSCHRIJVING_VELD_DEFINITIES,
)
from utils.auth import admin_required
from utils.mail import send_admin_cancellation_mail
from utils.sanitize import sanitize_html
from utils.site_text import SITE_TEXT_PAGINAS, vind_pagina, get_site_teksten
from utils.nav import _resolve_url as _resolve_nav_item_url
from utils.inschrijving import get_inschrijving_categorieen, get_hoe_gehoord_opties, get_inschrijving_veld_config
from utils.page_blocks import block_afbeeldingsbestanden, afbeeldingen_uit_data
from utils.url_validation import is_safe_target_url, parse_video_embed

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _save_uploaded_image(image_file):
    """Slaat een geüploade afbeelding op met een unieke bestandsnaam en geeft die naam terug
    (of None als er geen bestand is meegestuurd, of het geen toegelaten afbeeldingstype is)."""
    if not image_file or not image_file.filename:
        return None

    ext = Path(secure_filename(image_file.filename)).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4()}{ext}"
    image_file.save(upload_folder / filename)
    return filename


def _delete_uploaded_image(filename):
    """Verwijdert een eerder geüploade afbeelding van schijf. Genegeerd als
    filename leeg is of het bestand al niet (meer) bestaat - dit wordt
    aangeroepen telkens een afbeelding vervangen of een record met een
    afbeelding verwijderd wordt, zodat static/images/ niet blijft
    aangroeien met bestanden die nergens meer naar verwijzen."""
    if not filename:
        return
    path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    try:
        path.unlink(missing_ok=True)
    except OSError:
        current_app.logger.warning(f"Kon geüploade afbeelding niet verwijderen: {filename}")


def _slugify(text):
    """Zet vrije tekst om in een URL-vriendelijke slug (kleine letters, koppeltekens)."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _parse_optioneel_positief_getal(value):
    """Parseert een optioneel getalveld (bv. aantal bekers): lege invoer -> None
    (toont "X" op de site, zie templates/_team_macros.html), geeft (waarde, fout) terug."""
    value = (value or "").strip()
    if not value:
        return None, None
    try:
        getal = int(value)
    except ValueError:
        return None, "Vul een geheel getal in (of laat leeg)."
    if getal < 0:
        return None, "Vul een getal van 0 of hoger in."
    return getal, None


def _parse_datetime_local(value):
    """Parseert de waarde van een <input type="datetime-local"> (bv. '2026-08-08T14:30'),
    geeft None terug als de waarde leeg of ongeldig is."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


def _parse_date(value):
    """Parseert de waarde van een <input type="date"> (bv. '2026-10-12'),
    geeft None terug als de waarde leeg of ongeldig is."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _html_is_blank(html):
    """True als deze rich-text HTML geen zichtbare tekst of afbeelding bevat
    (Quill stuurt een lege editor als '<p><br></p>', niet als lege string)."""
    text = re.sub(r"<[^>]+>", "", html or "").strip()
    return not text and "<img" not in (html or "")


PAGE_BLOCK_TYPE_LABELS = {
    "rich_text": "Tekstblok",
    "image_gallery": "Afbeelding(en)",
    "columns": "Kolommen",
    "video": "Video",
    "button": "Knop",
    "quote": "Citaat",
    "faq": "Veelgestelde vragen",
    "stats": "Statistieken",
    "embed_html": "HTML/embed",
}


def _next_block_position(page_id):
    max_position = db.session.query(db.func.max(PageBlock.position)).filter_by(page_id=page_id).scalar() or 0
    return max_position + 1


def _parse_weergave_fields():
    """Leest de gedeelde 'Weergave'-velden (uitlijning/achtergrond/breedte/
    witruimte) die op élk blokformulier staan - zie utils.page_blocks.
    STYLE_DEFAULTS voor de toegelaten waarden. Heet bewust 'weergave' i.p.v.
    'style' als data-sleutel, want het knop-blok gebruikt 'style' al voor
    zijn eigen kleur (primary/secondary)."""
    align = request.form.get("weergave_align")
    background = request.form.get("weergave_background")
    width = request.form.get("weergave_width")
    spacing = request.form.get("weergave_spacing")
    return {
        "align": align if align in ("left", "center", "right") else "left",
        "background": background if background in ("none", "licht", "blauw", "donker") else "none",
        "width": width if width in ("smal", "normaal", "breed") else "normaal",
        "spacing": spacing if spacing in ("compact", "normaal", "ruim") else "normaal",
    }


def _parse_block_form(block_type, existing_data):
    """Leest request.form/request.files uit voor het gegeven bloktype en
    geeft (data, error) terug. existing_data is de huidige block.data bij
    bewerken (leeg dict bij toevoegen) - nodig om bestaande afbeeldingen/
    kolommen te kunnen behouden, vervangen of verwijderen. Ruimt zelf oude
    afbeeldingsbestanden op die vervangen/verwijderd worden (zelfde patroon
    als _delete_uploaded_image elders in dit bestand). Voegt de gedeelde
    'weergave'-stijlvelden toe aan het resultaat, ongeacht bloktype."""
    existing_data = existing_data or {}
    data = {}
    error = None

    if block_type == "rich_text":
        html = sanitize_html(request.form.get("html") or "")
        data = {"html": html}

    elif block_type == "image_gallery":
        images = []
        bestaande = existing_data.get("images", [])
        for i, img in enumerate(bestaande):
            if request.form.get(f"remove_image_{i}"):
                _delete_uploaded_image(img.get("filename"))
                continue
            alt = (request.form.get(f"alt_{i}") or "").strip()
            images.append({"filename": img.get("filename"), "alt": alt})
        for bestand in request.files.getlist("new_images"):
            filename = _save_uploaded_image(bestand)
            if filename:
                images.append({"filename": filename, "alt": ""})
        data = {"images": images}

    elif block_type == "columns":
        try:
            aantal = int(request.form.get("column_count") or 2)
        except ValueError:
            aantal = 2
        aantal = min(max(aantal, 2), 4)

        bestaande = existing_data.get("columns", [])
        columns = []
        for i in range(aantal):
            heading = (request.form.get(f"heading_{i}") or "").strip()
            text = (request.form.get(f"text_{i}") or "").strip()
            oude_afbeelding = bestaande[i].get("image") if i < len(bestaande) else None
            nieuwe_afbeelding = _save_uploaded_image(request.files.get(f"image_{i}"))
            if nieuwe_afbeelding:
                _delete_uploaded_image(oude_afbeelding)
                afbeelding = nieuwe_afbeelding
            elif request.form.get(f"remove_image_{i}"):
                _delete_uploaded_image(oude_afbeelding)
                afbeelding = None
            else:
                afbeelding = oude_afbeelding
            columns.append({"heading": heading, "text": text, "image": afbeelding})

        # Bij het verkleinen van het aantal kolommen: afbeeldingen van de
        # kolommen die wegvallen niet laten rondslingeren op schijf.
        for oude_kolom in bestaande[aantal:]:
            _delete_uploaded_image(oude_kolom.get("image"))

        data = {"columns": columns}

    elif block_type == "video":
        url = (request.form.get("url") or "").strip()
        embed = parse_video_embed(url)
        if embed is None:
            data, error = {"url": url}, "Geen geldige YouTube- of Vimeo-URL herkend."
        else:
            provider, embed_id = embed
            data = {"provider": provider, "embed_id": embed_id, "source_url": url}

    elif block_type == "button":
        label = (request.form.get("label") or "").strip()
        url = (request.form.get("url") or "").strip()
        stijl = request.form.get("style") if request.form.get("style") in ("primary", "secondary") else "primary"
        data = {"label": label, "url": url, "style": stijl}
        if not label:
            error = "Tekst voor de knop is verplicht."
        elif not is_safe_target_url(url):
            error = "Ongeldige URL. Gebruik een pad dat begint met '/', of een volledige http(s)-URL."

    elif block_type == "quote":
        text = (request.form.get("text") or "").strip()
        auteur = (request.form.get("auteur") or "").strip()
        data = {"text": text, "auteur": auteur}

    elif block_type == "faq":
        try:
            aantal = int(request.form.get("item_count") or 3)
        except ValueError:
            aantal = 3
        aantal = min(max(aantal, 1), 6)
        items = []
        for i in range(aantal):
            vraag = (request.form.get(f"vraag_{i}") or "").strip()
            antwoord = (request.form.get(f"antwoord_{i}") or "").strip()
            if vraag or antwoord:
                items.append({"vraag": vraag, "antwoord": antwoord})
        data = {"items": items}

    elif block_type == "stats":
        try:
            aantal = int(request.form.get("item_count") or 3)
        except ValueError:
            aantal = 3
        aantal = min(max(aantal, 1), 4)
        items = []
        for i in range(aantal):
            getal = (request.form.get(f"getal_{i}") or "").strip()
            label = (request.form.get(f"stat_label_{i}") or "").strip()
            if getal or label:
                items.append({"getal": getal, "label": label})
        data = {"items": items}

    elif block_type == "embed_html":
        html = sanitize_html(request.form.get("html") or "")
        data = {"html": html}

    else:
        return {}, "Onbekend bloktype."

    data["weergave"] = _parse_weergave_fields()
    return data, error


def _dashboard_acties():
    """Telt de dingen die mogelijk actie van de admin vragen - elk met een
    link naar de plek waar je dat oplost."""
    zeven_dagen_geleden = datetime.utcnow() - timedelta(days=7)
    return [
        {
            "label": "Onverwerkte GDPR-verzoeken",
            "aantal": VergeetMijVerzoek.query.filter_by(verwerkt=False).count(),
            "url": url_for("admin.gdpr_verzoeken"),
        },
        {
            "label": "Nieuwe inschrijvingen (laatste 7 dagen)",
            "aantal": Inschrijving.query.filter(Inschrijving.aangemaakt_op >= zeven_dagen_geleden).count(),
            "url": url_for("admin.inschrijvingen"),
        },
        {
            "label": "Bestellingen die actie nodig hebben",
            "aantal": Order.query.filter(Order.order_status.notin_(["Verzonden", "Geannuleerd", "Terugbetaald"])).count(),
            "url": url_for("admin.orders"),
        },
        {
            "label": "Ongepubliceerde pagina's",
            "aantal": Page.query.filter_by(is_published=False).count(),
            "url": url_for("admin.pages"),
        },
    ]


def _dashboard_waarschuwingen():
    """Verzamelt korte, doorklikbare signalen dat iets aandacht nodig heeft
    (geen harde fouten - de site blijft gewoon werken, maar iets staat er
    onvolledig of kapot bij)."""
    waarschuwingen = []

    for team in Team.query.order_by(Team.sectie, Team.naam).all():
        ontbreekt = []
        if not team.foto_url:
            ontbreekt.append("foto")
        if not team.omschrijving or team.omschrijving.startswith("[Placeholder]"):
            ontbreekt.append("omschrijving")
        if ontbreekt:
            waarschuwingen.append({
                "tekst": f"Team '{team.naam}' heeft geen {' en '.join(ontbreekt)}",
                "url": url_for("admin.edit_team", team_id=team.id),
            })

    for product in Product.query.filter_by(is_active=True).order_by(Product.product_name).all():
        heeft_voorraad = any(v.is_active and v.stock > 0 for v in product.variants)
        if not heeft_voorraad:
            waarschuwingen.append({
                "tekst": f"Product '{product.product_name}' is actief maar heeft geen koopbare variant (voorraad)",
                "url": url_for("admin.edit_product", product_id=product.product_id),
            })

    for item in NavItem.query.order_by(NavItem.position).all():
        if item.item_type in ("category", "divider"):
            continue
        if _resolve_nav_item_url(item) is None:
            waarschuwingen.append({
                "tekst": f"Navigatie-item '{item.label}' verwijst naar iets dat niet meer bestaat",
                "url": url_for("admin.navigation") + f"#nav-item-{item.id}",
            })

    return waarschuwingen


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template(
        "admin.html", user=g.user,
        acties=_dashboard_acties(), waarschuwingen=_dashboard_waarschuwingen(),
    )


@admin_bp.route("/products")
@admin_required
def products():
    all_products = Product.query.all()
    return render_template("admin_products.html", user=g.user, products=all_products)


@admin_bp.route("/products/add", methods=["POST"])
@admin_required
def add_product():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    image_filename = _save_uploaded_image(request.files.get("image"))

    product = Product(
        product_name=name,
        description=description,
        image_url=image_filename,
        printing_available=bool(request.form.get("printing_available")),
        is_active=bool(request.form.get("is_active")),
    )
    db.session.add(product)
    db.session.commit()

    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return redirect(url_for("admin.products"))

    if request.method == "GET":
        variants = ProductVariant.query.filter_by(product_id=product_id).all()
        return render_template("edit_product.html", user=g.user, product=product, variants=variants)

    product.product_name = (request.form.get("name") or "").strip()
    product.description = (request.form.get("description") or "").strip()
    product.printing_available = bool(request.form.get("printing_available"))
    product.is_active = bool(request.form.get("is_active"))

    new_image = _save_uploaded_image(request.files.get("image"))
    if new_image:
        _delete_uploaded_image(product.image_url)
        product.image_url = new_image

    db.session.commit()
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/toggle_active", methods=["POST"])
@admin_required
def toggle_product_active(product_id):
    product = Product.query.get(product_id)
    if product is not None:
        product.is_active = not product.is_active
        db.session.commit()
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/variants/add", methods=["POST"])
@admin_required
def add_variant(product_id):
    variant = ProductVariant(
        product_id=product_id,
        color=(request.form.get("color") or "").strip(),
        size=(request.form.get("size") or "").strip(),
        price=float(request.form.get("price")),
        stock=int(request.form.get("stock")),
        is_active=bool(request.form.get("is_active")),
    )
    db.session.add(variant)
    db.session.commit()

    return redirect(url_for("admin.edit_product", product_id=product_id))


@admin_bp.route("/variants/<int:variant_id>/edit", methods=["POST"])
@admin_required
def edit_variant(variant_id):
    variant = ProductVariant.query.get(variant_id)
    if variant is None:
        return redirect(url_for("admin.products"))

    variant.color = (request.form.get("color") or "").strip()
    variant.size = (request.form.get("size") or "").strip()
    variant.price = float(request.form.get("price"))
    variant.stock = int(request.form.get("stock"))
    variant.is_active = bool(request.form.get("is_active"))
    db.session.commit()

    return redirect(url_for("admin.edit_product", product_id=variant.product_id))


@admin_bp.route("/variants/<int:variant_id>/toggle_active", methods=["POST"])
@admin_required
def toggle_variant_active(variant_id):
    variant = ProductVariant.query.get(variant_id)
    if variant is None:
        return redirect(url_for("admin.products"))

    variant.is_active = not variant.is_active
    db.session.commit()
    return redirect(url_for("admin.edit_product", product_id=variant.product_id))


@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.all()
    return render_template("admin_users.html", user=g.user, users=all_users)


@admin_bp.route("/orders")
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin_orders.html", user=g.user, orders=all_orders)


@admin_bp.route("/orders/<int:order_id>")
@admin_required
def view_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return redirect(url_for("admin.orders"))
    return render_template("view_order.html", user=g.user, order=order, order_statuses=ORDER_STATUSES)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return redirect(url_for("admin.orders"))

    status = (request.form.get("order_status") or "").strip()
    if status not in ORDER_STATUSES:
        return redirect(url_for("admin.view_order", order_id=order_id))

    was_cancelled_now = status == "Geannuleerd" and order.order_status != "Geannuleerd"
    order.order_status = status

    if was_cancelled_now:
        # Voorraad terugboeken voor elke regel in de geannuleerde bestelling
        for line in order.lines:
            if line.variant:
                line.variant.stock += line.quantity

    db.session.commit()

    if was_cancelled_now:
        try:
            send_admin_cancellation_mail(order)
        except Exception:
            current_app.logger.exception(f"Annulatiemail versturen voor order {order_id} is mislukt")

    return redirect(url_for("admin.view_order", order_id=order_id))


@admin_bp.route("/inschrijvingen")
@admin_required
def inschrijvingen():
    alle = Inschrijving.query.order_by(Inschrijving.aangemaakt_op.desc()).all()
    return render_template("admin_inschrijvingen.html", user=g.user, inschrijvingen=alle)


@admin_bp.route("/scholen")
@admin_required
def scholen():
    # Verhuisd naar het Inschrijvingsformulier-tabblad; deze URL blijft
    # werken als doorverwijzing voor wie de oude link nog had staan.
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/scholen/add", methods=["POST"])
@admin_required
def add_school():
    naam = (request.form.get("naam") or "").strip()

    if not naam:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error="Naam is verplicht."))
    if School.query.filter_by(naam=naam).first() is not None:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error=f"'{naam}' staat al in de lijst."))

    db.session.add(School(naam=naam))
    db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/scholen/<int:school_id>/delete", methods=["POST"])
@admin_required
def delete_school(school_id):
    school = School.query.get(school_id)
    if school is not None:
        db.session.delete(school)
        db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


def _inschrijvingsformulier_context(error=None):
    veld_config = get_inschrijving_veld_config()
    velden = [(sleutel, veld_config[sleutel]) for sleutel, _label, _verplicht in INSCHRIJVING_VELD_DEFINITIES]
    return dict(
        user=g.user, velden=velden,
        categorieen=InschrijvingCategorie.query.order_by(InschrijvingCategorie.id).all(),
        hoe_gehoord_opties=HoeGehoordOptie.query.order_by(HoeGehoordOptie.id).all(),
        scholen=School.query.order_by(School.naam).all(),
        error=error,
    )


@admin_bp.route("/inschrijvingsformulier")
@admin_required
def inschrijvingsformulier():
    get_inschrijving_categorieen()  # zorgt dat de lijst geseed is
    get_hoe_gehoord_opties()
    return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context())


@admin_bp.route("/inschrijvingsformulier/velden", methods=["POST"])
@admin_required
def save_inschrijving_velden():
    veld_config = get_inschrijving_veld_config()
    for sleutel, _label, _verplicht in INSCHRIJVING_VELD_DEFINITIES:
        nieuw_label = (request.form.get(f"label_{sleutel}") or "").strip()
        if nieuw_label:
            veld_config[sleutel].label = nieuw_label
        veld_config[sleutel].verplicht = bool(request.form.get(f"verplicht_{sleutel}"))
    db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/inschrijvingsformulier/categorieen/add", methods=["POST"])
@admin_required
def add_inschrijving_categorie():
    naam = (request.form.get("naam") or "").strip()
    if not naam:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error="Naam is verplicht."))
    if InschrijvingCategorie.query.filter_by(naam=naam).first() is not None:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error=f"'{naam}' staat al in de lijst."))
    db.session.add(InschrijvingCategorie(naam=naam))
    db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/inschrijvingsformulier/categorieen/<int:categorie_id>/delete", methods=["POST"])
@admin_required
def delete_inschrijving_categorie(categorie_id):
    categorie = InschrijvingCategorie.query.get(categorie_id)
    if categorie is not None:
        db.session.delete(categorie)
        db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/inschrijvingsformulier/hoe-gehoord/add", methods=["POST"])
@admin_required
def add_hoe_gehoord_optie():
    naam = (request.form.get("naam") or "").strip()
    if not naam:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error="Naam is verplicht."))
    if HoeGehoordOptie.query.filter_by(naam=naam).first() is not None:
        return render_template("admin/inschrijvingsformulier.html", **_inschrijvingsformulier_context(error=f"'{naam}' staat al in de lijst."))
    db.session.add(HoeGehoordOptie(naam=naam))
    db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/inschrijvingsformulier/hoe-gehoord/<int:optie_id>/delete", methods=["POST"])
@admin_required
def delete_hoe_gehoord_optie(optie_id):
    optie = HoeGehoordOptie.query.get(optie_id)
    if optie is not None:
        db.session.delete(optie)
        db.session.commit()
    return redirect(url_for("admin.inschrijvingsformulier"))


@admin_bp.route("/site-teksten/<slug>", methods=["GET", "POST"])
@admin_required
def edit_site_tekst(slug):
    pagina = vind_pagina(slug)
    if pagina is None:
        abort(404)

    if request.method == "POST":
        bestaande = {r.sleutel: r for r in SiteText.query.all()}
        for sleutel, omschrijving, standaard_waarde, veld_type in pagina["velden"]:
            ruwe_waarde = (request.form.get(sleutel) or "").strip()
            if veld_type == "html":
                ruwe_waarde = sanitize_html(ruwe_waarde)
            nieuwe_waarde = ruwe_waarde or standaard_waarde
            if sleutel in bestaande:
                bestaande[sleutel].waarde = nieuwe_waarde
            else:
                db.session.add(SiteText(sleutel=sleutel, omschrijving=omschrijving, waarde=nieuwe_waarde))
        db.session.commit()
        return redirect(url_for("admin.pages"))

    waarden = get_site_teksten()
    velden = [
        (sleutel, omschrijving, waarden[sleutel], veld_type)
        for sleutel, omschrijving, _standaard_waarde, veld_type in pagina["velden"]
    ]
    bekijk_url = None
    if pagina["endpoint"]:
        try:
            bekijk_url = url_for(pagina["endpoint"])
        except BuildError:
            bekijk_url = None

    return render_template("admin/site_tekst_form.html", user=g.user, pagina=pagina, velden=velden, bekijk_url=bekijk_url)


@admin_bp.route("/gdpr-verzoeken")
@admin_required
def gdpr_verzoeken():
    alle = VergeetMijVerzoek.query.order_by(VergeetMijVerzoek.aangemaakt_op.desc()).all()
    return render_template("admin_gdpr.html", user=g.user, verzoeken=alle)


@admin_bp.route("/gdpr-verzoeken/<int:verzoek_id>/verwerkt", methods=["POST"])
@admin_required
def toggle_gdpr_verwerkt(verzoek_id):
    verzoek = VergeetMijVerzoek.query.get(verzoek_id)
    if verzoek is not None:
        verzoek.verwerkt = not verzoek.verwerkt
        db.session.commit()
    return redirect(url_for("admin.gdpr_verzoeken"))


def _vaste_pagina_rijen():
    """Bouwt de rijen voor de 'vaste' (code-gedreven) pagina's uit
    SITE_TEXT_PAGINAS, met een 'Bekijk pagina'-URL waar mogelijk - zie
    utils/site_text.py."""
    rijen = []
    for pagina in SITE_TEXT_PAGINAS:
        bekijk_url = None
        if pagina["endpoint"]:
            try:
                bekijk_url = url_for(pagina["endpoint"])
            except BuildError:
                bekijk_url = None
        rijen.append({"kind": "vast", "title": pagina["label"], "pagina": pagina, "bekijk_url": bekijk_url})
    return rijen


@admin_bp.route("/pages")
@admin_required
def pages():
    content_rijen = [{"kind": "content", "title": p.title, "page": p} for p in Page.query.all()]
    alle_rijen = sorted(content_rijen + _vaste_pagina_rijen(), key=lambda r: r["title"].lower())
    return render_template("admin/pages_list.html", user=g.user, rijen=alle_rijen)


@admin_bp.route("/pages/<int:page_id>/preview")
@admin_required
def preview_page(page_id):
    """Toont de pagina precies zoals bezoekers ze zouden zien, ongeacht
    is_published - voor de live-preview-iframe in het bewerkscherm. In
    tegenstelling tot pages.view (de publieke route) is dit enkel voor
    ingelogde admins bereikbaar."""
    page = Page.query.get(page_id)
    if page is None:
        abort(404)
    return render_template("pages/view.html", page=page)


@admin_bp.route("/pages/upload-image", methods=["POST"])
@admin_required
def upload_page_image():
    """Afbeelding-upload voor de rich-text editor: slaat het bestand op en
    geeft de URL terug zodat de editor die inline kan invoegen (in plaats
    van de afbeelding als base64 in de opgeslagen HTML te embedden)."""
    filename = _save_uploaded_image(request.files.get("image"))
    if filename is None:
        return jsonify({"error": "Geen geldige afbeelding ontvangen."}), 400
    return jsonify({"url": url_for("static", filename=f"images/{filename}")})


@admin_bp.route("/pages/add", methods=["GET", "POST"])
@admin_required
def add_page():
    if request.method == "GET":
        return render_template("admin/page_form.html", user=g.user)

    title = (request.form.get("title") or "").strip()
    slug = _slugify(request.form.get("slug") or title)
    is_published = bool(request.form.get("is_published"))
    meta_description = (request.form.get("meta_description") or "").strip() or None
    hero_image = _save_uploaded_image(request.files.get("hero_image"))

    error = None
    if not title:
        error = "Titel is verplicht."
    elif not slug:
        error = "Slug is verplicht."
    elif Page.query.filter_by(slug=slug).first() is not None:
        error = f"Er bestaat al een pagina met slug '{slug}'. Kies een andere titel of slug."

    if error:
        # hero_image werd hierboven al opgeslagen (indien meegestuurd) vóór
        # deze validatie - zonder opruimen zou dat bestand nergens meer naar
        # verwijzen als de pagina nu niet aangemaakt wordt.
        _delete_uploaded_image(hero_image)
        return render_template(
            "admin/page_form.html", user=g.user, error=error,
            form_title=title, form_slug=slug, form_is_published=is_published,
            form_meta_description=meta_description,
        )

    page = Page(
        title=title, slug=slug, hero_image=hero_image, is_published=is_published,
        meta_description=meta_description,
    )
    db.session.add(page)
    db.session.commit()
    # Meteen doorrollen naar het bewerkscherm: een pagina zonder inhoud
    # heeft weinig nut, en dit is waar die inhoud voortaan opgebouwd wordt.
    return redirect(url_for("admin.edit_page", page_id=page.id))


def _render_page_edit(page, **kwargs):
    return render_template(
        "admin/page_canvas.html", user=g.user, page=page,
        block_types=PAGE_BLOCK_TYPES, block_type_labels=PAGE_BLOCK_TYPE_LABELS,
        **kwargs,
    )


@admin_bp.route("/pages/<int:page_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_page(page_id):
    page = Page.query.get(page_id)
    if page is None:
        return redirect(url_for("admin.pages"))

    if request.method == "GET":
        return _render_page_edit(page)

    title = (request.form.get("title") or "").strip()
    slug = _slugify(request.form.get("slug") or title)
    is_published = bool(request.form.get("is_published"))
    meta_description = (request.form.get("meta_description") or "").strip() or None

    error = None
    if not title:
        error = "Titel is verplicht."
    elif not slug:
        error = "Slug is verplicht."
    elif Page.query.filter(Page.slug == slug, Page.id != page.id).first() is not None:
        error = f"Er bestaat al een andere pagina met slug '{slug}'. Kies een andere titel of slug."

    if error:
        return _render_page_edit(
            page, error=error, form_title=title, form_slug=slug, form_is_published=is_published,
            form_meta_description=meta_description,
        )

    page.title = title
    page.slug = slug
    page.is_published = is_published
    page.meta_description = meta_description

    new_image = _save_uploaded_image(request.files.get("hero_image"))
    if new_image:
        _delete_uploaded_image(page.hero_image)
        page.hero_image = new_image

    db.session.commit()
    return redirect(url_for("admin.edit_page", page_id=page.id))


@admin_bp.route("/pages/<int:page_id>/toggle_published", methods=["POST"])
@admin_required
def toggle_page_published(page_id):
    page = Page.query.get(page_id)
    if page is not None:
        page.is_published = not page.is_published
        db.session.commit()
    return redirect(url_for("admin.pages"))


@admin_bp.route("/pages/<int:page_id>/delete", methods=["POST"])
@admin_required
def delete_page(page_id):
    page = Page.query.get(page_id)
    if page is None:
        return redirect(url_for("admin.pages"))

    linking_items = NavItem.query.filter_by(page_id=page_id).all()
    if linking_items:
        labels = ", ".join(f"'{i.label}'" for i in linking_items)
        error = (
            f"Deze pagina kan niet verwijderd worden: de navigatie verwijst er nog naar "
            f"via {labels}. Verwijder of wijzig eerst dat navigatie-item op de "
            f"Navigatie-pagina, dan kan de pagina hierna wel verwijderd worden."
        )
        content_rijen = [{"kind": "content", "title": p.title, "page": p} for p in Page.query.all()]
        alle_rijen = sorted(content_rijen + _vaste_pagina_rijen(), key=lambda r: r["title"].lower())
        return render_template("admin/pages_list.html", user=g.user, rijen=alle_rijen, error=error)

    for block in page.blocks:
        for filename in block_afbeeldingsbestanden(block):
            _delete_uploaded_image(filename)
    _delete_uploaded_image(page.hero_image)
    db.session.delete(page)   # cascadeert naar PageBlock-rijen (Page.blocks-relationship)
    db.session.commit()
    return redirect(url_for("admin.pages"))


@admin_bp.route("/pages/<int:page_id>/blocks/add/<block_type>", methods=["GET", "POST"])
@admin_required
def add_page_block(page_id, block_type):
    page = Page.query.get(page_id)
    if page is None or block_type not in PAGE_BLOCK_TYPES:
        abort(404)

    if request.method == "GET":
        return render_template(
            "admin/page_block_form.html", user=g.user, page=page, block=None,
            block_type=block_type, block_type_label=PAGE_BLOCK_TYPE_LABELS[block_type],
        )

    data, error = _parse_block_form(block_type, {})
    if error:
        return render_template(
            "admin/page_block_form.html", user=g.user, page=page, block=None,
            block_type=block_type, block_type_label=PAGE_BLOCK_TYPE_LABELS[block_type],
            error=error, form_data=data,
        )

    blok = PageBlock(page_id=page.id, block_type=block_type, position=_next_block_position(page.id), data=data)
    db.session.add(blok)
    db.session.commit()
    return redirect(url_for("admin.edit_page", page_id=page.id))


@admin_bp.route("/pages/<int:page_id>/blocks/<int:block_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_page_block(page_id, block_id):
    page = Page.query.get(page_id)
    block = PageBlock.query.get(block_id)
    if page is None or block is None or block.page_id != page.id:
        abort(404)

    if request.method == "GET":
        return render_template(
            "admin/page_block_form.html", user=g.user, page=page, block=block,
            block_type=block.block_type, block_type_label=PAGE_BLOCK_TYPE_LABELS[block.block_type],
        )

    data, error = _parse_block_form(block.block_type, block.data)
    if error:
        return render_template(
            "admin/page_block_form.html", user=g.user, page=page, block=block,
            block_type=block.block_type, block_type_label=PAGE_BLOCK_TYPE_LABELS[block.block_type],
            error=error, form_data=data,
        )

    block.data = data
    db.session.commit()
    return redirect(url_for("admin.edit_page", page_id=page.id))


@admin_bp.route("/pages/<int:page_id>/blocks/<int:block_id>/delete", methods=["POST"])
@admin_required
def delete_page_block(page_id, block_id):
    block = PageBlock.query.get(block_id)
    if block is not None and block.page_id == page_id:
        for filename in block_afbeeldingsbestanden(block):
            _delete_uploaded_image(filename)
        db.session.delete(block)
        db.session.commit()
    return redirect(url_for("admin.edit_page", page_id=page_id))


@admin_bp.route("/pages/<int:page_id>/blocks/reorder", methods=["POST"])
@admin_required
def reorder_page_blocks(page_id):
    """AJAX-endpoint voor het slepen (SortableJS) in de blokken-builder,
    zelfde patroon als reorder_nav_items() maar dan voor een platte lijst
    blokken die bij één specifieke pagina horen."""
    data = request.get_json(silent=True) or {}
    updates = data.get("items") or []

    for update in updates:
        block = PageBlock.query.get(update.get("id"))
        if block is None or block.page_id != page_id:
            continue
        block.position = update.get("position", block.position)

    db.session.commit()
    return jsonify({"ok": True})


def _collect_descendant_ids(item_id):
    """Verzamelt recursief alle id's van kinderen (en kleinkinderen, ...) van een navitem."""
    ids = []
    for child in NavItem.query.filter_by(parent_id=item_id).all():
        ids.append(child.id)
        ids.extend(_collect_descendant_ids(child.id))
    return ids


def _validate_nav_target(item_type, page_id, team_id, route_endpoint, external_url):
    """Geeft een foutmelding terug als het gekozen doel voor dit type ongeldig is, anders None."""
    if item_type in ("category", "divider"):
        return None
    if item_type == "page":
        if not page_id or Page.query.get(page_id) is None:
            return "Kies een geldige pagina."
        return None
    if item_type == "route":
        if not route_endpoint:
            return "Geef een route-eindpunt op (bv. 'shop.products')."
        try:
            url_for(route_endpoint)
        except BuildError:
            return f"Route-eindpunt '{route_endpoint}' bestaat niet of vereist parameters die hier niet ingevuld kunnen worden."
        return None
    if item_type == "external":
        if not external_url:
            return "Geef een externe URL op."
        return None
    return "Ongeldig type."


def _nav_admin_context(error=None):
    top_items = NavItem.query.filter_by(parent_id=None).order_by(NavItem.position).all()
    categories = [i for i in top_items if i.item_type == "category"]
    all_pages = Page.query.order_by(Page.title).all()
    return dict(
        user=g.user, top_items=top_items, categories=categories,
        all_pages=all_pages, error=error,
    )


def _nav_redirect(item_id=None):
    """Redirect naar het navigatie-overzicht, met een anker naar het betrokken
    item zodat de pagina na de herlaad automatisch terug naar dat item scrolt
    (i.p.v. telkens bovenaan te beginnen, wat bij items diep in een lange
    lijst voelt alsof een knop niks deed)."""
    url = url_for("admin.navigation")
    if item_id is not None:
        url += f"#nav-item-{item_id}"
    return redirect(url)


@admin_bp.route("/navigation")
@admin_required
def navigation():
    return render_template("admin/navigation.html", **_nav_admin_context())


@admin_bp.route("/navigation/add", methods=["POST"])
@admin_required
def add_nav_item():
    label = (request.form.get("label") or "").strip()
    item_type = request.form.get("item_type") or ""
    parent_id = request.form.get("parent_id") or None
    parent_id = int(parent_id) if parent_id else None
    page_id = request.form.get("page_id") or None
    page_id = int(page_id) if page_id else None
    team_id = request.form.get("team_id") or None
    team_id = int(team_id) if team_id else None
    route_endpoint = (request.form.get("route_endpoint") or "").strip() or None
    external_url = (request.form.get("external_url") or "").strip() or None
    open_in_new_tab = bool(request.form.get("open_in_new_tab"))

    error = None
    if not label:
        error = "Label is verplicht."
    elif item_type not in NAV_ITEM_TYPES:
        error = "Ongeldig type."
    elif item_type == "category" and parent_id is not None:
        error = "Een categorie kan enkel op het hoofdniveau staan."
    else:
        error = _validate_nav_target(item_type, page_id, team_id, route_endpoint, external_url)

    if error:
        return render_template("admin/navigation.html", **_nav_admin_context(error=error))

    max_position = db.session.query(db.func.max(NavItem.position)).filter_by(parent_id=parent_id).scalar() or 0
    item = NavItem(
        label=label, item_type=item_type, parent_id=parent_id,
        page_id=page_id if item_type == "page" else None,
        team_id=team_id if item_type == "team" else None,
        route_endpoint=route_endpoint if item_type == "route" else None,
        external_url=external_url if item_type == "external" else None,
        open_in_new_tab=open_in_new_tab, position=max_position + 1,
    )
    db.session.add(item)
    db.session.commit()
    return _nav_redirect(item.id)


@admin_bp.route("/navigation/<int:item_id>/edit", methods=["POST"])
@admin_required
def edit_nav_item(item_id):
    item = NavItem.query.get(item_id)
    if item is None:
        return redirect(url_for("admin.navigation"))

    label = (request.form.get("label") or "").strip()
    page_id = request.form.get("page_id") or None
    page_id = int(page_id) if page_id else None
    team_id = request.form.get("team_id") or None
    team_id = int(team_id) if team_id else None
    route_endpoint = (request.form.get("route_endpoint") or "").strip() or None
    external_url = (request.form.get("external_url") or "").strip() or None
    open_in_new_tab = bool(request.form.get("open_in_new_tab"))
    is_visible = bool(request.form.get("is_visible"))

    error = None
    if not label:
        error = "Label is verplicht."
    else:
        error = _validate_nav_target(item.item_type, page_id, team_id, route_endpoint, external_url)

    if error:
        return render_template("admin/navigation.html", **_nav_admin_context(error=error))

    item.label = label
    if item.item_type == "page":
        item.page_id = page_id
    elif item.item_type == "team":
        item.team_id = team_id
    elif item.item_type == "route":
        item.route_endpoint = route_endpoint
    elif item.item_type == "external":
        item.external_url = external_url
    item.open_in_new_tab = open_in_new_tab
    item.is_visible = is_visible
    db.session.commit()
    return _nav_redirect(item.id)


@admin_bp.route("/navigation/<int:item_id>/delete", methods=["POST"])
@admin_required
def delete_nav_item(item_id):
    item = NavItem.query.get(item_id)
    if item is not None:
        # SQLite handhaaft hier geen foreign keys - kinderen expliciet mee
        # verwijderen i.p.v. op een databank-cascade te vertrouwen.
        descendant_ids = _collect_descendant_ids(item_id)
        if descendant_ids:
            NavItem.query.filter(NavItem.id.in_(descendant_ids)).delete(synchronize_session=False)
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("admin.navigation"))


@admin_bp.route("/navigation/<int:item_id>/move", methods=["POST"])
@admin_required
def move_nav_item(item_id):
    """Wisselt de positie van dit item met de vorige/volgende sibling (zelfde parent)."""
    item = NavItem.query.get(item_id)
    if item is None:
        return redirect(url_for("admin.navigation"))

    direction = request.form.get("direction")
    siblings = NavItem.query.filter_by(parent_id=item.parent_id).order_by(NavItem.position).all()
    index = next((i for i, s in enumerate(siblings) if s.id == item.id), None)

    if index is not None:
        swap_index = index - 1 if direction == "up" else index + 1
        if 0 <= swap_index < len(siblings):
            other = siblings[swap_index]
            item.position, other.position = other.position, item.position
            db.session.commit()

    return _nav_redirect(item.id)


@admin_bp.route("/navigation/<int:item_id>/move_to_parent", methods=["POST"])
@admin_required
def move_nav_item_to_parent(item_id):
    """Verplaatst dit item naar een andere categorie (of naar het hoofdniveau)."""
    item = NavItem.query.get(item_id)
    if item is None or item.item_type == "category":
        return redirect(url_for("admin.navigation"))

    new_parent_id = request.form.get("parent_id") or None
    new_parent_id = int(new_parent_id) if new_parent_id else None

    if new_parent_id is not None:
        new_parent = NavItem.query.get(new_parent_id)
        if new_parent is None or new_parent.item_type != "category":
            return redirect(url_for("admin.navigation"))

    max_position = db.session.query(db.func.max(NavItem.position)).filter_by(parent_id=new_parent_id).scalar() or 0
    item.parent_id = new_parent_id
    item.position = max_position + 1
    db.session.commit()
    return _nav_redirect(item.id)


@admin_bp.route("/navigation/reorder", methods=["POST"])
@admin_required
def reorder_nav_items():
    """AJAX-endpoint voor het slepen (SortableJS) in de navigatiebeheer-UI.
    Verwacht JSON: {"items": [{"id": int, "parent_id": int|null, "position": int}, ...]}"""
    data = request.get_json(silent=True) or {}
    updates = data.get("items") or []

    category_ids = {i.id for i in NavItem.query.filter_by(item_type="category").all()}

    for update in updates:
        item = NavItem.query.get(update.get("id"))
        if item is None:
            continue
        new_parent_id = update.get("parent_id")
        # Een categorie mag enkel op het hoofdniveau blijven staan.
        if item.item_type == "category" and new_parent_id is not None:
            continue
        # Enkel een bestaande categorie (of het hoofdniveau) is een geldige parent.
        if new_parent_id is not None and new_parent_id not in category_ids:
            continue
        item.parent_id = new_parent_id
        item.position = update.get("position", item.position)

    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.route("/nieuws")
@admin_required
def nieuws():
    alle_berichten = NieuwsBericht.query.order_by(NieuwsBericht.position).all()
    return render_template("admin/nieuws_list.html", user=g.user, nieuwsberichten=alle_berichten)


@admin_bp.route("/nieuws/add", methods=["GET", "POST"])
@admin_required
def add_nieuws():
    if request.method == "GET":
        return render_template("admin/nieuws_form.html", user=g.user, bericht=None, categorieen=NIEUWS_CATEGORIEEN)

    titel = (request.form.get("titel") or "").strip()
    inhoud_raw = request.form.get("inhoud") or ""
    samenvatting = (request.form.get("samenvatting") or "").strip() or None
    categorie = request.form.get("categorie") or NIEUWS_CATEGORIEEN[0]
    gepubliceerd_op = _parse_datetime_local(request.form.get("gepubliceerd_op")) or datetime.utcnow()
    groot = bool(request.form.get("groot"))

    error = None
    if not titel or _html_is_blank(inhoud_raw):
        error = "Titel en inhoud zijn verplicht."
    elif categorie not in NIEUWS_CATEGORIEEN:
        error = "Ongeldige categorie."

    if error:
        return render_template(
            "admin/nieuws_form.html", user=g.user, bericht=None, categorieen=NIEUWS_CATEGORIEEN, error=error,
            form_titel=titel, form_inhoud=sanitize_html(inhoud_raw), form_samenvatting=samenvatting,
            form_categorie=categorie, form_groot=groot,
        )

    # Nieuwe berichten komen standaard vooraan (net als 'laatste nieuws'), de
    # admin kan de volgorde nadien met de pijltjes aanpassen.
    min_position = db.session.query(db.func.min(NieuwsBericht.position)).scalar() or 0
    afbeelding = _save_uploaded_image(request.files.get("afbeelding"))
    bericht = NieuwsBericht(
        titel=titel, inhoud=sanitize_html(inhoud_raw), samenvatting=samenvatting, afbeelding=afbeelding,
        categorie=categorie, gepubliceerd_op=gepubliceerd_op, groot=groot,
        position=min_position - 1,
    )
    db.session.add(bericht)
    db.session.commit()
    return redirect(url_for("admin.nieuws"))


@admin_bp.route("/nieuws/<int:bericht_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_nieuws(bericht_id):
    bericht = NieuwsBericht.query.get(bericht_id)
    if bericht is None:
        return redirect(url_for("admin.nieuws"))

    if request.method == "GET":
        return render_template("admin/nieuws_form.html", user=g.user, bericht=bericht, categorieen=NIEUWS_CATEGORIEEN)

    titel = (request.form.get("titel") or "").strip()
    inhoud_raw = request.form.get("inhoud") or ""
    samenvatting = (request.form.get("samenvatting") or "").strip() or None
    categorie = request.form.get("categorie") or NIEUWS_CATEGORIEEN[0]
    gepubliceerd_op = _parse_datetime_local(request.form.get("gepubliceerd_op")) or bericht.gepubliceerd_op
    groot = bool(request.form.get("groot"))

    error = None
    if not titel or _html_is_blank(inhoud_raw):
        error = "Titel en inhoud zijn verplicht."
    elif categorie not in NIEUWS_CATEGORIEEN:
        error = "Ongeldige categorie."

    if error:
        return render_template(
            "admin/nieuws_form.html", user=g.user, bericht=bericht, categorieen=NIEUWS_CATEGORIEEN, error=error,
            form_titel=titel, form_inhoud=sanitize_html(inhoud_raw), form_samenvatting=samenvatting,
            form_categorie=categorie, form_groot=groot,
        )

    bericht.titel = titel
    bericht.inhoud = sanitize_html(inhoud_raw)
    bericht.samenvatting = samenvatting
    bericht.categorie = categorie
    bericht.gepubliceerd_op = gepubliceerd_op
    bericht.groot = groot

    new_image = _save_uploaded_image(request.files.get("afbeelding"))
    if new_image:
        _delete_uploaded_image(bericht.afbeelding)
        bericht.afbeelding = new_image
    elif request.form.get("verwijder_afbeelding"):
        _delete_uploaded_image(bericht.afbeelding)
        bericht.afbeelding = None

    db.session.commit()
    return redirect(url_for("admin.nieuws"))


@admin_bp.route("/nieuws/<int:bericht_id>/move", methods=["POST"])
@admin_required
def move_nieuws(bericht_id):
    """Wisselt de positie van dit bericht met het vorige/volgende (handmatige weergavevolgorde)."""
    bericht = NieuwsBericht.query.get(bericht_id)
    if bericht is None:
        return redirect(url_for("admin.nieuws"))

    direction = request.form.get("direction")
    alle_berichten = NieuwsBericht.query.order_by(NieuwsBericht.position).all()
    index = next((i for i, b in enumerate(alle_berichten) if b.id == bericht.id), None)

    if index is not None:
        swap_index = index - 1 if direction == "up" else index + 1
        if 0 <= swap_index < len(alle_berichten):
            other = alle_berichten[swap_index]
            bericht.position, other.position = other.position, bericht.position
            db.session.commit()

    return redirect(url_for("admin.nieuws"))


@admin_bp.route("/evenementen")
@admin_required
def evenementen():
    alle_evenementen = Evenement.query.order_by(Evenement.datum.asc()).all()
    return render_template(
        "admin/evenementen_list.html", user=g.user, evenementen=alle_evenementen,
        huidige_datum=datetime.utcnow().date(),
    )


@admin_bp.route("/evenementen/add", methods=["GET", "POST"])
@admin_required
def add_evenement():
    if request.method == "GET":
        return render_template("admin/evenementen_form.html", user=g.user, evenement=None)

    titel = (request.form.get("titel") or "").strip()
    datum = _parse_date(request.form.get("datum"))
    tekst = (request.form.get("tekst") or "").strip()

    error = None
    if not titel or not datum or not tekst:
        error = "Titel, datum en tekst zijn verplicht."

    if error:
        return render_template(
            "admin/evenementen_form.html", user=g.user, evenement=None, error=error,
            form_titel=titel, form_datum=request.form.get("datum"), form_tekst=tekst,
        )

    evenement = Evenement(titel=titel, datum=datum, tekst=tekst)
    db.session.add(evenement)
    db.session.commit()
    return redirect(url_for("admin.evenementen"))


@admin_bp.route("/evenementen/<int:evenement_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_evenement(evenement_id):
    evenement = Evenement.query.get(evenement_id)
    if evenement is None:
        return redirect(url_for("admin.evenementen"))

    if request.method == "GET":
        return render_template("admin/evenementen_form.html", user=g.user, evenement=evenement)

    titel = (request.form.get("titel") or "").strip()
    datum = _parse_date(request.form.get("datum"))
    tekst = (request.form.get("tekst") or "").strip()

    error = None
    if not titel or not datum or not tekst:
        error = "Titel, datum en tekst zijn verplicht."

    if error:
        return render_template(
            "admin/evenementen_form.html", user=g.user, evenement=evenement, error=error,
            form_titel=titel, form_datum=request.form.get("datum"), form_tekst=tekst,
        )

    evenement.titel = titel
    evenement.datum = datum
    evenement.tekst = tekst
    db.session.commit()
    return redirect(url_for("admin.evenementen"))


@admin_bp.route("/evenementen/<int:evenement_id>/delete", methods=["POST"])
@admin_required
def delete_evenement(evenement_id):
    evenement = Evenement.query.get(evenement_id)
    if evenement is not None:
        db.session.delete(evenement)
        db.session.commit()
    return redirect(url_for("admin.evenementen"))


@admin_bp.route("/sponsors")
@admin_required
def sponsors():
    alle_sponsors = Sponsor.query.order_by(Sponsor.position).all()
    return render_template("admin/sponsors_list.html", user=g.user, sponsors=alle_sponsors)


@admin_bp.route("/sponsors/add", methods=["POST"])
@admin_required
def add_sponsor():
    naam = (request.form.get("naam") or "").strip()
    website_url = (request.form.get("website_url") or "").strip() or None
    logo = _save_uploaded_image(request.files.get("logo"))

    if not naam or not logo:
        # logo werd hierboven al opgeslagen (indien meegestuurd) vóór deze
        # check - zonder opruimen zou dat bestand nergens meer naar wijzen
        # als de sponsor nu niet aangemaakt wordt.
        _delete_uploaded_image(logo)
        # Sponsors staan op één lijstpagina (zoals producten) - bij een
        # fout gewoon terug naar het overzicht, de naam is snel opnieuw ingevuld.
        return redirect(url_for("admin.sponsors"))

    max_position = db.session.query(db.func.max(Sponsor.position)).scalar() or 0
    sponsor = Sponsor(naam=naam, logo=logo, website_url=website_url, position=max_position + 1)
    db.session.add(sponsor)
    db.session.commit()
    return redirect(url_for("admin.sponsors"))


@admin_bp.route("/sponsors/<int:sponsor_id>/edit", methods=["POST"])
@admin_required
def edit_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor is None:
        return redirect(url_for("admin.sponsors"))

    naam = (request.form.get("naam") or "").strip()
    if naam:
        sponsor.naam = naam
    sponsor.website_url = (request.form.get("website_url") or "").strip() or None

    new_logo = _save_uploaded_image(request.files.get("logo"))
    if new_logo:
        _delete_uploaded_image(sponsor.logo)
        sponsor.logo = new_logo

    db.session.commit()
    return redirect(url_for("admin.sponsors"))


@admin_bp.route("/sponsors/<int:sponsor_id>/toggle_active", methods=["POST"])
@admin_required
def toggle_sponsor_active(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor is not None:
        sponsor.is_active = not sponsor.is_active
        db.session.commit()
    return redirect(url_for("admin.sponsors"))


@admin_bp.route("/sponsors/<int:sponsor_id>/move", methods=["POST"])
@admin_required
def move_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor is None:
        return redirect(url_for("admin.sponsors"))

    direction = request.form.get("direction")
    all_sponsors = Sponsor.query.order_by(Sponsor.position).all()
    index = next((i for i, s in enumerate(all_sponsors) if s.id == sponsor.id), None)

    if index is not None:
        swap_index = index - 1 if direction == "up" else index + 1
        if 0 <= swap_index < len(all_sponsors):
            other = all_sponsors[swap_index]
            sponsor.position, other.position = other.position, sponsor.position
            db.session.commit()

    return redirect(url_for("admin.sponsors"))


@admin_bp.route("/sponsors/<int:sponsor_id>/delete", methods=["POST"])
@admin_required
def delete_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor is not None:
        _delete_uploaded_image(sponsor.logo)
        db.session.delete(sponsor)
        db.session.commit()
    return redirect(url_for("admin.sponsors"))


@admin_bp.route("/nieuws/<int:bericht_id>/delete", methods=["POST"])
@admin_required
def delete_nieuws(bericht_id):
    bericht = NieuwsBericht.query.get(bericht_id)
    if bericht is not None:
        _delete_uploaded_image(bericht.afbeelding)
        db.session.delete(bericht)
        db.session.commit()
    return redirect(url_for("admin.nieuws"))


@admin_bp.route("/teams")
@admin_required
def teams():
    alle_teams = Team.query.order_by(Team.sectie, Team.naam).all()
    return render_template("admin/teams_list.html", user=g.user, teams=alle_teams, sectie_labels=TEAM_SECTIE_LABELS)


@admin_bp.route("/teams/add", methods=["GET", "POST"])
@admin_required
def add_team():
    if request.method == "GET":
        return render_template("admin/team_form.html", user=g.user, team=None, team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS)

    naam = (request.form.get("naam") or "").strip()
    slug = _slugify(request.form.get("slug") or naam)
    sectie = request.form.get("sectie") or "dames"
    categorie = (request.form.get("categorie") or "").strip() or None
    trainer = (request.form.get("trainer") or "").strip() or None
    omschrijving = (request.form.get("omschrijving") or "").strip() or None
    aantal_bekers, fout_bekers = _parse_optioneel_positief_getal(request.form.get("aantal_bekers"))
    aantal_landstitels, fout_landstitels = _parse_optioneel_positief_getal(request.form.get("aantal_landstitels"))
    aantal_europese_wedstrijden, fout_europees = _parse_optioneel_positief_getal(request.form.get("aantal_europese_wedstrijden"))

    error = None
    if not naam:
        error = "Naam is verplicht."
    elif sectie not in TEAM_SECTIES:
        error = "Ongeldige sectie."
    elif not slug:
        error = "Slug is verplicht."
    elif Team.query.filter_by(slug=slug).first() is not None:
        error = f"Er bestaat al een team met slug '{slug}'."
    elif fout_bekers or fout_landstitels or fout_europees:
        error = fout_bekers or fout_landstitels or fout_europees

    if error:
        return render_template(
            "admin/team_form.html", user=g.user, team=None, error=error,
            team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS,
            form_naam=naam, form_slug=slug, form_sectie=sectie, form_categorie=categorie,
            form_trainer=trainer, form_omschrijving=omschrijving,
            form_aantal_bekers=aantal_bekers if aantal_bekers is not None else "",
            form_aantal_landstitels=aantal_landstitels if aantal_landstitels is not None else "",
            form_aantal_europese_wedstrijden=aantal_europese_wedstrijden if aantal_europese_wedstrijden is not None else "",
        )

    foto_url = _save_uploaded_image(request.files.get("foto"))
    team = Team(
        naam=naam, slug=slug, sectie=sectie, categorie=categorie,
        trainer=trainer, omschrijving=omschrijving, foto_url=foto_url,
        aantal_bekers=aantal_bekers, aantal_landstitels=aantal_landstitels,
        aantal_europese_wedstrijden=aantal_europese_wedstrijden,
    )
    db.session.add(team)
    db.session.commit()
    return redirect(url_for("admin.teams"))


@admin_bp.route("/teams/<int:team_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        return redirect(url_for("admin.teams"))

    if request.method == "GET":
        return render_template("admin/team_form.html", user=g.user, team=team, team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS)

    naam = (request.form.get("naam") or "").strip()
    slug = _slugify(request.form.get("slug") or naam)
    sectie = request.form.get("sectie") or "dames"
    categorie = (request.form.get("categorie") or "").strip() or None
    trainer = (request.form.get("trainer") or "").strip() or None
    omschrijving = (request.form.get("omschrijving") or "").strip() or None
    aantal_bekers, fout_bekers = _parse_optioneel_positief_getal(request.form.get("aantal_bekers"))
    aantal_landstitels, fout_landstitels = _parse_optioneel_positief_getal(request.form.get("aantal_landstitels"))
    aantal_europese_wedstrijden, fout_europees = _parse_optioneel_positief_getal(request.form.get("aantal_europese_wedstrijden"))

    error = None
    if not naam:
        error = "Naam is verplicht."
    elif sectie not in TEAM_SECTIES:
        error = "Ongeldige sectie."
    elif not slug:
        error = "Slug is verplicht."
    elif Team.query.filter(Team.slug == slug, Team.id != team.id).first() is not None:
        error = f"Er bestaat al een ander team met slug '{slug}'."
    elif fout_bekers or fout_landstitels or fout_europees:
        error = fout_bekers or fout_landstitels or fout_europees

    if error:
        return render_template(
            "admin/team_form.html", user=g.user, team=team, error=error,
            team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS,
            form_naam=naam, form_slug=slug, form_sectie=sectie, form_categorie=categorie,
            form_trainer=trainer, form_omschrijving=omschrijving,
            form_aantal_bekers=aantal_bekers if aantal_bekers is not None else "",
            form_aantal_landstitels=aantal_landstitels if aantal_landstitels is not None else "",
            form_aantal_europese_wedstrijden=aantal_europese_wedstrijden if aantal_europese_wedstrijden is not None else "",
        )

    team.naam = naam
    team.slug = slug
    team.sectie = sectie
    team.categorie = categorie
    team.trainer = trainer
    team.omschrijving = omschrijving
    team.aantal_bekers = aantal_bekers
    team.aantal_landstitels = aantal_landstitels
    team.aantal_europese_wedstrijden = aantal_europese_wedstrijden

    new_foto = _save_uploaded_image(request.files.get("foto"))
    if new_foto:
        _delete_uploaded_image(team.foto_url)
        team.foto_url = new_foto
    elif request.form.get("verwijder_foto"):
        _delete_uploaded_image(team.foto_url)
        team.foto_url = None

    db.session.commit()
    return redirect(url_for("admin.teams"))


@admin_bp.route("/teams/<int:team_id>/delete", methods=["POST"])
@admin_required
def delete_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        return redirect(url_for("admin.teams"))

    linking_items = NavItem.query.filter_by(team_id=team_id).all()
    if linking_items:
        labels = ", ".join(f"'{i.label}'" for i in linking_items)
        error = (
            f"Dit team kan niet verwijderd worden: de navigatie verwijst er nog naar "
            f"via {labels}. Verwijder of wijzig eerst dat navigatie-item op de "
            f"Navigatie-pagina, dan kan het team hierna wel verwijderd worden."
        )
        alle_teams = Team.query.order_by(Team.sectie, Team.naam).all()
        return render_template("admin/teams_list.html", user=g.user, teams=alle_teams, sectie_labels=TEAM_SECTIE_LABELS, error=error)

    _delete_uploaded_image(team.foto_url)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for("admin.teams"))
