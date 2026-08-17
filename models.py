"""
models.py
---------
Alle database-modellen, als SQLAlchemy ORM-klassen.

Gegroepeerd in:
1. Club (Team, NieuwsBericht)
2. Gebruikers & authenticatie (User)
3. Webshop (Product, ProductVariant, Order, OrderLine)

De webshop-modellen zijn gemigreerd vanuit de originele sqlite3-versie
(model.py uit hello_flask) naar SQLAlchemy, met dezelfde velden/relaties,
zodat bestaande data-structuur en logica behouden blijven.
"""

from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------------------------
# Club
# ---------------------------------------------------------------------------

# Secties waarin een team kan worden ingedeeld, met hun weergavenaam in de admin/UI.
TEAM_SECTIE_LABELS = {
    "dames": "Dames",
    "heren": "Heren",
    "jeugd": "Jeugd",
    "ghandbal": "G-Handbal",
    "fithandbal": "FIT-Handbal",
}
TEAM_SECTIES = list(TEAM_SECTIE_LABELS.keys())


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)   # bv. "heren-1", gebruikt in de URL
    sectie = db.Column(db.String(20), nullable=False)                # zie TEAM_SECTIES
    categorie = db.Column(db.String(50))
    trainer = db.Column(db.String(100))
    omschrijving = db.Column(db.Text)
    foto_url = db.Column(db.String(255))                             # bestandsnaam in static/images/

    def __repr__(self):
        return f"<Team {self.naam}>"


# Categorieën voor nieuwsberichten op de homepage
NIEUWS_CATEGORIEEN = ["Club", "Dames", "Heren", "Jeugd"]


class NieuwsBericht(db.Model):
    __tablename__ = "nieuwsberichten"

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(200), nullable=False)
    inhoud = db.Column(db.Text, nullable=False)   # rich-text HTML, gesaniteerd bij opslaan (zie utils/sanitize.py)
    # Optionele, admin-geschreven tekst voor de verkorte weergave (kaarten/
    # slider). Leeg = automatisch een stuk van 'inhoud' tonen (zie de
    # 'platte_tekst'-Jinja-filter in utils/sanitize.py).
    samenvatting = db.Column(db.Text)
    afbeelding = db.Column(db.String(255))          # bestandsnaam in static/images/
    categorie = db.Column(db.String(20), nullable=False, default="Club")
    gepubliceerd_op = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer, nullable=False, default=0)   # handmatige weergavevolgorde (admin: pijltjes omhoog/omlaag)
    groot = db.Column(db.Boolean, nullable=False, default=False)    # 'groot' formaat: kaart neemt 2 kolommen in

    def __repr__(self):
        return f"<NieuwsBericht {self.titel}>"


class Sponsor(db.Model):
    """Een sponsor, getoond in de sponsorbalk op de homepage."""
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(150), nullable=False)
    logo = db.Column(db.String(255), nullable=False)   # bestandsnaam in static/images/
    website_url = db.Column(db.String(500))
    position = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Sponsor {self.naam}>"


# Standaard-categorieën waarmee InschrijvingCategorie geseed wordt (zie utils/inschrijving.py)
DEFAULT_INSCHRIJVING_CATEGORIEEN = [
    "Kleuters (Ballenbaasjes)", "JM08 & JM10", "JM12", "J14", "M14",
    "G-Handbal", "FIT-Handbal",
]

# Standaard-opties voor "hoe heb je de Ballenbaasjes leren kennen" (optioneel veld)
DEFAULT_HOE_GEHOORD_OPTIES = [
    "Via een vriendje", "Instagram", "Facebook", "Flyer",
    "Schoolinitiatie", "E-mail", "Google", "Andere",
]

# Veldsleutels van het inschrijvingsformulier, met hun standaardlabel en
# standaard-verplicht-status (zie InschrijvingVeldConfig / utils/inschrijving.py)
INSCHRIJVING_VELD_DEFINITIES = [
    ("voornaam_speler", "Voornaam speler", True),
    ("achternaam_speler", "Achternaam speler", True),
    ("geboortedatum", "Geboortedatum", True),
    ("geboorteplaats", "Geboorteplaats", True),
    ("categorie", "Categorie", True),
    ("straat_nr", "Straat en huisnummer", True),
    ("postcode", "Postcode", True),
    ("gemeente", "Gemeente", True),
    ("email", "E-mailadres", True),
    ("telefoon", "Gsm-nummer", True),
    ("hoe_gehoord", "Hoe heb je de Ballenbaasjes leren kennen?", False),
    ("school", "School", False),
    ("opmerkingen", "Belangrijke info over het kind", False),
]


