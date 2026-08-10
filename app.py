"""
app.py
------
Dit is het hart van de applicatie. Hier wordt de Flask-app aangemaakt via
een "application factory" (de functie create_app). Dat patroon zorgt ervoor
dat je later makkelijk kan testen, meerdere configuraties kan gebruiken,
en de app in kleinere, overzichtelijke stukken (blueprints) kan opdelen.

Starten voor development doe je via run.py, niet via dit bestand direct.
"""

from flask import Flask, render_template

from config import config_by_name
from extensions import db, csrf, limiter


def create_app(config_name="development"):
    """Bouwt en configureert een Flask-app en geeft die terug."""

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Extensies koppelen aan de app
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Blueprints registreren: dit "plakt" de routes uit routes/*.py
    # aan de app vast.
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.shop import shop_bp
    from routes.admin import admin_bp
    from routes.pages import pages_bp
    from routes.club import club_bp
    from routes.kalender import kalender_bp
    from routes.dames import dames_bp
    from routes.heren import heren_bp
    from routes.jeugd import jeugd_bp
    from routes.ghandbal import ghandbal_bp
    from routes.fithandbal import fithandbal_bp
    from routes.vacatures import vacatures_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(club_bp)
    app.register_blueprint(kalender_bp)
    app.register_blueprint(dames_bp)
    app.register_blueprint(heren_bp)
    app.register_blueprint(jeugd_bp)
    app.register_blueprint(ghandbal_bp)
    app.register_blueprint(fithandbal_bp)
    app.register_blueprint(vacatures_bp)

    # Zorgt dat de database-tabellen bestaan (handig in development;
    # voor productie gebruik je later beter Flask-Migrate).
    with app.app_context():
        db.create_all()

    # Stelt de navbar-boom (NavItem's) beschikbaar in elke template, zodat
    # base.html de navigatie kan renderen zonder dat elke route dit zelf
    # moet meegeven.
    from utils.nav import build_nav_tree

    @app.context_processor
    def inject_nav_tree():
        return {"nav_tree": build_nav_tree()}

    # Stelt de admin-bewerkbare hero-teksten (SiteText) beschikbaar in elke
    # template, met dezelfde context-processor-aanpak als de navbar hierboven.
    from utils.site_text import get_site_teksten

    @app.context_processor
    def inject_site_teksten():
        return {"site_teksten": get_site_teksten()}

    # Eigen foutpagina's i.p.v. Flask/Werkzeug's kale standaardpagina's:
    # 404 (onbestaande URL) en 429 (rate limit overschreden, bv. te vaak
    # inloggen na elkaar - zie @limiter.limit(...) in routes/auth.py).
    @app.errorhandler(404)
    def pagina_niet_gevonden(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def te_veel_aanvragen(_error):
        return render_template("errors/429.html"), 429

    return app
