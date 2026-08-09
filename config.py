"""
config.py
---------
Alle instellingen voor de Flask-app staan hier gebundeld, zodat je nooit
gevoelige gegevens (zoals een secret key of database-wachtwoord) hardcoded
in je code hoeft te zetten. Instellingen worden uit omgevingsvariabelen
gehaald (.env-bestand), met een veilige standaardwaarde voor development.
"""

import os
from dotenv import load_dotenv

# Laad variabelen uit een .env-bestand in de projectroot (indien aanwezig)
load_dotenv()

# Basisdirectory van het project, handig voor bestandspaden
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Instellingen die in elke omgeving gelden."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "verander-deze-sleutel-in-productie")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe (webshop betalingen)
    STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
    # ID van de 'Verzendingskosten' shipping rate in Stripe. Test- en live-mode
    # zijn gescheiden datasets met elk hun eigen ID - bij overschakelen naar
    # live mode dit ID in .env aanpassen, code hoeft niet te veranderen.
    STRIPE_SHIPPING_RATE_ID = os.environ.get("STRIPE_SHIPPING_RATE_ID")

    # Webshop-instellingen
    FREE_SHIPPING_THRESHOLD = 50.0   # gratis verzending vanaf dit subtotaal (excl. verzendkosten zelf)
    PRINTING_COST_PER_SIDE = 5.0     # extra kost per bedrukte zijde (voor- en/of achterkant)

    # Spond-wedstrijdenkalender, ingebed als iframe op /kalender/wedstrijden.
    # Nog aan te vullen met de echte embed-URL van jullie Spond-groep.
    # 'or' i.p.v. .get(..., default): zo valt een lege waarde in .env
    # (SPOND_EMBED_URL= zonder waarde erachter) ook terug op de placeholder,
    # in plaats van een lege iframe-src te geven.
    SPOND_EMBED_URL = os.environ.get("SPOND_EMBED_URL") or "https://spond.com/"

    # Flanders Trophy: puur doorlinken, geen eigen pagina's op deze site
    FLANDERS_TROPHY_FACEBOOK_URL = "https://www.facebook.com/"
    FLANDERS_TROPHY_INSTAGRAM_URL = "https://www.instagram.com/"
    FLANDERS_TROPHY_WEBSITE_URL = "https://www.flanderstrophy.be"

    # Mail (contactformulier + orderbevestiging)
    GMAIL_USER = os.environ.get("GMAIL_USER")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

    # Upload-map voor geüploade afbeeldingen: productfoto's, pagina-
    # hero-afbeeldingen en inline afbeeldingen in de pagina-editor
    # (relatief aan static/)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024   # 8 MB, voorkomt te grote uploads


class DevelopmentConfig(Config):
    """Instellingen voor lokaal ontwikkelen."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'handbalclub.db')}"
    )


def _normalize_database_url(url):
    """Sommige hosts (bv. oudere Heroku-achtige styleconventies) geven 'postgres://'
    terug, maar SQLAlchemy 1.4+ vereist het volledige 'postgresql://'-schema."""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class ProductionConfig(Config):
    """Instellingen voor de live-omgeving (bv. Render, Hetzner)."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get("DATABASE_URL"))


# Maak het eenvoudig om per omgeving de juiste config te kiezen
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
