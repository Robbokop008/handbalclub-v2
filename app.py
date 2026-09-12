"""
app.py
------
Dit is het hart van de applicatie. Hier wordt de Flask-app aangemaakt via
een "application factory" (de functie create_app). Dat patroon zorgt ervoor
dat je later makkelijk kan testen, meerdere configuraties kan gebruiken,
en de app in kleinere, overzichtelijke stukken (blueprints) kan opdelen.

Starten voor development doe je via run.py, niet via dit bestand direct.
"""

from flask import Flask, render_template, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config_by_name, ONVEILIGE_STANDAARD_SECRET_KEY
from extensions import db, csrf, limiter


def create_app(config_name="development"):
    """Bouwt en configureert een Flask-app en geeft die terug."""

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Op productie (Hetzner) draait gunicorn achter één reverse proxy (nginx).
    # Zonder ProxyFix ziet Flask elk request als afkomstig van nginx zelf
    # (127.0.0.1) i.p.v. het echte client-IP - dat breekt Flask-Limiter
    # (@limiter.limit op login/contact/etc. zou dan alle bezoekers samen
    # limiteren) en request.is_secure (nginx praat intern http met gunicorn).
    # x_for/x_proto/x_host=1: vertrouw exact één hop aan X-Forwarded-*
    # headers, precies zoveel als de nginx-laag ervoor toevoegt.
    if config_name == "production":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Geen stille onveilige standaardwaarde in productie: als SECRET_KEY niet
    # via de omgevingsvariabelen ingesteld is, valt Config terug op een
    # sleutel die letterlijk in de broncode staat (handig om lokaal snel te
    # kunnen opstarten, maar onveilig als dat ook in productie zou gebeuren -
    # daarmee zijn sessies/cookies voor iedereen met leestoegang tot de repo
    # te vervalsen). Faal hier duidelijk i.p.v. stil onveilig te draaien.
    if config_name == "production" and app.config["SECRET_KEY"] == ONVEILIGE_STANDAARD_SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY staat nog op de onveilige standaardwaarde. Stel een "
            "echte, geheime sleutel in via de omgevingsvariabelen (.env) "
            "voor je de site in productie draait."
        )

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

    # Stelt de sponsors beschikbaar in elke template: de eerste 2 actieve
    # sponsors als "hoofdsponsor"-logo's naast het hamburgermenu in de
    # header, en alle actieve sponsors in de sponsorenlijst in de footer
    # (anders zijn sponsors vanaf de 3e nergens op de site zichtbaar).
    from models import Sponsor

    @app.context_processor
    def inject_sponsors():
        alle_sponsors = Sponsor.query.filter_by(is_active=True).order_by(Sponsor.position).all()
        return {
            "header_sponsors": alle_sponsors[:2],
            "footer_sponsors": alle_sponsors,
        }

    # Footer-copyrightjaar: automatisch het huidige jaar, niet iets wat een
    # admin kan laten "vergeten bijwerken" - zie templates/base.html.
    from datetime import datetime as _datetime

    @app.context_processor
    def inject_huidig_jaar():
        return {"huidig_jaar": _datetime.utcnow().year}

    # Stelt het Google Analytics Measurement ID beschikbaar in elke template
    # (base.html laadt het gtag-script + cookiebanner enkel als dit gezet
    # is - zie config.py). Via app.config i.p.v. een aparte SiteText-sleutel:
    # dit is een technisch ID, geen door een admin te bewerken tekst.
    @app.context_processor
    def inject_ga_measurement_id():
        return {"ga_measurement_id": app.config.get("GA_MEASUREMENT_ID")}

    # Welke body-class (navy achtergrond + restyled kaarten/hero, zie
    # static/style.css) een pagina krijgt, per route-endpoint. Dit was een
    # groeiende if/elif-keten in templates/base.html - bij elke nieuwe
    # restyled pagina werd dat onoverzichtelijker, vandaar een gewone
    # Python-lookup i.p.v. nog een {% elif %} toe te voegen.
    PAGINA_STIJL_PER_ENDPOINT = {
        "main.home": "home-page",
        "club.overzicht": "club-page",
        "kalender.overzicht": "kalender-page",
        "dames.overzicht": "dames-page",
        "heren.overzicht": "heren-page",
        "jeugd.overzicht": "jeugd-page",
        "ghandbal.index": "ghandbal-page",
        "fithandbal.index": "fithandbal-page",
        "main.contact": "content-page",
        "main.vergeet_mij": "content-page",
        "main.nieuws": "content-page",
        "main.nieuws_detail": "content-page",
        "pages.view": "content-page",
        "shop.products": "content-page",
        "shop.product_detail": "content-page",
        "shop.cart": "content-page",
        "shop.checkout_success": "content-page",
        "auth.login": "auth-page",
        "auth.register": "auth-page",
        "auth.profile": "auth-page",
        "auth.account_settings": "auth-page",
    }

    @app.context_processor
    def inject_body_page_class():
        return {"body_page_class": PAGINA_STIJL_PER_ENDPOINT.get(request.endpoint)}

    # Jinja-filter die gesaniteerde rich-text HTML (nieuwsberichten) omzet
    # naar leesbare platte tekst voor previews - zie utils/sanitize.py.
    from utils.sanitize import html_naar_platte_tekst

    app.add_template_filter(html_naar_platte_tekst, name="platte_tekst")

    # Jinja-global om de canonieke video-embed-URL server-side op te bouwen
    # in templates/pages/_blocks/video.html - zie utils/url_validation.py.
    from utils.url_validation import build_video_embed_url

    app.add_template_global(build_video_embed_url, name="video_embed_url")

    # Jinja-global om de stijlvelden (uitlijning/achtergrond/breedte/witruimte)
    # van een pagina-blok met defaults aan te vullen - zie utils/page_blocks.py.
    from utils.page_blocks import resolve_style

    app.add_template_global(resolve_style, name="resolve_style")

    # Eigen foutpagina's i.p.v. Flask/Werkzeug's kale standaardpagina's:
    # 404 (onbestaande URL) en 429 (rate limit overschreden, bv. te vaak
    # inloggen na elkaar - zie @limiter.limit(...) in routes/auth.py).
    @app.errorhandler(404)
    def pagina_niet_gevonden(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def te_veel_aanvragen(_error):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def interne_fout(_error):
        # errors/500.html extend base.html, en base.html haalt via de
        # context processors hierboven (nav, site_teksten, sponsors) dingen
        # uit de database op. Als de 500 zelf door een databaseprobleem
        # kwam, zou die render dus ook mislukken - vandaar deze fallback
        # naar kale HTML in plaats van een tweede crash.
        try:
            return render_template("errors/500.html"), 500
        except Exception:
            return (
                "<h1>Er ging iets mis</h1>"
                "<p>Er is een onverwachte fout opgetreden. Probeer het later opnieuw.</p>"
                '<p><a href="/">Terug naar de homepage</a></p>'
            ), 500

    # Onderhoudsmodus: als een admin dit via /admin aanzet, krijgen gewone
    # bezoekers overal onderhoud.html te zien i.p.v. de opgevraagde pagina -
    # zie utils/site_settings.py. Uitgezonderd: het admin-paneel zelf
    # (anders kan niemand de modus nog uitzetten), /login en /logout (zodat
    # een admin nog kan in-/uitloggen), de Stripe-webhook (machine-naar-
    # machine, geen bezoeker die de melding moet zien - anders stapelen
    # mislukte afleverpogingen zich op bij Stripe), statische bestanden
    # (nodig om onderhoud.html zelf correct te tonen), en een ingelogde
    # admin (die moet de site kunnen blijven bekijken, bv. om iets na te
    # kijken tijdens een grote update - zie check hieronder).
    ONDERHOUDSMODUS_TOEGESTANE_ENDPOINTS = {
        "static", "auth.login", "auth.logout", "shop.stripe_webhook",
    }

    @app.before_request
    def check_onderhoudsmodus():
        if request.blueprint == "admin" or request.endpoint in ONDERHOUDSMODUS_TOEGESTANE_ENDPOINTS:
            return None

        from utils.site_settings import is_onderhoudsmodus_actief
        if not is_onderhoudsmodus_actief():
            return None

        user_id = session.get("user_id")
        if user_id is not None:
            from models import User
            user = User.query.get(user_id)
            if user is not None and user.is_admin:
                return None

        # Retry-After: vertelt browsers/zoekmachines dat dit tijdelijk is
        # (kom over een uur terug) i.p.v. de pagina als permanent verdwenen
        # te behandelen.
        #
        # body_page_class expliciet op None: de context-processor hierboven
        # (inject_body_page_class) leidt die anders af uit de oorspronkelijk
        # opgevraagde pagina (bv. "home-page"/"club-page" -> navy
        # achtergrond, zie static/style.css). onderhoud.html's tekst gebruikt
        # de kleuren voor de standaard lichte achtergrond, dus zonder deze
        # override kan de tekst - afhankelijk van welke URL bezocht werd -
        # onleesbaar donker-op-donker uitvallen.
        return render_template("onderhoud.html", body_page_class=None), 503, {"Retry-After": "3600"}

    # Baseline HTTP-securityheaders op elke response. Geen volledige Content-
    # Security-Policy hier: de site gebruikt op verschillende plekken inline
    # <style>/<script>, en een CSP zonder zorgvuldige nonce-aanpak zou die
    # stukken zomaar kunnen blokkeren - dat is bewust buiten deze scope
    # gehouden. De frame-ancestors-directive hieronder is een uitzondering:
    # die regelt enkel wie mag framen en raakt scripts/styles niet.
    TOEGESTANE_FRAME_ANCESTOR = "https://handbalsint-truiden.be"

    @app.after_request
    def voeg_security_headers_toe(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        # De admin-preview van een pagina moet in een eigen <iframe> in het
        # bewerkscherm kunnen tonen (zie admin.preview_page) - enkel daar
        # SAMEORIGIN i.p.v. framen van buitenaf.
        if request.endpoint == "admin.preview_page":
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            # X-Frame-Options kent geen "sta enkel dit domein toe" (de
            # ALLOW-FROM-waarde is verouderd en wordt niet meer ondersteund
            # door moderne browsers), dus gebruiken we hiervoor de CSP
            # frame-ancestors-directive. X-Frame-Options laten we hier weg
            # zodat browsers niet toch terugvallen op de strengere DENY.
            response.headers["Content-Security-Policy"] = (
                f"frame-ancestors 'self' {TOEGESTANE_FRAME_ANCESTOR}"
            )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # HSTS: dwingt de browser om deze site voortaan altijd via https te
        # benaderen, ook als iemand per ongeluk http:// intypt. Enkel in
        # productie - anders zou een browser die lokaal ooit via https
        # test (bv. via een tunnel) dit voor het dev-domein blijven
        # onthouden en lokaal http-gebruik blokkeren.
        if not app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app