class School(db.Model):
    """Eén school, beheerd via de admin, voor de schoolkeuze in het inschrijvingsformulier."""
    __tablename__ = "scholen"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<School {self.naam}>"


class InschrijvingCategorie(db.Model):
    """Eén categorie (bv. 'JM12'), beheerd via de admin, voor de categoriekeuze in het inschrijvingsformulier."""
    __tablename__ = "inschrijving_categorieen"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<InschrijvingCategorie {self.naam}>"


class HoeGehoordOptie(db.Model):
    """Eén keuzeoptie voor 'hoe heb je de Ballenbaasjes leren kennen', beheerd via de admin."""
    __tablename__ = "hoe_gehoord_opties"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<HoeGehoordOptie {self.naam}>"


class InschrijvingVeldConfig(db.Model):
    """Admin-bewerkbaar label + verplicht/optioneel-status van één veld van het inschrijvingsformulier."""
    __tablename__ = "inschrijving_veld_config"

    id = db.Column(db.Integer, primary_key=True)
    veld_sleutel = db.Column(db.String(50), unique=True, nullable=False)
    label = db.Column(db.String(150), nullable=False)
    verplicht = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<InschrijvingVeldConfig {self.veld_sleutel}>"


class Inschrijving(db.Model):
    """
    Eén inschrijvingsaanvraag, ingediend via het gedeelde formulier voor
    Jeugd, G-Handbal en FIT-Handbal. Bij elke nieuwe inschrijving gaat er
    automatisch een e-mail naar de club (zie utils/mail.py).

    Alle velden behalve id/aangemaakt_op zijn nullable op databankniveau:
    of een veld verplicht is, wordt admin-bewerkbaar bepaald via
    InschrijvingVeldConfig en afgedwongen in routes/jeugd.py, niet via een
    vast databankschema.
    """
    __tablename__ = "inschrijvingen"

    id = db.Column(db.Integer, primary_key=True)
    categorie = db.Column(db.String(100))

    # Speler
    voornaam_speler = db.Column(db.String(100))
    achternaam_speler = db.Column(db.String(100))
    geboortedatum = db.Column(db.Date)
    geboorteplaats = db.Column(db.String(100))

    # Adres
    straat_nr = db.Column(db.String(150))
    postcode = db.Column(db.String(20))
    gemeente = db.Column(db.String(100))

    # Contact
    email = db.Column(db.String(150))
    telefoon = db.Column(db.String(30))

    # Optioneel
    hoe_gehoord = db.Column(db.String(100))
    school = db.Column(db.String(150))
    opmerkingen = db.Column(db.Text)

    aangemaakt_op = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Inschrijving {self.voornaam_speler} {self.achternaam_speler} ({self.categorie})>"


class VergeetMijVerzoek(db.Model):
    """Een GDPR-verzoek tot verwijdering van persoonsgegevens."""
    __tablename__ = "vergeet_mij_verzoeken"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    lidnummer = db.Column(db.String(50))
    opmerking = db.Column(db.Text)
    verwerkt = db.Column(db.Boolean, nullable=False, default=False)
    aangemaakt_op = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VergeetMijVerzoek {self.naam}>"


NAV_ITEM_TYPES = ["category", "divider", "page", "team", "route", "external"]


