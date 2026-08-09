# HC Sint-Truiden - Website + Webshop

Flask-project voor de handbalclub, met geïntegreerde webshop (SQLAlchemy,
bedrukkingsopties, gratis verzending, bestelstatussen).

## Projectstructuur

```
handbalclub/
├── app.py              # Application factory
├── run.py              # Startpunt voor lokale development
├── config.py            # Instellingen (dev/productie, Stripe, mail, webshop-constantes)
├── extensions.py         # db, csrf, limiter - centraal geïnitialiseerd
├── models.py              # Alle SQLAlchemy-modellen (club + webshop + CMS: Page, NavItem)
├── routes/
│   ├── main.py             # Home, teams, nieuws, over ons, contact (publiek)
│   ├── auth.py               # Login, registratie, profiel, accountinstellingen
│   ├── shop.py                 # Producten, winkelmandje, Stripe checkout + webhook
│   ├── pages.py                  # Publieke weergave van CMS-pagina's: /pagina/<slug>
│   └── admin.py                    # Adminpaneel: producten/gebruikers/bestellingen/
│                                      pagina's/navigatie
├── utils/
│   ├── auth.py                   # @login_required / @admin_required decorators
│   ├── mail.py                     # Contactmail, orderbevestiging, annulatiemelding
│   ├── sanitize.py                   # Saniteert rich-text HTML (bleach) vóór opslag
│   └── nav.py                          # Bouwt de navbar-boom op uit NavItem's
├── scripts/
│   ├── seed_pages.py                     # Eenmalige migratie: placeholder-pagina's -> Page
│   └── seed_nav.py                         # Eenmalige migratie: hardcoded navbar -> NavItem
├── templates/                       # Jinja2-templates, publieke kant via base.html
│   ├── base.html                     # Gedeelde publieke layout (header/nav/footer),
│   │                                    navbar wordt gerenderd uit nav_tree (zie utils/nav.py)
│   ├── pages/view.html                 # Generieke weergave van een CMS-pagina
│   ├── admin/                            # Adminomgeving, eigen sidebar-shell (niet de
│   │                                        publieke header/footer)
│   │   ├── _shell.html                       # Sidebar-layout, door alle adminpagina's
│   │   │                                        geëxtend
│   │   ├── pages_list.html / page_form.html    # Pagina's beheren (incl. Quill-editor)
│   │   └── navigation.html / _nav_item.html      # Navigatie beheren (boom + drag-and-drop)
│   ├── shop/                           # Webshop-templates
│   └── ... (main, auth, admin templates)
├── static/
│   ├── style.css                        # Sitebrede stylesheet (HBST-huisstijl)
│   ├── images/                           # Product-, pagina- en overige afbeeldingen
│   └── vendor/                            # Self-hosted front-end libs (geen CDN/build-stap)
│       ├── quill/                            # Rich-text editor voor pagina's
│       └── sortablejs/                         # Drag-and-drop voor navigatiebeheer
├── instance/                              # SQLite-database (niet in git)
├── requirements.txt
└── .env.example                           # Kopieer naar .env, vul zelf in
```

## Webshop-functionaliteit

- **Varianten** (kleur/maat) per product, elk met eigen prijs en voorraad.
- **Bedrukking**: optioneel per winkelmandje-regel een voor-/achterkant-tekst
  (+€5 per bedrukte zijde), enkel beschikbaar als het product dit toelaat.
- **Gratis verzending** vanaf €50 subtotaal; anders wordt de Stripe shipping
  rate (`STRIPE_SHIPPING_RATE_ID`) toegevoegd aan de Checkout Session.
- **Producten/varianten worden nooit verwijderd**, enkel geactiveerd/
  gedeactiveerd — bestaande bestellingen blijven zo altijd correct
  verwijzen naar hun product/variant (kleur, maat, prijs op moment van
  bestellen).
- **Bestelstatussen** (Ontvangen / In behandeling / Klaar voor verzending /
  Verzonden / Geannuleerd / Terugbetaald), beheerbaar in het adminpaneel.
  Bij annuleren wordt de voorraad automatisch teruggeboekt en gaat er een
  meldingsmail naar de clubmail.
- **Publiek vs. achter login**: home/teams/nieuws/over ons/contact zijn
  publiek; winkelmandje, afrekenen, profiel en admin vereisen een login.

## Sitestructuur

Naast de webshop (FanShop) is de volledige sitemap nu aanwezig. Twee
soorten pagina's:

- **Code-gedreven** (blijven vaste Flask-routes/templates): shop, login/
  profiel, contactformulier, jeugd-inschrijvingsformulier, teampagina's
  (`routes/dames.py` / `routes/heren.py`, data uit het `Team`-model via
  slug + sectie 'dames'/'heren'), Wedstrijden (Spond-iframe).
