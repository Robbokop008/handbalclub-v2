"""
utils/oude_site_redirects.py
------------------------------
Permanente redirects van de URL's van de vorige (Joomla-)website naar hun
tegenhanger op deze site. De oude site stond ~15 jaar online onder
hetzelfde domein: Google had die URL's geïndexeerd (bv. /kalender/
wedstrijden.html, /senioren/dames-1.html, /10-nieuws/dames/612-....html) en
externe sites (Wikipedia, pers, federatie, Facebook) linken er nog naar.
Zonder redirect gaven die allemaal een 404, waardoor de site bij de
overstap haar volledige zoekmachineranking kwijtspeelde - met een 301 geeft
Google die opgebouwde waarde door aan de nieuwe URL.

De lijst is opgebouwd uit het Wayback Machine-archief van het domein.
Oude pagina's zonder zinvolle tegenhanger (fotoalbums, oude RSForm-
formulieren, feeds, ...) staan hier bewust niet in: een 404 is voor Google
duidelijker dan een redirect naar een niet-verwante pagina (die telt toch
als "soft 404"). Idem voor de spam-URL's die op de gehackte oude site
stonden (bv. /f/special/..., /odr/order/...) - die moeten net verdwijnen.

Gebruikt door de 404-handler in app.py, dus enkel voor paden waar geen
enkele route van deze site op matcht.
"""

import re

from flask import url_for

# Oud pad (kleine letters, zonder query-string) -> (endpoint, url_for-kwargs).
OUDE_PADEN = {
    "/index.php": ("main.home", {}),

    # Club
    "/club/contact.html": ("main.contact", {}),
    "/club/aanspreekpunt-persoonlijke-integriteit.html": ("club.overzicht", {}),
    "/club/bestuur.html": ("club.overzicht", {}),
    "/club/e-mails-bestuur-coördinatoren.html": ("club.overzicht", {}),
    "/club/e-mails-jeugd.html": ("club.overzicht", {}),
    "/club/historiek.html": ("club.overzicht", {}),
    "/club/missie-en-visie.html": ("club.overzicht", {}),
    "/club/verzekeringsformulier.html": ("club.overzicht", {}),
    "/vacatures.html": ("pages.view", {"slug": "vacatures"}),

    # Dames / Heren
    "/senioren/dames-1.html": ("dames.overzicht", {}),
    "/senioren/dames-beloften.html": ("dames.overzicht", {}),
    "/senioren/dames-1-beloften-team-seizoen-2019-2020.html": ("dames.overzicht", {}),
    "/senioren/heren-1.html": ("heren.overzicht", {}),
    "/senioren/heren-2.html": ("heren.overzicht", {}),
    "/heren/heren-1.html": ("heren.overzicht", {}),
    "/heren/heren-2.html": ("heren.overzicht", {}),

    # Jeugd
    "/heren/j18.html": ("jeugd.overzicht", {}),
    "/jeugd/3-5-jaar-multi-move-bewegingsschool.html": ("jeugd.overzicht", {}),
    "/jeugd/j16.html": ("jeugd.overzicht", {}),
    "/jeugd/j18.html": ("jeugd.overzicht", {}),
    "/jeugd/jm10-08.html": ("jeugd.overzicht", {}),
    "/jeugd/jm12-10-08.html": ("jeugd.overzicht", {}),
    "/jeugd/jm12-hbst-rsg.html": ("jeugd.overzicht", {}),
    "/jeugd/jm12.html": ("jeugd.overzicht", {}),
    "/jeugd/jm14-2.html": ("jeugd.overzicht", {}),
    "/jeugd/jm14.html": ("jeugd.overzicht", {}),
    "/jeugd/m16.html": ("jeugd.overzicht", {}),
    "/jeugd/jeugdbeleidsplan.html": ("pages.view", {"slug": "jeugd-jeugdbeleidsplan"}),
    "/jeugd/inschrijving-nieuwe-speler.html": ("jeugd.inschrijving", {}),
    "/ik-wil-handballen.html": ("jeugd.inschrijving", {}),
    "/inschrijven.html": ("jeugd.inschrijving", {}),

    # G-Handbal / FIT-Handbal
    "/g-handbal.html": ("ghandbal.index", {}),
    "/g-handbal/g-hb2.html": ("ghandbal.index", {}),
    "/g-handbal/jm14-2.html": ("ghandbal.index", {}),
    "/g-handbal/inschrijving-g-handbal.html": ("jeugd.inschrijving", {"categorie": "G-Handbal"}),
    "/fithandbal.html": ("fithandbal.index", {}),

    # Fanzone
    "/fanzone/fanshopbestelformulier.html": ("shop.products", {}),
    "/fanzone/vergeet-mij-formulier-gdpr.html": ("main.vergeet_mij", {}),
    "/events.html": ("kalender.overzicht", {}),
}

# Patronen voor hele groepen oude URL's, in volgorde van controle.
OUDE_PATRONEN = [
    # Kalenderpagina's (/kalender/wedstrijden.html, /kalender/trainingen.html,
    # /kalender/sporthallen.html, inschrijvingen voor eetfestijnen, ...) en de
    # losse evenementpagina's (/events/evenement/19-bbq.html, ...).
    (re.compile(r"^/kalender/[^/]+\.html$"), ("kalender.overzicht", {})),
    (re.compile(r"^/events/.+\.html$"), ("kalender.overzicht", {})),
    # Nieuwsoverzichten (/nieuws/dames.html, /nieuws/archief.html, ...) en
    # losse artikels. Joomla zette die onder /nieuws/<categorie>/ of onder
    # /<categorie-id>-<alias>/ (bv. /10-nieuws/dames/612-....html,
    # /8-nieuws/438-....html, /22-heren-1/543-....html). De artikels zelf zijn
    # niet overgezet naar deze site, dus het nieuwsoverzicht is de beste
    # tegenhanger.
    (re.compile(r"^/nieuws/[^/]+\.html$"), ("main.nieuws", {})),
    (re.compile(r"^/nieuws/[^/]+/.+\.html$"), ("main.nieuws", {})),
    (re.compile(r"^/\d+-[^/]+/(?:[^/]+/)*\d+-[^/]+$"), ("main.nieuws", {})),
]


def oude_site_doel_url(pad):
    """Geeft de URL terug waar een oud pad van de vorige website naartoe
    moet, of None als er geen tegenhanger is."""
    pad = pad.lower()
    doel = OUDE_PADEN.get(pad)
    if doel is None:
        doel = next((d for patroon, d in OUDE_PATRONEN if patroon.match(pad)), None)
    if doel is None:
        return None
    endpoint, kwargs = doel
    return url_for(endpoint, **kwargs)
