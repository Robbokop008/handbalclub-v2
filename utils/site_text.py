"""
utils/site_text.py
-------------------
Kleine, admin-bewerkbare tekstfragmenten (hero-titels/introzinnen) die
verspreid over de site in templates gebruikt worden - zie models.SiteText.

De teksten zijn gegroepeerd per pagina (SITE_TEXT_PAGINAS) zodat de admin-
omgeving per pagina kan bewerken i.p.v. één lange lijst met alle velden
door elkaar - zie routes/admin.py (site_teksten / edit_site_tekst).

Elke sleutel heeft een standaardwaarde. Zolang een admin niets aangepast
heeft, of als een veld leeggelaten wordt bij het opslaan, valt de site
terug op die standaardtekst - zo kan een lege admin-invoer nooit een
kapotte/lege hero-sectie opleveren.
"""

from extensions import db
from models import SiteText

# Elke pagina: een slug (gebruikt in de admin-URL), een leesbaar label, het
# endpoint om "Bekijk pagina" naartoe te linken (None als de pagina niet
# rechtstreeks te bezoeken is, bv. een bedankt-/bevestigingspagina), een
# optionele opmerking daarover, en de tekstvelden (sleutel, omschrijving,
# standaardwaarde) die op die pagina gebruikt worden.
#
# "home" en "kalender" stonden hier vroeger ook in, maar zijn tijdens de
# restyling vervangen door volledig hardcoded pagina's (foto-hero +
# zwevende kaarten, resp. de accordion-pagina) zonder site_teksten-hero -
# bewust verwijderd i.p.v. dode velden te laten staan die een admin wel
# kan invullen maar die nergens meer getoond worden (zie
# scripts/migrate_site_text_cleanup.py voor de eenmalige opkuis).
SITE_TEXT_PAGINAS = [
    {
        "slug": "contact",
        "label": "Contact",
        "endpoint": "main.contact",
        "velden": [
            ("contact_hero_titel", "Hero-titel", "Contacteer ons"),
            ("contact_hero_intro", "Hero-intro", "Heb je vragen of hulp nodig? Stuur ons een bericht en we nemen binnenkort contact met je op."),
        ],
    },
    {
        "slug": "inschrijving",
        "label": "Inschrijving nieuwe speler",
        "endpoint": "jeugd.inschrijving",
        "velden": [
            ("inschrijving_hero_titel", "Hero-titel", "Inschrijving nieuwe speler"),
            ("inschrijving_hero_intro", "Hero-intro", "Vul onderstaand formulier in om je (of je kind) in te schrijven. We nemen zo snel mogelijk contact met je op."),
        ],
    },
    {
        "slug": "inschrijving-bedankt",
        "label": "Inschrijving nieuwe speler — bedanktpagina",
        "endpoint": None,
        "opmerking": "Deze pagina is enkel zichtbaar na een echte inschrijving, en kan dus niet rechtstreeks bezocht worden.",
        "velden": [
            ("inschrijving_bedankt_titel", "Titel", "Bedankt voor je inschrijving!"),
        ],
    },
    {
        "slug": "login",
        "label": "Inloggen",
        "endpoint": "auth.login",
        "velden": [
            ("login_hero_titel", "Hero-titel", "Veilig inloggen op uw account"),
            ("login_hero_subtitel", "Hero-subtekst", "Log in om verder te gaan."),
        ],
    },
    {
        "slug": "register",
        "label": "Registreren",
        "endpoint": "auth.register",
        "velden": [
            ("register_hero_titel", "Hero-titel", "Start je avontuur met Handbal Sint-Truiden"),
            ("register_hero_subtitel", "Hero-subtekst", "Registreer nu om onze webshop te ontdekken en bestellingen te plaatsen."),
        ],
    },
    {
        "slug": "profiel",
        "label": "Profiel",
        "endpoint": "auth.profile",
        "velden": [
            ("profiel_hero_titel", "Hero-titel", "Jouw profiel, verfijnd"),
            ("profiel_hero_subtitel", "Hero-subtekst", "Beheer je account, bekijk recente aankopen en houd je lidmaatschapsgegevens up-to-date in één elegant controlecentrum."),
        ],
    },
    {
        "slug": "account-instellingen",
        "label": "Accountinstellingen",
        "endpoint": "auth.account_settings",
        "velden": [
            ("account_instellingen_hero_titel", "Hero-titel", "Accountinstellingen"),
            ("account_instellingen_hero_subtitel", "Hero-subtekst", "Update uw accountgegevens hier."),
        ],
    },
    {
        "slug": "webshop-producten",
        "label": "Webshop — productoverzicht",
        "endpoint": "shop.products",
        "velden": [
            ("shop_hero_titel", "Hero-titel", "Ontdek onze collectie"),
        ],
    },
    {
        "slug": "webshop-winkelmandje",
        "label": "Webshop — winkelmandje",
        "endpoint": "shop.cart",
        "velden": [
            ("cart_hero_titel", "Hero-titel (winkelmandje gevuld)", "Je winkelmandje"),
            ("cart_hero_subtitel", "Hero-subtekst (winkelmandje gevuld)", "Beoordeel je geselecteerde items, pas aantallen aan en ga naar de checkout wanneer je klaar bent."),
            ("cart_leeg_hero_titel", "Hero-titel (winkelmandje leeg)", "Je winkelmandje is leeg"),
            ("cart_leeg_hero_subtitel", "Hero-subtekst (winkelmandje leeg)", "Bekijk onze producten en voeg items toe aan je winkelmandje."),
        ],
    },
    {
        "slug": "webshop-checkout-success",
        "label": "Webshop — bestelling geplaatst",
        "endpoint": None,
        "opmerking": "Deze pagina is enkel zichtbaar na een echte bestelling, en kan dus niet rechtstreeks bezocht worden.",
        "velden": [
            ("checkout_success_hero_titel", "Hero-titel", "Bedankt!"),
            ("checkout_success_hero_subtitel", "Hero-subtekst", "Uw bestelling is succesvol geplaatst. Een bevestigingsmail is naar u verzonden met de bestelgegevens. Wij zullen uw artikelen zo spoedig mogelijk verwerken en verzenden."),
        ],
    },
    {
        "slug": "footer",
        "label": "Footer",
        "endpoint": "main.home",
        "opmerking": "Verschijnt onderaan elke pagina van de site.",
        "velden": [
            ("footer_over_ons_tekst", "Tekst onder 'Over ons'", "Leer meer over onze club en onze waarden"),
        ],
    },
]


def vind_pagina(slug):
    """Geeft het paginadict met dit slug terug, of None als het niet bestaat."""
    for pagina in SITE_TEXT_PAGINAS:
        if pagina["slug"] == slug:
            return pagina
    return None


def _alle_velden():
    for pagina in SITE_TEXT_PAGINAS:
        for sleutel, omschrijving, standaard_waarde in pagina["velden"]:
            yield sleutel, omschrijving, standaard_waarde


DEFAULT_VALUES = {sleutel: waarde for sleutel, _omschrijving, waarde in _alle_velden()}


def get_site_teksten():
    """Geeft een dict {sleutel: waarde} terug voor gebruik in templates, met fallback op de standaardwaarde."""
    rijen = {r.sleutel: r.waarde for r in SiteText.query.all()}
    ontbrekend = [(s, o, w) for s, o, w in _alle_velden() if s not in rijen]
    if ontbrekend:
        for sleutel, omschrijving, waarde in ontbrekend:
            db.session.add(SiteText(sleutel=sleutel, omschrijving=omschrijving, waarde=waarde))
            rijen[sleutel] = waarde
        db.session.commit()
    return {**DEFAULT_VALUES, **rijen}