class NavItem(db.Model):
    """
    Eén item in de navbar. Zelf-refererende boom via parent_id:
    - "category": een dropdown-opener op het hoofdniveau (parent_id is None),
      heeft kinderen.
    - "divider": een niet-klikbaar groepslabel binnen een dropdown (bv.
      "Dames"/"Heren" onder Teams), geen link, geen kinderen.
    - "page": link naar een Page (page_id).
    - "team": link naar een Team (team_id).
    - "route": link naar een vaste Flask-eindpunt-naam (route_endpoint),
      voor bestemmingen die code-gedreven blijven (bv. "shop.products").
    - "external": link naar een vrije URL (external_url).

    page_id/team_id zijn echte foreign keys (i.p.v. een losse tekst-slug):
    zo kan een Page/Team niet verwijderd worden zolang er nog een NavItem
    naar verwijst (zie admin_required routes delete_page/delete_team) - een
    admin kan via de UI dus nooit een kapotte menu-link achterlaten.
    """
    __tablename__ = "nav_items"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("nav_items.id"), nullable=True)
    label = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    item_type = db.Column(db.String(20), nullable=False)

    page_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)
    route_endpoint = db.Column(db.String(150), nullable=True)
    external_url = db.Column(db.String(500), nullable=True)

    open_in_new_tab = db.Column(db.Boolean, nullable=False, default=False)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)

    children = db.relationship(
        "NavItem", backref=db.backref("parent", remote_side=[id]), order_by="NavItem.position"
    )
    page = db.relationship("Page")
    team = db.relationship("Team")

    def __repr__(self):
        return f"<NavItem {self.label} ({self.item_type})>"


class Page(db.Model):
    """Een door de admin beheerde inhoudspagina, getoond via /pagina/<slug>.
    De inhoud zelf zit in PageBlock-rijen (zie hieronder); body_html is
    legacy (van vóór de blokken-page-builder) en wordt niet meer gebruikt
    door nieuwe/bewerkte pagina's."""
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body_html = db.Column(db.Text, nullable=False, default="")
    hero_image = db.Column(db.String(255))   # bestandsnaam in static/images/
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blocks = db.relationship(
        "PageBlock", order_by="PageBlock.position", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Page {self.slug}>"


PAGE_BLOCK_TYPES = ["rich_text", "image_gallery", "columns", "video", "button"]


class PageBlock(db.Model):
    """Eén content-blok binnen een Page, getoond in volgorde van position.
    De vorm van 'data' hangt af van block_type - zie utils/page_blocks.py
    en de bloksjablonen in templates/pages/_blocks/ en
    templates/admin/page_block_form.html voor de exacte sleutels per type."""
    __tablename__ = "page_blocks"

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id"), nullable=False)
    block_type = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    data = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PageBlock {self.block_type} (page {self.page_id}, pos {self.position})>"


class SiteText(db.Model):
    """
    Eén admin-bewerkbaar tekstfragment (hero-titel/introzin) dat verspreid
    over de site in templates gebruikt wordt - zie utils/site_text.py voor
    de volledige lijst van sleutels en hun standaardwaarde.
    """
    __tablename__ = "site_teksten"

    id = db.Column(db.Integer, primary_key=True)
    sleutel = db.Column(db.String(100), unique=True, nullable=False)
    omschrijving = db.Column(db.String(255))
    waarde = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<SiteText {self.sleutel}>"


# ---------------------------------------------------------------------------
# Gebruikers
# ---------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    membership_status = db.Column(db.String(30), default="Bronze", nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    orders = db.relationship("Order", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------------------------------------------------------------------
# Webshop
# ---------------------------------------------------------------------------

class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))   # bestandsnaam in static/images/
    printing_available = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    variants = db.relationship(
        "ProductVariant", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product {self.product_name}>"


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    variant_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<ProductVariant {self.color}/{self.size} ({self.product_id})>"


# Volgorde bepaalt de keuzemogelijkheden in het admin-statusveld
ORDER_STATUSES = ["Ontvangen", "In behandeling", "Klaar voor verzending", "Verzonden", "Geannuleerd", "Terugbetaald"]


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)          # subtotaal producten, excl. verzending
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="Pending", nullable=False)
    order_status = db.Column(db.String(30), default="Ontvangen", nullable=False)

    lines = db.relationship(
        "OrderLine", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def total_paid(self):
        """Subtotaal + verzendkosten - wat de klant effectief betaald heeft."""
        return float(self.total_price) + float(self.shipping_cost)

    def __repr__(self):
        return f"<Order #{self.order_id} - {self.payment_status}>"


class OrderLine(db.Model):
    __tablename__ = "order_lines"

    order_line_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.variant_id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)   # prijs per stuk, bevroren bij bestellen (incl. bedrukking)
    print_front = db.Column(db.String(100), nullable=True)
    print_back = db.Column(db.String(100), nullable=True)

    product = db.relationship("Product")
    variant = db.relationship("ProductVariant")

    @property
    def subtotal(self):
        return self.quantity * float(self.price)
