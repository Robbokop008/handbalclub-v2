"""
models.py
---------
Alle database-modellen, als SQLAlchemy ORM-klassen.

Gegroepeerd in:
1. Club (Team, NieuwsBericht, Evenement, Sponsor, Affiche, ...)
2. Gebruikers & authenticatie (User)
3. Webshop (Product, ProductVariant, Order, OrderLine)
4. Tickets (TicketWedstrijd, TicketType, TicketLijn) - via dezelfde
   winkelmand/Order als de webshop
5. Acties met afhaling (Actie, ActieArtikel, ActieVariant, AfhaalMoment,
   ActieLijn) - eveneens via dezelfde winkelmand/Order

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

    # Prestatiebadges op de Dames/Heren-overzichtspagina's (zie
    # templates/_team_macros.html:team_achievements()) - per team anders,
    # dus geen vaste tekst maar hier bewerkbaar. None = nog niet ingevuld
    # (toont "X" i.p.v. een echt getal); aantal_europese_wedstrijden=None
    # laat die badge bovendien helemaal weg (niet elk team heeft Europees
    # gespeeld).
    aantal_bekers = db.Column(db.Integer)
    aantal_landstitels = db.Column(db.Integer)
    aantal_europese_wedstrijden = db.Column(db.Integer)

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


class Evenement(db.Model):
    """Los van de Spond-kalender-embed (die biedt geen koppelbare/openbare API) -
    voor het 'Volgende event'-blokje naast 'Laatste nieuws' op de homepage.
    Volgorde is altijd chronologisch (datum), geen handmatige position zoals
    bij NieuwsBericht - zie main.home (enkel toekomstige events, op datum)."""
    __tablename__ = "evenementen"

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(200), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    tekst = db.Column(db.Text, nullable=False)
    # Optioneel: enkel ingevuld als een admin het meegeeft. Wordt gebruikt
    # voor de Event-structured data (zie templates/index.html) - zonder
    # locatie laten we die er bewust uit, in plaats van een adres te
    # verzinnen dat voor een extern tornooi toch niet klopt.
    locatie = db.Column(db.String(255))

    def __repr__(self):
        return f"<Evenement {self.titel} ({self.datum})>"


class Sponsor(db.Model):
    """Een sponsor: de eerste 2 (actief, op volgorde) in de header, alle actieve in de footer."""
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(150), nullable=False)
    logo = db.Column(db.String(255), nullable=False)   # bestandsnaam in static/images/
    website_url = db.Column(db.String(500))
    position = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Sponsor {self.naam}>"


class Affiche(db.Model):
    """Een liggende affiche bovenaan de homepage, bv. voor een actie of een
    tornooi. Zichtbaar zolang ze actief is en binnen haar periode valt; zijn
    er meerdere tegelijk zichtbaar, dan wisselen ze af in een slider (op
    volgorde van position)."""
    __tablename__ = "affiches"

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(200), nullable=False)          # enkel voor de admin
    afbeelding = db.Column(db.String(255), nullable=False)     # liggend, bestandsnaam in static/images/
    # Optionele staande/vierkante versie voor smalle schermen - een liggende
    # affiche wordt op een gsm zo klein dat de tekst onleesbaar wordt.
    afbeelding_gsm = db.Column(db.String(255))
    alt_tekst = db.Column(db.String(500), nullable=False)      # wat er op de affiche staat (schermlezers, Google)
    link = db.Column(db.String(500))                           # optioneel: relatief pad of http(s)-URL
    # Leeg = meteen zichtbaar / zichtbaar tot de admin ze deactiveert.
    # Belgische lokale tijd, zoals de rest van de site.
    toon_vanaf = db.Column(db.DateTime, nullable=True)
    toon_tot = db.Column(db.DateTime, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        """'Inactief', 'Gepland', 'Verlopen' of 'Zichtbaar'."""
        nu = nu_belgisch()
        if not self.is_active:
            return "Inactief"
        if self.toon_vanaf is not None and self.toon_vanaf > nu:
            return "Gepland"
        if self.toon_tot is not None and self.toon_tot <= nu:
            return "Verlopen"
        return "Zichtbaar"

    @property
    def is_zichtbaar(self):
        return self.status == "Zichtbaar"

    @property
    def link_is_extern(self):
        return bool(self.link) and not self.link.startswith("/")

    def __repr__(self):
        return f"<Affiche {self.titel}>"


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

    # Of een admin deze inschrijving al heeft afgehandeld (bv. speler
    # ingeschreven bij de bond, ouders gecontacteerd, ...) - zelfde patroon
    # als VergeetMijVerzoek.verwerkt hieronder.
    verwerkt = db.Column(db.Boolean, nullable=False, default=False)
    # Interne notitie, enkel zichtbaar voor admins (bv. "gebeld op 17/10")
    notitie = db.Column(db.Text)

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
    notitie = db.Column(db.Text)   # interne notitie, enkel voor admins
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
    # Korte omschrijving (~155 tekens) voor de meta-description/og:description
    # van deze pagina - zie templates/pages/view.html. Leeg = generieke
    # sitebrede fallback (zie base.html).
    meta_description = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    blocks = db.relationship(
        "PageBlock", order_by="PageBlock.position", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Page {self.slug}>"


PAGE_BLOCK_TYPES = [
    "rich_text", "image_gallery", "columns", "video", "button",
    "quote", "faq", "stats", "embed_html",
]


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


class SiteInstelling(db.Model):
    """
    Site-brede aan/uit-instellingen: de onderhoudsmodus en de webshop
    (zie utils/site_settings.py). Eén rij (singleton), lazy aangemaakt bij
    de eerste aanvraag - zelfde aanpak als SiteText hierboven.
    """
    __tablename__ = "site_instellingen"

    id = db.Column(db.Integer, primary_key=True)
    onderhoudsmodus_actief = db.Column(db.Boolean, default=False, nullable=False)
    # Standaard True: de webshop is normaal gewoon open, dit is enkel om ze
    # bewust dicht te zetten (bv. tijdens de zomerstop).
    webshop_actief = db.Column(db.Boolean, default=True, nullable=False)
    # Wanneer de adminhandleiding-PDF (static/documents/handleiding.pdf) voor
    # het laatst geüpload is - None zolang er nog nooit één geüpload is.
    handleiding_bijgewerkt_op = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<SiteInstelling onderhoudsmodus_actief={self.onderhoudsmodus_actief} "
            f"webshop_actief={self.webshop_actief}>"
        )


class ChangelogEntry(db.Model):
    """Eén item in het door de admin bijgehouden wijzigingslogboek ('wat heb
    ik toegevoegd aan de site'), zie routes/admin.py: changelog(). Losstaand
    van AuditLog hierboven: dat logt automatisch élke admin-actie, dit is een
    handmatig, vrij te formuleren overzicht voor de eigenaar zelf."""
    __tablename__ = "changelog_entries"

    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    beschrijving = db.Column(db.Text, nullable=False)
    aangemaakt_op = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ChangelogEntry {self.datum}: {self.beschrijving[:40]}>"


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
# Auditlog
# ---------------------------------------------------------------------------

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    actor_name = db.Column(db.String(200), nullable=False)

    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.actor_name}>"


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

# Order.payment_status zoals Stripe/de checkout ze zet, met hun weergavenaam in de admin
BETAALSTATUS_LABELS = {"Pending": "Openstaand", "paid": "Betaald", "failed": "Mislukt"}


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)          # subtotaal producten + tickets + acties, excl. verzending
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="Pending", nullable=False)
    order_status = db.Column(db.String(30), default="Ontvangen", nullable=False)
    # Door Stripe gevraagd als de bestelling actieartikelen (afhaling) bevat,
    # zodat de club kan bellen als er iets misloopt. Snapshot op de
    # bestelling, niet op het account.
    telefoon = db.Column(db.String(30), nullable=True)
    # Uit de standaardlijst van bestellingen gehaald door een admin (bv.
    # afgewerkt). Niets wordt verwijderd: met een filter blijven ze zichtbaar.
    gearchiveerd = db.Column(db.Boolean, nullable=False, default=False)

    lines = db.relationship(
        "OrderLine", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    ticket_lines = db.relationship(
        "TicketLijn", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    actie_lines = db.relationship(
        "ActieLijn", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    actie_opmerkingen = db.relationship(
        "ActieOpmerking", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    def actie_opmerking(self, actie):
        """Wat de koper invulde in het opmerkingenveld van deze actie, of None."""
        return next((o.tekst for o in self.actie_opmerkingen if o.actie_id == actie.id), None)

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


# ---------------------------------------------------------------------------
# Tickets voor wedstrijden (onderdeel van de webshop)
# ---------------------------------------------------------------------------

# Bestellingen met deze status tellen niet (meer) mee voor verkochte tickets
# of de naamlijst - zelfde principe als de voorraad die bij annulatie
# teruggeboekt wordt.
TICKET_ONGELDIGE_ORDER_STATUSSEN = ["Geannuleerd", "Terugbetaald"]


def nu_belgisch():
    """Huidige Belgische lokale tijd als naive datetime - zelfde vorm als
    TicketWedstrijd.datum_tijd (die een admin in lokale tijd invult)."""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("Europe/Brussels")).replace(tzinfo=None)


class TicketWedstrijd(db.Model):
    """Een wedstrijd waarvoor tickets verkocht worden. Los van de Spond-
    kalender (die geen koppelbare API heeft) - een admin maakt ze zelf aan.
    Net als producten nooit verwijderd zodra er tickets voor verkocht zijn,
    enkel actief/inactief gezet."""
    __tablename__ = "ticket_wedstrijden"

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(200), nullable=False)          # bv. "Heren 1 - HC Tongeren"
    datum_tijd = db.Column(db.DateTime, nullable=False)          # aanvangsuur, Belgische lokale tijd
    locatie = db.Column(db.String(255))
    omschrijving = db.Column(db.Text)
    # Leeg = geen limiet. Anders het maximum aantal tickets over alle
    # tickettypes samen (bv. de capaciteit van de tribune).
    max_tickets = db.Column(db.Integer, nullable=True)
    # Leeg = geen limiet. Anders het maximum aantal tickets (alle types
    # samen) dat één klant in één bestelling voor deze wedstrijd koopt.
    max_per_bestelling = db.Column(db.Integer, nullable=True)
    # Leeg = de verkoop sluit bij de aanvang. Anders het moment (Belgische
    # lokale tijd, net als datum_tijd) waarop de online verkoop eerder sluit.
    verkoop_einde = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket_types = db.relationship(
        "TicketType", backref="wedstrijd", lazy=True, cascade="all, delete-orphan",
        order_by="TicketType.id",
    )

    @property
    def actieve_ticket_types(self):
        return [t for t in self.ticket_types if t.is_active]

    @property
    def verkoop_sluit_op(self):
        """De ingestelde einddatum van de verkoop, of anders de aanvang."""
        return self.verkoop_einde or self.datum_tijd

    @property
    def verkoop_gesloten(self):
        """De verkoop sluit automatisch op verkoop_sluit_op."""
        return self.verkoop_sluit_op <= nu_belgisch()

    def aantal_verkocht(self):
        """Tickets in bestellingen die (nog) niet mislukt/geannuleerd zijn.
        Bewust incl. bestellingen die nog op betaling wachten: die houden hun
        plaatsen vast, net zoals de voorraad bij producten al bij het
        afrekenen afgeschreven wordt. Mislukt/verloopt de betaling, dan
        telt de bestelling vanzelf niet meer mee (payment_status 'failed')."""
        totaal = (
            db.session.query(db.func.coalesce(db.func.sum(TicketLijn.quantity), 0))
            .join(Order, TicketLijn.order_id == Order.order_id)
            .join(TicketType, TicketLijn.ticket_type_id == TicketType.id)
            .filter(
                TicketType.wedstrijd_id == self.id,
                Order.payment_status != "failed",
                Order.order_status.notin_(TICKET_ONGELDIGE_ORDER_STATUSSEN),
            )
            .scalar()
        )
        return int(totaal or 0)

    def aantal_beschikbaar(self):
        """None = onbeperkt."""
        if self.max_tickets is None:
            return None
        return max(0, self.max_tickets - self.aantal_verkocht())

    @property
    def is_koopbaar(self):
        return self.is_active and not self.verkoop_gesloten and bool(self.actieve_ticket_types)

    def __repr__(self):
        return f"<TicketWedstrijd {self.titel} ({self.datum_tijd})>"


class TicketType(db.Model):
    """Soort ticket voor een wedstrijd, bv. 'Volwassene' of 'Kind -12', elk
    met een eigen prijs. Zelfde principe als ProductVariant: nooit
    verwijderd, enkel gedeactiveerd, omdat ticketregels ernaar verwijzen."""
    __tablename__ = "ticket_types"

    id = db.Column(db.Integer, primary_key=True)
    wedstrijd_id = db.Column(db.Integer, db.ForeignKey("ticket_wedstrijden.id"), nullable=False)
    naam = db.Column(db.String(100), nullable=False)
    prijs = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<TicketType {self.naam} ({self.wedstrijd_id})>"


class TicketLijn(db.Model):
    """Ticketregel in een bestelling - de tegenhanger van OrderLine voor
    tickets. Aparte tabel i.p.v. OrderLine uitbreiden: OrderLine.product_id
    is verplicht, en die kolom nullable maken vraagt op sqlite een volledige
    tabel-herbouw."""
    __tablename__ = "order_ticket_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey("ticket_types.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)   # prijs per ticket, bevroren bij bestellen

    ticket_type = db.relationship("TicketType")

    @property
    def wedstrijd(self):
        return self.ticket_type.wedstrijd

    @property
    def subtotal(self):
        return self.quantity * float(self.price)


# ---------------------------------------------------------------------------
# Acties: verkoop met afhaling (bv. afhaalgerechten, wafelverkoop) - via
# dezelfde winkelmand/Order als de webshop
# ---------------------------------------------------------------------------

# De 14 allergenen die volgens de EU-regelgeving vermeld moeten worden.
ALLERGENEN = [
    ("gluten", "Gluten"),
    ("schaaldieren", "Schaaldieren"),
    ("eieren", "Eieren"),
    ("vis", "Vis"),
    ("pindas", "Pinda's"),
    ("soja", "Soja"),
    ("melk", "Melk"),
    ("noten", "Noten"),
    ("selder", "Selder"),
    ("mosterd", "Mosterd"),
    ("sesam", "Sesamzaad"),
    ("sulfiet", "Sulfiet"),
    ("lupine", "Lupine"),
    ("weekdieren", "Weekdieren"),
]
ALLERGEEN_SLEUTELS = {sleutel for sleutel, _ in ALLERGENEN}

WEEKDAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]


class Actie(db.Model):
    """Een verkoopactie met afhaling, bv. "Europese droom - afhaalgerechten".
    Een actie heeft artikelen (met varianten) en afhaalmomenten; de koper
    kiest per actie één afhaalmoment voor alles wat hij bij die actie
    bestelt. Net als producten en wedstrijden nooit verwijderd zodra er
    bestellingen aan hangen, enkel actief/inactief gezet."""
    __tablename__ = "acties"

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(200), nullable=False)
    omschrijving = db.Column(db.Text)
    afbeelding = db.Column(db.String(255))   # bestandsnaam in static/images/
    # Wordt ingevuld als adres bij een nieuw afhaalmoment; elk moment heeft
    # daarna zijn eigen adres.
    standaard_adres = db.Column(db.String(255))
    # Leeg = geen deadline voor de hele actie. Anders het moment (Belgische
    # lokale tijd) waarop bestellen voor alle afhaalmomenten sluit. Een
    # afhaalmoment kan daarbovenop een eigen, vroegere deadline hebben.
    bestellen_tot = db.Column(db.DateTime, nullable=True)
    # Titel van het vrije tekstveld onderaan het actieformulier, bv.
    # "Opmerking/Aanmoediging". Leeg = "Opmerking" (zie opmerking_titel).
    opmerking_label = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    artikelen = db.relationship(
        "ActieArtikel", backref="actie", lazy=True, cascade="all, delete-orphan",
        order_by="(ActieArtikel.position, ActieArtikel.id)",
    )
    momenten = db.relationship(
        "AfhaalMoment", backref="actie", lazy=True, cascade="all, delete-orphan",
        order_by="AfhaalMoment.start",
    )

    @property
    def opmerking_titel(self):
        return self.opmerking_label or "Opmerking"

    @property
    def actieve_artikelen(self):
        """Artikelen die te koop zijn: actief en met minstens één actieve variant."""
        return [a for a in self.artikelen if a.is_active and a.actieve_varianten]

    @property
    def actieve_momenten(self):
        return [m for m in self.momenten if m.is_active]

    @property
    def bestelbare_momenten(self):
        return [m for m in self.actieve_momenten if m.is_bestelbaar]

    @property
    def laatste_einde(self):
        """Einde van het laatste actieve afhaalmoment, of None."""
        return max((m.einde for m in self.actieve_momenten), default=None)

    @property
    def is_zichtbaar(self):
        """Een actie staat in de shop tot het laatste afhaalmoment voorbij
        is - ook als bestellen al gesloten is (dan met die melding)."""
        return self.is_active and self.laatste_einde is not None and self.laatste_einde > nu_belgisch()

    @property
    def is_uitverkocht(self):
        varianten = [v for a in self.actieve_artikelen for v in a.actieve_varianten]
        return bool(varianten) and all(v.aantal_beschikbaar() == 0 for v in varianten)

    @property
    def is_bestelbaar(self):
        return (
            self.is_active and bool(self.actieve_artikelen) and bool(self.bestelbare_momenten)
            and not self.is_uitverkocht
        )

    @property
    def laagste_prijs(self):
        return min((v.prijs for a in self.actieve_artikelen for v in a.actieve_varianten), default=None)

    def heeft_bestellingen(self):
        return (
            ActieLijn.query.join(AfhaalMoment, ActieLijn.moment_id == AfhaalMoment.id)
            .filter(AfhaalMoment.actie_id == self.id).first() is not None
        )

    def __repr__(self):
        return f"<Actie {self.titel}>"


class ActieArtikel(db.Model):
    """Iets dat binnen een actie verkocht wordt, bv. een gerecht. Prijs en
    voorraad zitten op de varianten (bv. klein/groot), zodat een artikel
    met maar één soort gewoon één variant zonder naam heeft."""
    __tablename__ = "actie_artikelen"

    id = db.Column(db.Integer, primary_key=True)
    actie_id = db.Column(db.Integer, db.ForeignKey("acties.id"), nullable=False)
    naam = db.Column(db.String(200), nullable=False)
    omschrijving = db.Column(db.Text)
    afbeelding = db.Column(db.String(255))   # bestandsnaam in static/images/
    allergenen = db.Column(db.JSON, nullable=False, default=list)   # sleutels uit ALLERGENEN
    # Leeg = geen limiet. Anders het maximum aantal stuks (alle varianten
    # samen) van dit artikel in één bestelling.
    max_per_bestelling = db.Column(db.Integer, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=0)   # weergavevolgorde binnen de actie
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    varianten = db.relationship(
        "ActieVariant", backref="artikel", lazy=True, cascade="all, delete-orphan",
        order_by="ActieVariant.id",
    )

    @property
    def actieve_varianten(self):
        return [v for v in self.varianten if v.is_active]

    @property
    def allergeen_labels(self):
        """Labels in de vaste volgorde van ALLERGENEN."""
        gekozen = set(self.allergenen or [])
        return [label for sleutel, label in ALLERGENEN if sleutel in gekozen]

    def heeft_bestellingen(self):
        return (
            ActieLijn.query.join(ActieVariant, ActieLijn.variant_id == ActieVariant.id)
            .filter(ActieVariant.artikel_id == self.id).first() is not None
        )

    def __repr__(self):
        return f"<ActieArtikel {self.naam} ({self.actie_id})>"


class ActieVariant(db.Model):
    """Variant van een artikel met eigen prijs en voorraad, bv. 'Groot' of
    'Vegetarisch'. Zelfde principe als ProductVariant: nooit verwijderd
    zodra er bestellingen naar verwijzen, enkel gedeactiveerd."""
    __tablename__ = "actie_varianten"

    id = db.Column(db.Integer, primary_key=True)
    artikel_id = db.Column(db.Integer, db.ForeignKey("actie_artikelen.id"), nullable=False)
    naam = db.Column(db.String(100))   # leeg bij een artikel met maar één variant
    prijs = db.Column(db.Float, nullable=False)
    # Leeg = onbeperkt. Anders het totaal aantal stuks dat over de hele
    # actie verkocht kan worden. Geen teller die afgeschreven wordt: zie
    # aantal_verkocht().
    voorraad = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def volledige_naam(self):
        return f"{self.artikel.naam} ({self.naam})" if self.naam else self.artikel.naam

    def aantal_verkocht(self):
        """Zelfde principe als TicketWedstrijd.aantal_verkocht(): regels in
        bestellingen die niet mislukt/geannuleerd zijn, incl. bestellingen
        die nog op betaling wachten. Mislukt of verloopt de betaling, of
        wordt de bestelling geannuleerd, dan komt de voorraad vanzelf vrij."""
        totaal = (
            db.session.query(db.func.coalesce(db.func.sum(ActieLijn.quantity), 0))
            .join(Order, ActieLijn.order_id == Order.order_id)
            .filter(
                ActieLijn.variant_id == self.id,
                Order.payment_status != "failed",
                Order.order_status.notin_(TICKET_ONGELDIGE_ORDER_STATUSSEN),
            )
            .scalar()
        )
        return int(totaal or 0)

    def aantal_beschikbaar(self):
        """None = onbeperkt."""
        if self.voorraad is None:
            return None
        return max(0, self.voorraad - self.aantal_verkocht())

    def heeft_bestellingen(self):
        return ActieLijn.query.filter_by(variant_id=self.id).first() is not None

    def __repr__(self):
        return f"<ActieVariant {self.naam} ({self.artikel_id})>"


class AfhaalMoment(db.Model):
    """Een moment waarop bestellingen van een actie afgehaald worden: een
    datum met tijdvenster en een adres. Tijden in Belgische lokale tijd,
    zoals TicketWedstrijd.datum_tijd."""
    __tablename__ = "afhaalmomenten"

    id = db.Column(db.Integer, primary_key=True)
    actie_id = db.Column(db.Integer, db.ForeignKey("acties.id"), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    einde = db.Column(db.DateTime, nullable=False)
    adres = db.Column(db.String(255), nullable=False)
    # Leeg = enkel de deadline van de actie (of anders de start van dit
    # moment) geldt. Anders een eigen deadline voor dit moment.
    bestellen_tot = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def bestellen_sluit_op(self):
        """De vroegste van: deadline van de actie, eigen deadline, start."""
        return min(d for d in (self.actie.bestellen_tot, self.bestellen_tot, self.start) if d is not None)

    @property
    def is_bestelbaar(self):
        return self.is_active and self.bestellen_sluit_op > nu_belgisch()

    @property
    def label(self):
        """bv. 'zaterdag 14/11/2026 van 11:00 tot 14:00'"""
        return (
            f"{WEEKDAGEN[self.start.weekday()]} {self.start.strftime('%d/%m/%Y')} "
            f"van {self.start.strftime('%H:%M')} tot {self.einde.strftime('%H:%M')}"
        )

    def heeft_bestellingen(self):
        return ActieLijn.query.filter_by(moment_id=self.id).first() is not None

    def __repr__(self):
        return f"<AfhaalMoment {self.start} ({self.actie_id})>"


class ActieLijn(db.Model):
    """Actieregel in een bestelling - de tegenhanger van OrderLine/TicketLijn
    voor acties. Het afhaalmoment staat per regel; alle regels van dezelfde
    actie in één bestelling hebben hetzelfde moment (zie routes/shop.py en
    admin.update_order_afhaalmoment)."""
    __tablename__ = "order_actie_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("actie_varianten.id"), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey("afhaalmomenten.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)   # prijs per stuk, bevroren bij bestellen

    variant = db.relationship("ActieVariant")
    moment = db.relationship("AfhaalMoment")

    @property
    def actie(self):
        return self.moment.actie

    @property
    def subtotal(self):
        return self.quantity * float(self.price)


# Maximumlengte van een opmerking bij een actie (formulier en controle)
ACTIE_OPMERKING_MAX = 500


class ActieOpmerking(db.Model):
    """Wat de koper in het opmerkingenveld van een actie invulde (bv. een
    allergie of een aanmoediging voor de ploeg). Eén per actie per
    bestelling; enkel aangemaakt als er iets ingevuld is."""
    __tablename__ = "order_actie_opmerkingen"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    actie_id = db.Column(db.Integer, db.ForeignKey("acties.id"), nullable=False)
    tekst = db.Column(db.Text, nullable=False)

    actie = db.relationship("Actie")


def actie_lijnen_per_moment(lijnen):
    """Groepeert actieregels per afhaalmoment (en dus per actie),
    chronologisch, met de regels in de volgorde van de artikelen - zo tonen
    bevestigingsmail, bedankpagina en admin ze."""
    groepen = {}
    for lijn in lijnen:
        groepen.setdefault(lijn.moment, []).append(lijn)
    for groep in groepen.values():
        groep.sort(key=lambda l: (l.variant.artikel.position, l.variant.artikel_id, l.variant_id))
    return [(moment, groepen[moment]) for moment in sorted(groepen, key=lambda m: m.start)]