- **CMS-beheerd** (via de admin, zie hieronder): de informatieve
  pagina's onder Club/Kalender/Jeugd/FIT-Handbal/G-Handbal/Vacatures
  (Missie & Visie, Bestuur, Historiek, Verzekering, API's,
  leeftijdscategorieën, Trainingen, Evenementen, ...). Hun oude routes
  (bv. `routes/club.py`, `routes/jeugd.py`) blijven bestaan als
  permanente 301-redirect naar de nieuwe `/pagina/<slug>`-URL, zodat
  bestaande links/bookmarks blijven werken.

## Content- en navigatiebeheer (admin-CMS)

Admins (gebruikers met `is_admin=True`) beheren de volledige site vanuit
één omgeving op `/admin`:

- **Pagina's** (`/admin/pages`): aanmaken, bewerken (met een rich-text
  editor, incl. afbeeldingen), publiceren/depubliceren en verwijderen.
  Inhoud wordt bij opslaan altijd server-side gesaniteerd (`utils/
  sanitize.py`, via `bleach`) voor er `| safe` gerenderd wordt - ook al
  kunnen enkel admins pagina's schrijven, dit is een extra
  veiligheidslaag tegen stored-XSS.
- **Navigatie** (`/admin/navigation`): de volledige navbar (categorieën,
  groepslabels, items) is data (`NavItem`, zelf-refererende boom) i.p.v.
  hardcoded in `templates/base.html`. Items toevoegen/hernoemen/
  verwijderen, herordenen (▲/▼ of slepen) en verplaatsen tussen
  categorieën (select of slepen) - inclusief items die naar een vaste
  route (bv. de shop) of een externe URL linken, niet enkel naar
  CMS-pagina's.

Het Profiel/Inloggen-blok en het winkelmandje-icoon in de navbar blijven
bewust hardcoded in `base.html` (hun doel hangt af van de actieve sessie/
blueprint, niet van beheerde content).

`scripts/seed_pages.py` en `scripts/seed_nav.py` zijn de eenmalige
migratiescripts die de oorspronkelijke hardcoded pagina's/navbar naar
`Page`/`NavItem`-rijen omgezet hebben; ze zijn idempotent (opnieuw draaien
overschrijft bestaande rijen met dezelfde slug/structuur) maar normaal
gezien niet meer nodig na de eerste keer.

Nog te bouwen in een volgende fase:
- Het GDPR "vergeet mij"-formulier - momenteel een aankondigingspagina
- De homepage met nieuwscategorieën (Club/Dames/Heren/Jeugd), sponsorbalk
  en Spond-widget
- De echte Spond embed-URL invullen in `.env` (`SPOND_EMBED_URL`)
- De placeholder-tekst in de gemigreerde CMS-pagina's (bestuursleden,
  missietekst, historiek, ...) vervangen door de echte inhoud - dit kan nu
  rechtstreeks via `/admin/pages`, niet meer door templates te bewerken

## Lokaal opstarten

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # vul je eigen Stripe/Gmail-gegevens in
python run.py
```

Site draait dan op **http://127.0.0.1:5000**

## Voorbeelddata toevoegen (via Flask shell)

```bash
flask shell
```
```python
from extensions import db
from models import User, Product, ProductVariant

admin = User(first_name="Admin", last_name="User", username="admin", email="admin@club.be", is_admin=True)
admin.set_password("EenSterkWachtwoord1!")
db.session.add(admin)

p = Product(product_name="Clubtrui", description="Officiële clubtrui", printing_available=True)
db.session.add(p)
db.session.commit()

db.session.add(ProductVariant(product_id=p.product_id, color="Blauw", size="M", price=29.99, stock=20))
db.session.commit()
```

## Stripe-instellingen

Voor de webshop heb je in je Stripe dashboard nodig:
- Een **API key** (`STRIPE_API_KEY`)
- Een **webhook endpoint** op `/webhook`, met bijhorend **signing secret**
  (`STRIPE_WEBHOOK_SECRET`)
- Een **shipping rate** genaamd "Verzendingskosten" — kopieer het ID
  (`shr_...`) naar `STRIPE_SHIPPING_RATE_ID`

Test- en live-mode zijn gescheiden Stripe-omgevingen met elk hun eigen ID's:
bij overschakelen naar live mode enkel de `.env`-waarden aanpassen.

## Volgende stappen

- Flask-Migrate voor nette databasemigraties i.p.v. `db.create_all()`
- Aparte Flask-app/blueprint voor de toernooiwebsite
- Deployment op Hetzner (Cloud VPS aanbevolen, zoals eerder besproken)
- Optioneel, buiten scope van de huidige admin-CMS: versiegeschiedenis
  voor pagina's, granulaire adminrollen (vandaag enkel de ene
  `is_admin`-vlag), rich-text-beheer voor `Team.omschrijving`
