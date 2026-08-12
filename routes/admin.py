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

from flask import Blueprint, render_template, request, redirect, url_for, current_app, g, jsonify
from werkzeug.utils import secure_filename

from werkzeug.routing import BuildError

from datetime import datetime

from extensions import db
from models import (
    Product, ProductVariant, User, Order, ORDER_STATUSES, Inschrijving, VergeetMijVerzoek,
    Page, NavItem, NAV_ITEM_TYPES, NieuwsBericht, NIEUWS_CATEGORIEEN, Sponsor, Team,
    TEAM_SECTIES, TEAM_SECTIE_LABELS, School, SiteText,
    InschrijvingCategorie, HoeGehoordOptie, InschrijvingVeldConfig, INSCHRIJVING_VELD_DEFINITIES,
)
from utils.auth import admin_required
from utils.mail import send_admin_cancellation_mail
from utils.sanitize import sanitize_html
from utils.site_text import SITE_TEXT_DEFAULTS, get_site_teksten
from utils.inschrijving import get_inschrijving_categorieen, get_hoe_gehoord_opties, get_inschrijving_veld_config

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


def _parse_datetime_local(value):
    """Parseert de waarde van een <input type="datetime-local"> (bv. '2026-08-08T14:30'),
    geeft None terug als de waarde leeg of ongeldig is."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


def _html_is_blank(html):
    """True als deze rich-text HTML geen zichtbare tekst of afbeelding bevat
    (Quill stuurt een lege editor als '<p><br></p>', niet als lege string)."""
    text = re.sub(r"<[^>]+>", "", html or "").strip()
    return not text and "<img" not in (html or "")


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template("admin.html", user=g.user)


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


@admin_bp.route("/site-teksten", methods=["GET", "POST"])
@admin_required
def site_teksten():
    if request.method == "POST":
        bestaande = {r.sleutel: r for r in SiteText.query.all()}
        for _groep, sleutel, omschrijving, standaard_waarde in SITE_TEXT_DEFAULTS:
            nieuwe_waarde = (request.form.get(sleutel) or "").strip() or standaard_waarde
            if sleutel in bestaande:
                bestaande[sleutel].waarde = nieuwe_waarde
            else:
                db.session.add(SiteText(sleutel=sleutel, omschrijving=omschrijving, waarde=nieuwe_waarde))
        db.session.commit()
        return redirect(url_for("admin.site_teksten"))

    waarden = get_site_teksten()
    groepen = []
    for groep, sleutel, omschrijving, _standaard_waarde in SITE_TEXT_DEFAULTS:
        if not groepen or groepen[-1][0] != groep:
            groepen.append((groep, []))
        groepen[-1][1].append((sleutel, omschrijving, waarden[sleutel]))

    return render_template("admin/site_teksten.html", user=g.user, groepen=groepen)


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


@admin_bp.route("/pages")
@admin_required
def pages():
    all_pages = Page.query.order_by(Page.title).all()
    return render_template("admin/pages_list.html", user=g.user, pages=all_pages)


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
        return render_template("admin/page_form.html", user=g.user, page=None)

    title = (request.form.get("title") or "").strip()
    slug = _slugify(request.form.get("slug") or title)
    body_html = sanitize_html(request.form.get("body_html") or "")
    is_published = bool(request.form.get("is_published"))
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
            "admin/page_form.html", user=g.user, page=None, error=error,
            form_title=title, form_slug=slug, form_body_html=body_html,
            form_is_published=is_published,
        )

    page = Page(
        title=title, slug=slug, body_html=body_html,
        hero_image=hero_image, is_published=is_published,
    )
    db.session.add(page)
    db.session.commit()
    return redirect(url_for("admin.pages"))


@admin_bp.route("/pages/<int:page_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_page(page_id):
    page = Page.query.get(page_id)
    if page is None:
        return redirect(url_for("admin.pages"))

    if request.method == "GET":
        return render_template("admin/page_form.html", user=g.user, page=page)

    title = (request.form.get("title") or "").strip()
    slug = _slugify(request.form.get("slug") or title)
    body_html_raw = request.form.get("body_html") or ""
    is_published = bool(request.form.get("is_published"))

    error = None
    if not title:
        error = "Titel is verplicht."
    elif not slug:
        error = "Slug is verplicht."
    elif Page.query.filter(Page.slug == slug, Page.id != page.id).first() is not None:
        error = f"Er bestaat al een andere pagina met slug '{slug}'. Kies een andere titel of slug."

    if error:
        return render_template(
            "admin/page_form.html", user=g.user, page=page, error=error,
            form_title=title, form_slug=slug, form_body_html=sanitize_html(body_html_raw),
            form_is_published=is_published,
        )

    page.title = title
    page.slug = slug
    page.body_html = sanitize_html(body_html_raw)
    page.is_published = is_published

    new_image = _save_uploaded_image(request.files.get("hero_image"))
    if new_image:
        _delete_uploaded_image(page.hero_image)
        page.hero_image = new_image

    db.session.commit()
    return redirect(url_for("admin.pages"))


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
        all_pages = Page.query.order_by(Page.title).all()
        return render_template("admin/pages_list.html", user=g.user, pages=all_pages, error=error)

    _delete_uploaded_image(page.hero_image)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for("admin.pages"))


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
    if item_type == "team":
        if not team_id or Team.query.get(team_id) is None:
            return "Kies een geldig team."
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
    all_teams = Team.query.order_by(Team.sectie, Team.naam).all()
    return dict(
        user=g.user, top_items=top_items, categories=categories,
        all_pages=all_pages, all_teams=all_teams, error=error,
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
            form_titel=titel, form_inhoud=sanitize_html(inhoud_raw), form_categorie=categorie, form_groot=groot,
        )

    # Nieuwe berichten komen standaard vooraan (net als 'laatste nieuws'), de
    # admin kan de volgorde nadien met de pijltjes aanpassen.
    min_position = db.session.query(db.func.min(NieuwsBericht.position)).scalar() or 0
    afbeelding = _save_uploaded_image(request.files.get("afbeelding"))
    bericht = NieuwsBericht(
        titel=titel, inhoud=sanitize_html(inhoud_raw), afbeelding=afbeelding,
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
            form_titel=titel, form_inhoud=sanitize_html(inhoud_raw), form_categorie=categorie, form_groot=groot,
        )

    bericht.titel = titel
    bericht.inhoud = sanitize_html(inhoud_raw)
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

    error = None
    if not naam:
        error = "Naam is verplicht."
    elif sectie not in TEAM_SECTIES:
        error = "Ongeldige sectie."
    elif not slug:
        error = "Slug is verplicht."
    elif Team.query.filter_by(slug=slug).first() is not None:
        error = f"Er bestaat al een team met slug '{slug}'."

    if error:
        return render_template(
            "admin/team_form.html", user=g.user, team=None, error=error,
            team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS,
            form_naam=naam, form_slug=slug, form_sectie=sectie, form_categorie=categorie,
            form_trainer=trainer, form_omschrijving=omschrijving,
        )

    foto_url = _save_uploaded_image(request.files.get("foto"))
    team = Team(
        naam=naam, slug=slug, sectie=sectie, categorie=categorie,
        trainer=trainer, omschrijving=omschrijving, foto_url=foto_url,
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

    error = None
    if not naam:
        error = "Naam is verplicht."
    elif sectie not in TEAM_SECTIES:
        error = "Ongeldige sectie."
    elif not slug:
        error = "Slug is verplicht."
    elif Team.query.filter(Team.slug == slug, Team.id != team.id).first() is not None:
        error = f"Er bestaat al een ander team met slug '{slug}'."

    if error:
        return render_template(
            "admin/team_form.html", user=g.user, team=team, error=error,
            team_secties=TEAM_SECTIES, sectie_labels=TEAM_SECTIE_LABELS,
            form_naam=naam, form_slug=slug, form_sectie=sectie, form_categorie=categorie,
            form_trainer=trainer, form_omschrijving=omschrijving,
        )

    team.naam = naam
    team.slug = slug
    team.sectie = sectie
    team.categorie = categorie
    team.trainer = trainer
    team.omschrijving = omschrijving

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
